""" #######################################################################################
# RECURSO ACADÉMICO CREADO POR LA PROFESORA MÓNICA TAHAN CON EL USO DE GOOGLE ANTIGRAVITY #
# ACADEMY RESOURCE CREATED BY PROFESSOR MÓNICA TAHAN WITH THE USE OF GOOGLE ANTIGRAVITY   #
# Este script es una aplicación web que permite doblar videos en inglés a otros idiomas   #
# This script is a web application that allows you to dub videos in English to other      #
# languages                                                                               #
# Product Owner: Prof. Carlos Mijares                                                     #
# Autor: Mónica Tahan y Google Antigravity AI                                             #
# Author: Mónica Tahan and Google Antigravity AI                                          #
# Versión: 1.0                                                                            #
# Version: 1.0                                                                            #
# Fecha: 26/02/2026                                                                       # 
# Date: 02/26/2026                                                                        #
# Licencia: GNU/GPL                                                                       #
# License: GNU/GPL                                                                        #
###########################################################################################
"""

import os # space os of python
import argparse # space argparse of python
from tqdm import tqdm # space tqdm of python
from moviepy import VideoFileClip # space moviepy of python
import subprocess # space subprocess for Wav2Lip
import shutil # space shutil for file copying

# Import our modules
import audio_utils # space audio_utils of python
import transcription # space transcription of python
import translation # space translation of python
import tts # space tts of python
# Import the new Lip Sync algorithm
from mediapipe_lipsync import MediaPipeLipSync # space mediapipe_lipsync of python
from openvino_lipsync import OpenVINOLipSync # NEW: Intel OpenVINO Engine
from lipsync_nvidia import run_wav2lip # Restored: NVIDIA/CUDA Engine
from gradio_client import Client, handle_file # space gradio_client for cloud processing

HF_SPACE_URL = "mtahan/unexpo-videotranslator"
# Function to call Hugging Face Space for cloud processing
def call_cloud_api(video_path, target_lang, gender):
    """Offloads the entire processing to Hugging Face Space."""
    print(f"Connecting to Hugging Face Space: {HF_SPACE_URL}...")
    try:
        client = Client(HF_SPACE_URL)
        print("¡Conectado! Enviando video y esperando procesamiento en la nube (esto puede tardar unos minutos)...")
        # Mapping language code to the descriptive string the Space expects
        lang_map = {
            "es": "Español - es", "it": "Italiano - it", "fr": "Francés - fr",
            "de": "Alemán - de", "pt": "Portugués - pt", "ja": "Japonés - ja", "zh": "Chino - zh"
        }
        target_choice = lang_map.get(target_lang, "Español - es")
        gender_choice = "masculino" if gender == "male" else "femenino"
        
        result = client.predict(
            handle_file(video_path), # input_video
            target_choice,           # target_language_choice
            gender_choice,           # gender_choice
            True,                    # use_lipsync
            fn_index=0
        )
        return result
    except Exception as e:
        print(f"Cloud processing failed: {e}")
        return None
# Method to run Wav2Lip with high quality
def run_wav2lip(video_path, audio_path, output_path):
    """Runs the high-quality Wav2Lip model (requires GPU for speed)."""
    # Wav2Lip is expected in the current directory (linked via Junction)
    cmd = [
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "--face", video_path,
        "--audio", audio_path,
        "--outfile", output_path,
        "--nosmooth"
    ]
    try:
        # What this does is run the command in the terminal? subprocess execute the command into a shell
        subprocess.run(cmd, check=True) # Run the command
        return True
    except Exception as e:
        print(f"Error in Wav2Lip high-quality: {e}") # Print error if it fails
        return False
