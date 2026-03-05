import cv2
import numpy as np
import librosa
import os
from tqdm import tqdm
from audio_utils import merge_audio_video

class MediaPipeLipSync:
    def __init__(self):
        # We fall back to OpenCV Haar Cascades since MediaPipe lacks Python 3.13 binaries.
        # This classic approach is purely mathematical, fast, and educational.
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.last_face = None

    def extract_audio_energy(self, audio_path, fps, video_duration):
        y, sr = librosa.load(audio_path, sr=None)
        rms = librosa.feature.rms(y=y)[0]
        # Normalize
        peak = np.max(rms)
        if peak > 0:
            rms = rms / peak
        
        # Smooth
        window_len = int(sr * 0.1 / 512) + 1 # ~100ms window
        kernel = np.ones(window_len) / window_len
        rms = np.convolve(rms, kernel, mode='same')
        
        # Interpolate to video fps
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
        video_times = np.arange(0, video_duration, 1.0 / fps)
        
        rms_interp = np.interp(video_times, times, rms)
        return rms_interp

    def sync_lips(self, video_path, audio_path, output_path):
        print("Analizando audio original para movimiento (RMS)...")
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps == 0:
            fps = 30.0
            
        duration = total_frames / fps

        rms = self.extract_audio_energy(audio_path, fps, float(duration))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_video = "temp_fastsync.mp4"
        out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

        map_x, map_y = np.meshgrid(np.arange(width), np.arange(height))
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)

        frame_idx = 0
        pbar = tqdm(total=total_frames, desc="Animando rostro (Visión Clásica)")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            vol = rms[frame_idx] if frame_idx < len(rms) else 0.0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostro
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Estabilización temporal del cuadro de la cara
            if len(faces) > 0:
                # Tomar la cara más grande
                face = max(faces, key=lambda rect: rect[2] * rect[3])
                if self.last_face is not None:
                    # Suavizar el cuadro (IIR filter)
                    x, y, w, h = face
                    lx, ly, lw, lh = self.last_face
                    self.last_face = (int(0.8*lx + 0.2*x), int(0.8*ly + 0.2*y), 
                                      int(0.8*lw + 0.2*w), int(0.8*lh + 0.2*h))
                else:
                    self.last_face = face
            
            warped_frame = frame.copy()
            
            if self.last_face is not None:
                x, y, w, h = self.last_face
                
                # Definir aproximadamente la mandíbula inferior (35% inferior de la cara)
                # y restringir los lados al 60% central
                jaw_y = y + int(h * 0.65)
                jaw_h = y + h - jaw_y
                jaw_x = x + int(w * 0.2)
                jaw_w = int(w * 0.6)
                
                max_disp = h * 0.12 # Desplazamiento máximo: 12% del alto de la cara
                displacement = max_disp * vol
                
                if displacement > 1.0:
                    mask = np.zeros((height, width), dtype=np.float32)
                    
                    # Crear el polígono de la mandíbula
                    poly_pts = np.array([
                        [jaw_x, jaw_y],
                        [jaw_x + jaw_w, jaw_y],
                        [jaw_x + jaw_w - int(jaw_w*0.2), jaw_y + jaw_h],
                        [jaw_x + int(jaw_w*0.2), jaw_y + jaw_h]
                    ], np.int32)
                    
                    cv2.fillPoly(mask, [poly_pts], 1.0)
                    
                    # Suavizado pesado para deformar los tejidos elásticamente
                    blur_size = int(h * 0.2)
                    if blur_size % 2 == 0: blur_size += 1
                    if blur_size < 3: blur_size = 3
                        
                    mask = cv2.GaussianBlur(mask, (blur_size, blur_size), 0)
                    
                    my = (map_y - (mask * displacement)).astype(np.float32)
                    warped_frame = cv2.remap(frame, map_x, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            
            out.write(warped_frame)
            frame_idx += 1
            pbar.update(1)
            
        cap.release()
        out.release()
        pbar.close()

        print("Fusionando audio y video acelerado...")
        merge_audio_video(temp_video, audio_path, output_path)
        
        if os.path.exists(temp_video):
            os.remove(temp_video)
            
        return True
