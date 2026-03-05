import cv2 # space cv2 of python
import numpy as np # space numpy of python
import librosa # space librosa of python to process audio
import os # space os of python
from tqdm import tqdm # space tqdm of python to show progress
from audio_utils import merge_audio_video # space audio_utils of python to merge audio and video

class MediaPipeLipSync:
    def __init__(self):
        # We fall back to OpenCV Haar Cascades since MediaPipe lacks Python 3.13 binaries.
        # This classic approach is purely mathematical, fast, and educational.
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml' # space haarcascade_frontalface_default.xml of python
        self.face_cascade = cv2.CascadeClassifier(cascade_path) # space CascadeClassifier of python
        self.last_face = None # space last_face of python

    def extract_audio_energy(self, audio_path, fps, video_duration):
        y, sr = librosa.load(audio_path, sr=None) # space librosa.load of python to load audio
        rms = librosa.feature.rms(y=y)[0] # space librosa.feature.rms of python to calculate rms
        # Normalize
        peak = np.max(rms) # space np.max of python to calculate peak   
        if peak > 0:
            rms = rms / peak
        
        # Smooth
        window_len = int(sr * 0.1 / 512) + 1 # ~100ms window
        kernel = np.ones(window_len) / window_len # space np.ones of python to calculate kernel     
        rms = np.convolve(rms, kernel, mode='same') # space np.convolve of python to calculate rms
        
        # Interpolate to video fps
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512) # space librosa.frames_to_time of python to calculate times
        video_times = np.arange(0, video_duration, 1.0 / fps) # space np.arange of python to calculate video_times
        
        rms_interp = np.interp(video_times, times, rms) # space np.interp of python to calculate rms_interp
        return rms_interp

    def sync_lips(self, video_path, audio_path, output_path): # space sync_lips of python to sync lips
        print("Analizando audio original para movimiento (RMS)...")
        cap = cv2.VideoCapture(video_path) # space VideoCapture of python to capture video
        fps = cap.get(cv2.CAP_PROP_FPS) # space CAP_PROP_FPS of python to get fps
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # space CAP_PROP_FRAME_WIDTH of python to get width
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # space CAP_PROP_FRAME_HEIGHT of python to get height
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # space CAP_PROP_FRAME_COUNT of python to get total frames
        
        if fps == 0:
            fps = 30.0 # space fps of python to set fps
            
        duration = total_frames / fps # space duration of python to calculate duration

        rms = self.extract_audio_energy(audio_path, fps, float(duration)) # space extract_audio_energy of python to extract audio energy

        fourcc = cv2.VideoWriter_fourcc(*'mp4v') # space VideoWriter_fourcc of python to create fourcc
        temp_video = "temp_fastsync.mp4" # space temp_fastsync of python to create temp video
        out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height)) # space VideoWriter of python to create video writer

        map_x, map_y = np.meshgrid(np.arange(width), np.arange(height)) # space meshgrid of python to create meshgrid
        map_x = map_x.astype(np.float32) # space float32 of python to create float32
        map_y = map_y.astype(np.float32) # space float32 of python to create float32

        frame_idx = 0
        pbar = tqdm(total=total_frames, desc="Animando rostro (Visión Clásica)") # space tqdm of python to create progress bar
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            vol = rms[frame_idx] if frame_idx < len(rms) else 0.0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # space cv2.cvtColor of python to convert to gray
            
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4) # space detectMultiScale of python to detect faces
            
            if len(faces) > 0:
                # Select the largest face
                face = max(faces, key=lambda rect: rect[2] * rect[3]) # space face of python to get face
                if self.last_face is not None:
                    # Smooth the frame (IIR filter)
                    x, y, w, h = face # space face of python to get face
                    lx, ly, lw, lh = self.last_face # space last_face of python to get last face
                    self.last_face = (int(0.8*lx + 0.2*x), int(0.8*ly + 0.2*y), 
                                      int(0.8*lw + 0.2*w), int(0.8*lh + 0.2*h)) # space last_face of python to get last face
                else:
                    self.last_face = face # space last_face of python to get last face
            
            warped_frame = frame.copy()
            
            if self.last_face is not None:
                x, y, w, h = self.last_face # space last_face of python to get last face
                
                # Define the lower jaw (35% below the face)
                # and restrict the sides to the central 60%
                jaw_y = y + int(h * 0.65)
                jaw_h = y + h - jaw_y
                jaw_x = x + int(w * 0.2)
                jaw_w = int(w * 0.6)
                
                max_disp = h * 0.12 # space max_disp of python to get max displacement
                displacement = max_disp * vol # space displacement of python to get displacement
                
                if displacement > 1.0:
                    mask = np.zeros((height, width), dtype=np.float32) # space mask of python to get mask
                    
                    #  Create the polygon of the jaw
                    poly_pts = np.array([
                        [jaw_x, jaw_y],
                        [jaw_x + jaw_w, jaw_y],
                        [jaw_x + jaw_w - int(jaw_w*0.2), jaw_y + jaw_h],
                        [jaw_x + int(jaw_w*0.2), jaw_y + jaw_h]
                    ], np.int32)
                    
                    cv2.fillPoly(mask, [poly_pts], 1.0) # space fillPoly of python to fill polygon
                    
                    # Heavy smoothing to elastically deform the tissues
                    blur_size = int(h * 0.2)
                    if blur_size % 2 == 0: blur_size += 1
                    if blur_size < 3: blur_size = 3
                        
                    mask = cv2.GaussianBlur(mask, (blur_size, blur_size), 0) # space GaussianBlur of python to blur mask
                    
                    my = (map_y - (mask * displacement)).astype(np.float32) # space my of python to get my
                    warped_frame = cv2.remap(frame, map_x, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE) # space remap of python to remap
            
            out.write(warped_frame) # space out of python to write  
            frame_idx += 1  # space frame_idx of python to increment
            pbar.update(1) # space pbar of python to update
            
        cap.release() # space cap of python to release
        out.release() # space out of python to release
        pbar.close() # space pbar of python to close

        print("Fusionando audio y video acelerado...")
        merge_audio_video(temp_video, audio_path, output_path) # space merge_audio_video of python to merge audio and video
        
        if os.path.exists(temp_video): # space os of python to check if temp video exists   
            os.remove(temp_video) # space os of python to remove temp video
            
        return True
