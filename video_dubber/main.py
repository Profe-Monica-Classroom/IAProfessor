import os
import argparse
from tqdm import tqdm
from moviepy import VideoFileClip

# Import our modules
import audio_utils
import transcription
import translation
import tts
# Import the new Lip Sync algorithm
from mediapipe_lipsync import MediaPipeLipSync

def main():
    parser = argparse.ArgumentParser(description="AI Video Dubber with Lip Sync")
    parser.add_argument("--input", required=True, help="Path to input video (mp4)")
    parser.add_argument("--output", default="output_dubbed.mp4", help="Path to output video")
    parser.add_argument("--no_lipsync", action="store_true", help="Skip Wav2Lip step (just dubbing)")
    parser.add_argument("--target", default="es", help="Target language code (es, it, fr, de, etc.)")
    
    args = parser.parse_args()
    
    # Paths setup
    # Add current dir to PATH to ensure ffmpeg.exe is found if present locally
    os.environ["PATH"] += os.pathsep + os.getcwd()
    
    input_video = os.path.abspath(args.input)
    output_video = os.path.abspath(args.output)
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Processing: {input_video} to {args.target}")
    
    # 1. Extract Audio
    original_audio_path = os.path.join(temp_dir, "original_audio.wav")
    print("Extracting audio...")
    audio_utils.extract_audio(input_video, original_audio_path)
    
    # Get video duration
    clip = VideoFileClip(input_video)
    duration = clip.duration
    clip.close()

    # 2. Transcribe
    print("Transcribing...")
    transcriber = transcription.Transcriber(model_size="base") # Use 'small' or 'medium' for better accuracy if GPU
    segments = transcriber.transcribe(original_audio_path)
    
    # 3. Translate & TTS
    print(f"Translating to {args.target} and generating speech...")
    translator = translation.Translator(target=args.target)
    tts_engine = tts.TTSEngine(voice=args.target) # Now handles language code mapping
    
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
    print("Compositing new audio track...")
    mixed_audio_path = os.path.join(temp_dir, f"mixed_{args.target}.wav")
    audio_utils.create_composite_audio(audio_segments, duration, mixed_audio_path)
    
    # 5. Lip Sync (or just simple merge)
    if args.no_lipsync:
        print("Skipping lip sync, merging audio directly...")
        audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video)
    else:
        print("Starting Fast Lip Sync (MediaPipe + OpenCV)...")
        ls_processor = MediaPipeLipSync()
        success = ls_processor.sync_lips(input_video, mixed_audio_path, output_video)
        if not success:
            print("Lip sync failed. Falling back to simple merge.")
            audio_utils.merge_audio_video(input_video, mixed_audio_path, output_video)

    print(f"Done! Output saved to: {output_video}")

if __name__ == "__main__":
    main()
