# app.py
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
import gradio as gr # space gradio of hugging face
import os # space os of python
import shutil # space shutil of python
from moviepy import VideoFileClip # space moviepy of python
import subprocess # space subprocess of python
from mediapipe_lipsync import MediaPipeLipSync # Backup for CPU
import audio_utils # internal module
import transcription # internal module
import translation # internal module
import tts # internal module

# Method to create temp directory
def create_temp_dir():
    os.makedirs("temp", exist_ok=True)
    return "temp"

# Method to run wav2lip (Running on CPU Basic)
def run_wav2lip(video_path, audio_path, output_path): # use of subprocess to run wav2lip
    cmd = [
        "python", "Wav2Lip/inference.py",
        "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
        "--face", video_path,
        "--audio", audio_path,
        "--outfile", output_path,
        "--resize_factor", "4", # Increment of resize_factor to reduce load on CPU
        "--nosmooth"
    ] 
    # use of try-except to handle errors
    try:
        subprocess.run(cmd, check=True) # use of check=True to check for errors
        return True
    except Exception as e:
        print(f"Error in Wav2Lip: {e}") # print error   
        return False

# Method to dub video
def dub_video(input_video, target_language_choice="Español - es", gender_choice="masculino", use_lipsync=True): # use of dub_video method
    temp_dir = create_temp_dir() # use of create_temp_dir method
    target_language = target_language_choice.split(" - ")[-1]
    
    # Mapeo de género (es -> en) para el motor TTS
    gender = "male" if "masculino" in gender_choice.lower() else "female"
    
    # 0. Normalize Video (Especialmente para Webcam)
    # Gradio manda videos en .webm o con fps variables desde la webcam. 
    # Lo normalizamos a .mp4 para que todas las librerías lo lean bien.
    normalized_video = os.path.join(temp_dir, "normalized_input.mp4")
    norm_cmd = [
        "ffmpeg", "-y", "-i", input_video, 
        "-c:v", "libx264", "-preset", "ultrafast", 
        "-c:a", "aac", normalized_video
    ]
    try:
        subprocess.run(norm_cmd, check=True, capture_output=True)
        input_video = normalized_video
    except Exception as e:
        print(f"Advertencia: No se pudo normalizar el video: {e}")

    # 1. Extract Audio
    original_audio_path = os.path.join(temp_dir, "original_audio.wav") # use of os.path.join to create path
    has_audio = audio_utils.extract_audio(input_video, original_audio_path) # use of extract_audio method
    
    clip = VideoFileClip(input_video)
    duration = clip.duration
    clip.close()

    if not has_audio:
        # Si no hay audio, no podemos transcribir ni traducir.
        # Retornamos el video original o uno con silencio.
        print("El video no tiene audio para procesar.")
        return input_video

    # 2. Transcribe
    transcriber = transcription.Transcriber(model_size="base")
    segments = transcriber.transcribe(original_audio_path)
    
    if not segments:
        print("No se detectó voz en el audio.")
        return input_video
    
    # 3. Translate & TTS
    translator = translation.Translator(target=target_language)
    tts_engine = tts.TTSEngine(voice=target_language, gender=gender) # Clean mapping
    
    audio_segments = [] # list to store audio segments
    
    for i, seg in enumerate(segments): # loop through segments
        trans_text = translator.translate(seg['text']) # translate text
        segment_audio_path = os.path.join(temp_dir, f"seg_{i}.mp3") # use of os.path.join to create path
        tts_engine.generate(trans_text, segment_audio_path) # use of generate method
        
        audio_segments.append({
            'start': seg['start'],
            'path': segment_audio_path,
            'text': trans_text
        })
        
    # 4. Composite Audio
    mixed_audio_path = os.path.join(temp_dir, f"mixed_{target_language}.wav") # use of os.path.join to create path
    audio_utils.create_composite_audio(audio_segments, duration, mixed_audio_path) # use of create_composite_audio method
    
    # 5. Output Video path
    output_video = os.path.join(temp_dir, "final_dubbed_video.mp4") # use of os.path.join to create path

    # 6. Lip Sync or Merge
    if use_lipsync:
        success = run_wav2lip(input_video, mixed_audio_path, output_video)   # use of run_wav2lip method
        if not success:
            audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video) # use of merge_audio_video method
    else:
        audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video) # use of merge_audio_video method

    return output_video

# --- Gradio UI ---
# Custom theme to match UNEXPO colors (Blue and White)
unexpo_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="blue",
    neutral_hue="slate",
).set(
    button_primary_background_fill="#0056b3", # UNEXPO Blue
    button_primary_background_fill_hover="#004494",
    button_primary_text_color="white",
    block_title_text_color="#0056b3",
)

# use of gradio to create web interface     
with gr.Blocks(title="AI Video Dubber & Lip Sync (Cloud Version)", theme=unexpo_theme) as demo: # use of Blocks to create web interface
    gr.Markdown("# 🎓 Doblaje de Videos Universitarios con IA") # use of Markdown to create title
    gr.Markdown("Sube un video en inglés y la IA lo traducirá, clonará la voz y sincronizará los labios. **Nota: Al usar CPU Basic, el proceso de labios puede tardar varios minutos.**") # use of Markdown to create description

    
    with gr.Row(): # use of Row to create row
        with gr.Column(): # use of Column to create column
            video_in = gr.Video(label="Sube tu video (Inglés)") # use of Video to create video input
            lang_drop = gr.Dropdown(
                choices=["Español - es", "Italiano - it", "Francés - fr", "Alemán - de", "Portugués - pt", "Japonés - ja", "Chino - zh"], 
                value="Español - es", 
                label="Idioma Destino"
            )
            gender_radio = gr.Radio(
                choices=["masculino", "femenino"], 
                value="masculino", 
                label="Género de la Voz",
                info="Selecciona si prefieres una voz masculina o femenina."
            )
            lip_check = gr.Checkbox(value=False, label="Sincronizar Labios (Wav2Lip) - ATENCIÓN: Muy lento en CPU Basic")  # use of Checkbox to create checkbox
            btn = gr.Button("🎤 Traducir y Sincronizar Video", variant="primary") # use of Button to create button
            
        with gr.Column(): # use of Column to create column
            video_out = gr.Video(label="Video Traducido Resultante") # use of Video to create video output
            
    btn.click(
        fn=dub_video,
        inputs=[video_in, lang_drop, gender_radio, lip_check],
        outputs=video_out
    )

    
    gr.Markdown("---")   # use of Markdown to create horizontal line
    gr.Markdown("*Desarrollado para fines educativos - Asignatura: Inteligencia Artificial - Unexpo Núcleo Guarenas. Prof. Mónica Tahan - mtahan@unexpo.edu.ve*") # use of Markdown to create description

if __name__ == "__main__":
    demo.launch()
