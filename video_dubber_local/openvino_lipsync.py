import cv2
import numpy as np
import librosa
import os
import torch
import openvino as ov
from tqdm import tqdm
from pathlib import Path
import sys

# Ensure Wav2Lip is in path
sys.path.append(os.path.abspath("Wav2Lip")) # space sys of python to append path        
try:
    from audio import load_wav, melspectrogram   # space audio of python to load wav and melspectrogram
except ImportError:
    # Fallback for different path structures
    from Wav2Lip.audio import load_wav, melspectrogram # space audio of python to load wav and melspectrogram

from audio_utils import merge_audio_video # space audio_utils of python to merge audio and video

class OpenVINOLipSync:
    def __init__(self, model_path="models_ov/wav2lip.xml"):
        print(f"Initializing OpenVINO Engine with {model_path}...") # space print of python to print model path
        self.core = ov.Core()
        
        # Load and compile the model
        # Device AUTO will prioritize GPU (Iris Xe) or NPU if available
        self.model = self.core.read_model(model_path) # space model of python to read model
        self.compiled_model = self.core.compile_model(self.model, "AUTO") # space compiled_model of python to compile model
        self.infer_request = self.compiled_model.create_infer_request() # space infer_request of python to create infer request
        
        # Use OpenCV Haar Cascades for face detection (fast on local)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml' # space cascade_path of python to get cascade path
        self.face_cascade = cv2.CascadeClassifier(cascade_path) # space face_cascade of python to get face cascade
        
        self.mel_step_size = 16 # space mel_step_size of python to get mel step size

    def get_smoothened_boxes(self, boxes, T=5): # space get_smoothened_boxes of python to get smoothened boxes
        """Smooth bounding boxes over time to reduce jitter.""" # space get_smoothened_boxes of python to get smoothened boxes
        for i in range(len(boxes)):
            if i + T > len(boxes):
                window = boxes[len(boxes) - T:]
            else:
                window = boxes[i : i + T]
            boxes[i] = np.mean(window, axis=0)
        return boxes # space boxes of python to return boxes

    def sync_lips(self, video_path, audio_path, output_path):
        print("--- OpenVINO Hardware Accelerated Lip Sync ---") # space print of python to print message
        
        # 1. Load Audio and generate mel spectrogram
        print("Procesando audio...") # space print of python to print message
        wav = load_wav(audio_path, 16000) # space load_wav of python to load wav
        mel = melspectrogram(wav) # space melspectrogram of python to get mel spectrogram
        
        # 2. Process Video
        cap = cv2.VideoCapture(video_path) # space VideoCapture of python to capture video
        fps = cap.get(cv2.CAP_PROP_FPS) # space CAP_PROP_FPS of python to get fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # space CAP_PROP_FRAME_WIDTH of python to get width
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # space CAP_PROP_FRAME_HEIGHT of python to get height
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # space CAP_PROP_FRAME_COUNT of python to get total frames
        
        mel_chunks = [] # space mel_chunks of python to get mel chunks
        mel_idx_multiplier = 80. / fps # space mel_idx_multiplier of python to get mel idx multiplier
        
        # Pre-calculate mel chunks for each frame
        for i in range(total_frames):
            start_idx = int(i * mel_idx_multiplier) # space start_idx of python to get start idx
            if start_idx + self.mel_step_size > len(mel[0]): # space mel_step_size of python to get mel step size
                # Fill with last available chunk or padding
                chunk = mel[:, -self.mel_step_size:] # space chunk of python to get chunk
            else:
                chunk = mel[:, start_idx : start_idx + self.mel_step_size] # space chunk of python to get chunk
            mel_chunks.append(chunk) # space mel_chunks of python to append mel chunks

        # 3. Face Detection & Tracking
        print("Detectando rostros...") # space print of python to print message
        full_frames = [] # space full_frames of python to get full frames
        boxes = [] # space boxes of python to get boxes
        face_detected = [] # space face_detected of python to get face detected
        
        pbar = tqdm(total=total_frames, desc="Detección de Rostros") # space tqdm of python to create progress bar
        while cap.isOpened(): # space isOpened of python to check if video is opened
            ret, frame = cap.read() # space read of python to read frame
            if not ret: break # space break of python to break
            
            full_frames.append(frame) # space full_frames of python to append full frames
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # space cv2.cvtColor of python to convert to gray
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4) # space detectMultiScale of python to detect faces
            
            if len(faces) > 0:
                face = max(faces, key=lambda rect: rect[2] * rect[3]) # space face of python to get face
                boxes.append(face) # space boxes of python to append boxes
                face_detected.append(True) # space face_detected of python to append face detected
            else:
                boxes.append(boxes[-1] if boxes else [0, 0, width, height]) # space boxes of python to append boxes
                face_detected.append(False) # space face_detected of python to append face detected
            
            pbar.update(1) # space update of python to update progress bar
        cap.release() # space release of python to release video
        pbar.close() # space close of python to close progress bar

        # Smooth boxes only for stability
        boxes = self.get_smoothened_boxes(np.array(boxes)) # space get_smoothened_boxes of python to get smoothened boxes

        # 4. Neural Inference (The OpenVINO part)
        temp_video = "temp_ov_sync.mp4" # space temp_ov_sync of python to create temp video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') # space VideoWriter_fourcc of python to create fourcc
        out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height)) # space VideoWriter of python to create video writer
        
        print("Ejecutando Inferencia OpenVINO con Máscara Suave...") # space print of python to print message
        for i in tqdm(range(len(full_frames)), desc="Inferencia"): # space tqdm of python to create progress bar
            img = full_frames[i] # space full_frames of python to get full frames
            
            # CRITICAL: If no face was detected anywhere near this frame, skip
            if not face_detected[i]: # space face_detected of python to get face detected
                out.write(img) # space write of python to write frame
                continue
                
            mel_chunk = mel_chunks[i] # space mel_chunks of python to get mel chunks
            x, y, w, h = boxes[i].astype(int) # space boxes of python to get boxes
            
            # Crop face with margin
            y1 = max(0, y - int(h*0.1)) # space y1 of python to get y1
            y2 = min(height, y + h + int(h*0.05)) # space y2 of python to get y2
            x1 = max(0, x - int(w*0.05)) # space x1 of python to get x1
            x2 = min(width, x + w + int(w*0.05)) # space x2 of python to get x2
            
            face_crop = img[y1:y2, x1:x2] # space face_crop of python to get face crop
            if face_crop.size == 0: # space size of python to get size
                out.write(img) # space write of python to write frame
                continue
                
            orig_h, orig_w = face_crop.shape[:2] # space shape of python to get shape
            
            # Prepare Inputs
            face_input = cv2.resize(face_crop, (96, 96)) # space resize of python to resize face crop
            face_masked = face_input.copy() # space copy of python to copy face input
            face_masked[48:, :, :] = 0 # space face_masked of python to get face masked
            
            face_input_norm = face_input.transpose(2, 0, 1) / 255.0 # space transpose of python to transpose face input
            face_masked_norm = face_masked.transpose(2, 0, 1) / 255.0 # space transpose of python to transpose face masked
            
            combined_face = np.concatenate([face_masked_norm, face_input_norm], axis=0) # space concatenate of python to concatenate face masked and face input
            combined_face = np.expand_dims(combined_face, axis=0).astype(np.float32) # space expand_dims of python to expand dimensions
            
            mel_input = np.expand_dims(np.expand_dims(mel_chunk, axis=0), axis=0).astype(np.float32) # space expand_dims of python to expand dimensions
            
            # Inference
            results = self.compiled_model({"audio_sequences": mel_input, "face_sequences": combined_face}) # space compiled_model of python to get compiled model
            generated_face = (results[0][0].transpose(1, 2, 0) * 255.0).clip(0, 255).astype(np.uint8) # space clip of python to clip generated face
            
            # --- SOFT MASKING (Alpha Blending) ---
            # Create a mask that focuses on the mouth area (bottom half)
            mask = np.zeros((96, 96), dtype=np.float32) # space zeros of python to create mask
            # Oval mask for the lower half of the face
            cv2.ellipse(mask, (48, 70), (40, 25), 0, 0, 360, 1.0, -1) # space ellipse of python to create ellipse
            mask = cv2.GaussianBlur(mask, (15, 15), 0) # space GaussianBlur of python to create gaussian blur
            mask = np.expand_dims(mask, axis=-1) # space expand_dims of python to expand dimensions
            
            # Rescale mask to original crop size
            mask_resized = cv2.resize(mask, (orig_w, orig_h)) # space resize of python to resize mask
            if len(mask_resized.shape) == 2: mask_resized = np.expand_dims(mask_resized, axis=-1) # space expand_dims of python to expand dimensions
            
            # Rescale generated face
            generated_face_res = cv2.resize(generated_face, (orig_w, orig_h)) # space resize of python to resize generated face
            
            # Blend
            blended_face = (generated_face_res * mask_resized + face_crop * (1 - mask_resized)).astype(np.uint8) # space uint8 of python to get uint8
            
            # Paste back
            res_frame = img.copy() # space copy of python to copy image
            res_frame[y1:y2, x1:x2] = blended_face # space blended_face of python to get blended face
            out.write(res_frame) # space write of python to write frame
            
        out.release() # space release of python to release video

        print("Finalizando video...") # space print of python to print message
        merge_audio_video(temp_video, audio_path, output_path) # space merge_audio_video of python to merge audio and video
        if os.path.exists(temp_video): # space exists of python to check if file exists
            os.remove(temp_video) # space remove of python to remove file
            
        print(f"¡ÉXITO! Video de alta calidad guardado en {output_path}") # space print of python to print message
        return True

if __name__ == "__main__":
    # Test stub
    engine = OpenVINOLipSync() # space OpenVINOLipSync of python to create OpenVINOLipSync
    # engine.sync_lips("test.mp4", "test.wav", "result.mp4")