# Main method to run the script
def main():
    parser = argparse.ArgumentParser(description="AI Video Dubber with Lip Sync") # use of argparse to create parser. What this does is create a parser object that can be used to parse command-line arguments
    parser.add_argument("input", help="Path to input video (mp4)") # use of argparse to create positional input argument
    parser.add_argument("--output", default="output_dubbed.mp4", help="Path to output video") # use of argparse to create output argument
    parser.add_argument("--no_lipsync", action="store_true", help="Skip Wav2Lip step (just dubbing)") # use of argparse to create no_lipsync argument
    parser.add_argument("--target", default="es", help="Target language code (es, it, fr, de, etc.)") # use of argparse to create target argument
    parser.add_argument("--gender", default="male", choices=["male", "female"], help="Voice gender (male or female)") # use of argparse to create gender argument
    parser.add_argument("--quality", default="fast", choices=["fast", "high", "cloud", "intel"], help="Lip sync quality (fast=OpenCV, high=Wav2Lip, cloud=HF Space, intel=OpenVINO)") # use of argparse to create quality argument
    
    args = parser.parse_args() # use of argparse to parse arguments
    
    # Paths setup
    # Add current dir to PATH to ensure ffmpeg.exe is found if present locally
    os.environ["PATH"] += os.pathsep + os.getcwd() # use of os.environ to set path
    
    input_video = os.path.abspath(args.input) # use of os.path.abspath to get absolute path
    output_video = os.path.abspath(args.output) # use of os.path.abspath to get absolute path
    temp_dir = "temp" # use of os.path.join to create path
    os.makedirs(temp_dir, exist_ok=True) # use of os.makedirs to create directory
    
    print(f"Processing: {input_video} to {args.target} ({args.gender})")
    
    # NEW: Cloud handling (Bypass local process)
    if args.quality == "cloud":
        result_path = call_cloud_api(input_video, args.target, args.gender) # Call the cloud API
        if result_path:
            shutil.copy(result_path, output_video) # Copy the result to the output path
            print(f"Done! Cloud result saved to: {output_video}") # Print the result path
        else:
            print("El procesamiento en la nube falló. Verifique la conexión a internet o la URL del Space.") # Print error if it fails
        return

    # 1. Extract Audio
    original_audio_path = os.path.join(temp_dir, "original_audio.wav")
    print("Extrayendo audio...")     # Print message
    audio_utils.extract_audio(input_video, original_audio_path) # Extract audio from video
    
    # Get video duration
    clip = VideoFileClip(input_video) # Get video duration
    duration = clip.duration # Get video duration
    clip.close() # Close the video

    # 2. Transcribe
    print("Transcribiendo...") # Print message
    transcriber = transcription.Transcriber(model_size="base") # Initialize the transcriber
    segments = transcriber.transcribe(original_audio_path) # Transcribe the audio
    
    if not segments:
        print("No speech detected. Exiting.") # Print error if no speech detected
        return

    # 3. Translate & TTS
    print(f"Traduciendo a {args.target} ({args.gender}) y generando voz...") # Print message
    translator = translation.Translator(target=args.target) # Initialize the translator
    tts_engine = tts.TTSEngine(voice=args.target, gender=args.gender) # Initialize the TTS engine
    
    audio_segments = [] # use of audio_segments to store the audio segments
    
    for i, seg in enumerate(tqdm(segments)):
        # Translate
        translated_text = translator.translate(seg['text'])
        
        # Generate Audio
        segment_audio_path = os.path.join(temp_dir, f"seg_{i}.mp3") # use of os.path.join to create segment audio path
        tts_engine.generate(translated_text, segment_audio_path) # use of tts_engine to generate audio
        # use of audio_segments to store the audio segments
        audio_segments.append({
            'start': seg['start'],
            'path': segment_audio_path,
            'text': translated_text
        })
        
    # 4. Composite Audio
    print("Componiendo nueva pista de audio...") # use of audio_utils to create composite audio
    mixed_audio_path = os.path.join(temp_dir, f"mixed_{args.target}.wav") # use of os.path.join to create mixed audio path
    audio_utils.create_composite_audio(audio_segments, duration, mixed_audio_path) # use of audio_utils to create composite audio
    
    # 5. Lip Sync (or just simple merge)
    if args.no_lipsync:
        print("Saltando lip sync, mezclando audio directamente...") # use of audio_utils to merge audio
        audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video) # use of audio_utils to merge audio
    elif args.quality == "high":
        print("Iniciando Lip Sync de Alta Calidad (Wav2Lip)...") # Print message
        success = run_wav2lip(input_video, mixed_audio_path, output_video) # Run the Wav2Lip model
        if not success:
            print("Wav2Lip falló. Usando mezcla simple por defecto.") # Print error if it fails
            audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video)
    elif args.quality == "intel":
        print("Iniciando Aceleración de Hardware Intel OpenVINO...") # Print message
        try:
            ov_engine = OpenVINOLipSync() # Initialize the OpenVINO engine
            success = ov_engine.sync_lips(input_video, mixed_audio_path, output_video) # Run the OpenVINO engine
            if not success: raise Exception("Inference failed")
        except Exception as e:
            print(f"OpenVINO falló: {e}. Usando Sincronización Rápida.") # Print error if it fails
            ls_processor = MediaPipeLipSync() # Initialize the MediaPipe engine
            ls_processor.sync_lips(input_video, mixed_audio_path, output_video) # Run the MediaPipe engine
    else:
        print("Iniciando Sincronización Rápida (MediaPipe + OpenCV)...") # Print message
        ls_processor = MediaPipeLipSync() # Initialize the MediaPipe engine
        success = ls_processor.sync_lips(input_video, mixed_audio_path, output_video) # Run the MediaPipe engine
        if not success:
            print("Sincronización de labios falló. Usando mezcla simple.") # Print error if it fails
            audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video) # use of audio_utils to merge audio 

    print(f"¡Listo! Resultado guardado en: {output_video}") # Print message

if __name__ == "__main__":
    main()
