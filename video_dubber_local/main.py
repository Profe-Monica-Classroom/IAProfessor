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
def process_video(input_video, output_video, target_lang, gender, quality, no_lipsync, progress_callback=None):
    """Core dubbing orchestration logic, callable from CLI or Flask App."""
    
    def update_progress(msg, percent):
        if progress_callback:
            progress_callback(msg, percent)
        else:
            print(msg)
            
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    update_progress(f"Iniciando procesamiento: {target_lang} ({gender})", 5)
    
    # Cloud handling (Bypass local process)
    if quality == "cloud":
        update_progress("Conectando con la nube (Hugging Face)...", 10)
        result_path = call_cloud_api(input_video, target_lang, gender)
        if result_path:
            shutil.copy(result_path, output_video)
            update_progress(f"¡Listo! Resultado en la nube guardado en: {output_video}", 100)
        else:
            update_progress("Error: El procesamiento en la nube falló.", 0)
        return output_video

    # 1. Extract Audio
    original_audio_path = os.path.join(temp_dir, "original_audio.wav")
    update_progress("Paso 1/5: Extrayendo audio original...", 15)
    audio_utils.extract_audio(input_video, original_audio_path)
    
    # Get video duration
    clip = VideoFileClip(input_video)
    duration = clip.duration
    clip.close()

    # 2. Transcribe
    update_progress("Paso 2/5: Transcribiendo el audio (Whisper)...", 30)
    transcriber = transcription.Transcriber(model_size="base")
    segments = transcriber.transcribe(original_audio_path)
    
    if not segments:
        update_progress("No se detectó voz en el video. Finalizando.", 100)
        return None

    # 3. Translate & TTS
    update_progress(f"Paso 3/5: Traduciendo a {target_lang} y generando voces...", 50)
    translator = translation.Translator(target=target_lang)
    tts_engine = tts.TTSEngine(voice=target_lang, gender=gender)
    
    audio_segments = []
    
    for i, seg in enumerate(tqdm(segments)):
        # Translate
        translated_text = translator.translate(seg['text'])
        
        # Generate Audio
        segment_audio_path = os.path.join(temp_dir, f"seg_{i}.mp3")
        tts_engine.generate(translated_text, segment_audio_path)
        
        audio_segments.append({
            'start': seg['start'],
            'path': segment_audio_path,
            'text': translated_text
        })
        
    # 4. Composite Audio
    update_progress("Paso 4/5: Ensamblando la nueva pista de audio maestro...", 75)
    mixed_audio_path = os.path.join(temp_dir, f"mixed_{target_lang}.wav")
    audio_utils.create_composite_audio(audio_segments, duration, mixed_audio_path)
    
    # 5. Lip Sync (or just simple merge)
    update_progress("Paso 5/5: Aplicando sincronización de video y audio...", 85)
    if no_lipsync:
        update_progress("Modo Solo Audio: Mezclando sin modificar labios...", 90)
        audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video)
    elif quality == "high":
        update_progress("Iniciando Sincronización Alta Calidad (Wav2Lip Neural)...", 90)
        success = run_wav2lip(input_video, mixed_audio_path, output_video)
        if not success:
            update_progress("Wav2Lip falló. Usando mezcla simple.", 95)
            audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video)
    elif quality == "intel":
        update_progress("Iniciando Sincronización Intel (OpenVINO NPU)...", 90)
        try:
            ov_engine = OpenVINOLipSync()
            success = ov_engine.sync_lips(input_video, mixed_audio_path, output_video)
            if not success: raise Exception("Inference failed")
        except Exception as e:
            update_progress(f"OpenVINO falló: {e}. Activando motor de respaldo rápido.", 92)
            ls_processor = MediaPipeLipSync()
            ls_processor.sync_lips(input_video, mixed_audio_path, output_video)
    else:
        update_progress("Iniciando Sincronización Rápida (YOLOv8 Pose)...", 90)
        ls_processor = MediaPipeLipSync()
        success = ls_processor.sync_lips(input_video, mixed_audio_path, output_video)
        if not success:
            update_progress("Sincronización de labios falló. Usando mezcla simple.", 95)
            audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video)

    update_progress(f"¡Proceso completado exitosamente!", 100)
    return output_video

# Main method to run the script
def main():
    parser = argparse.ArgumentParser(description="AI Video Dubber with Lip Sync")
    parser.add_argument("input", help="Path to input video (mp4)")
    parser.add_argument("--output", default="output_dubbed.mp4", help="Path to output video")
    parser.add_argument("--no_lipsync", action="store_true", help="Skip Wav2Lip step (just dubbing)")
    parser.add_argument("--target", default="es", help="Target language code (es, it, fr, de, etc.)")
    parser.add_argument("--gender", default="male", choices=["male", "female"], help="Voice gender (male or female)")
    parser.add_argument("--quality", default="fast", choices=["fast", "high", "cloud", "intel"], help="Lip sync quality (fast=OpenCV, high=Wav2Lip, cloud=HF Space, intel=OpenVINO)")
    
    args = parser.parse_args()
    
    # Add current dir to PATH to ensure ffmpeg.exe is found if present locally
    os.environ["PATH"] += os.pathsep + os.getcwd()
    
    input_video = os.path.abspath(args.input)
    output_video = os.path.abspath(args.output)
    
    process_video(input_video, output_video, args.target, args.gender, args.quality, args.no_lipsync)

if __name__ == "__main__":
    main()
