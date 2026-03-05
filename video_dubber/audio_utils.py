from moviepy import VideoFileClip, AudioFileClip #package for audio processing
import os

def extract_audio(video_path, output_audio_path):
    """Extracts audio from a video file. Returns True if audio exists, False otherwise."""
    video = VideoFileClip(video_path)
    if video.audio is not None:
        video.audio.write_audiofile(output_audio_path, logger=None)
        video.close()
        return True
    else:
        video.close()
        # Create a silent audio file if no audio is found
        print("No audio track found in video. Creating silence.")
        return False

def merge_audio_video(video_path, audio_path, output_path):
    """Merges a video file with a new audio track."""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Trim audio/video to match the shorter one or just set audio
    final_video = video.with_audio(audio)
    
    # Write output
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
    video.close()
    audio.close()

from moviepy import AudioFileClip, CompositeAudioClip

def create_composite_audio(audio_segments, total_duration, output_path):
    """
    audio_segments: list of {'start': float, 'path': str}
    Ensures segments do not overlap by shifting them forward if necessary.
    """
    clips = []
    last_end_time = 0.0
    
    for seg in audio_segments:
        if os.path.exists(seg['path']):
            clip = AudioFileClip(seg['path'])
            
            # Start time is either the original start or the end of the last clip
            # whichever is later, to avoid overlapping.
            actual_start = max(seg['start'], last_end_time)
            
            clip = clip.with_start(actual_start)
            clips.append(clip)
            
            last_end_time = actual_start + clip.duration
    
    final_audio = CompositeAudioClip(clips)
    final_audio = final_audio.with_duration(total_duration)
    final_audio.write_audiofile(output_path, fps=44100)
    
    # close clips to release file handles
    for clip in clips:
        clip.close()
    final_audio.close()
