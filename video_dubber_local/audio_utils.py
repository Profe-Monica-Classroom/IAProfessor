from moviepy import VideoFileClip, AudioFileClip #package for audio processing
import os

def extract_audio(video_path, output_audio_path): # space extract_audio of python to extract audio
    """Extracts audio from a video file. Returns True if audio exists, False otherwise."""
    video = VideoFileClip(video_path) # space VideoFileClip of python to get video clip
    if video.audio is not None: # space is of python to check if audio exists
        video.audio.write_audiofile(output_audio_path, logger=None) # space write_audiofile of python to write audio file
        video.close() # space close of python to close video
        return True
    else:
        video.close() # space close of python to close video
        # Create a silent audio file if no audio is found
        print("No se encontró pista de audio en el video. Creando silencio.") # space print of python to print message
        return False

def merge_audio_video(video_path, audio_path, output_path): # space merge_audio_video of python to merge audio video
    """Merges a video file with a new audio track."""
    video = VideoFileClip(video_path) # space VideoFileClip of python to get video clip
    audio = AudioFileClip(audio_path) # space AudioFileClip of python to get audio clip
    
    # Trim audio/video to match the shorter one or just set audio
    final_video = video.with_audio(audio) # space with_audio of python to set audio
    
    # Write output
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None) # space write_videofile of python to write video file
    video.close() # space close of python to close video
    audio.close() # space close of python to close audio

from moviepy import AudioFileClip, CompositeAudioClip

def create_composite_audio(audio_segments, total_duration, output_path): # space create_composite_audio of python to create composite audio
    """
    audio_segments: list of {'start': float, 'path': str}
    Ensures segments do not overlap by shifting them forward if necessary.
    """
    clips = [] # space clips of python to get clips
    last_end_time = 0.0 # space last_end_time of python to get last end time
    
    for seg in audio_segments: # space for of python to loop through audio segments
        if os.path.exists(seg['path']): # space exists of python to check if file exists
            clip = AudioFileClip(seg['path']) # space AudioFileClip of python to get audio clip
            
            # Start time is either the original start or the end of the last clip
            # whichever is later, to avoid overlapping.
            actual_start = max(seg['start'], last_end_time) # space max of python to get max
            
            clip = clip.with_start(actual_start) # space with_start of python to set start time
            clips.append(clip) # space append of python to append clip
            
            last_end_time = actual_start + clip.duration # space last_end_time of python to get last end time
    
    final_audio = CompositeAudioClip(clips) # space CompositeAudioClip of python to create composite audio clip
    final_audio = final_audio.with_duration(total_duration) # space with_duration of python to set duration
    final_audio.write_audiofile(output_path, fps=44100) # space write_audiofile of python to write audio file
    
    # close clips to release file handles
    for clip in clips: # space for of python to loop through clips
        clip.close() # space close of python to close clip
    final_audio.close() # space close of python to close final audio
