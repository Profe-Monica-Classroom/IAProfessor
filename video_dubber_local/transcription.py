import os
import sys

# Try to import faster_whisper, if it fails, fallback to SpeechRecognition
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except (ImportError, OSError):
    print("ADVERTENCIA: La librería 'faster_whisper' no se pudo cargar. Usando Google Speech Recognition como respaldo.")
    WHISPER_AVAILABLE = False
    import speech_recognition as sr

class Transcriber:
    def __init__(self, model_size="base"):
        self.use_whisper = WHISPER_AVAILABLE
        if self.use_whisper:
            try:
                # Using CPU with int8 computation is generally fast and robust on Intel processors
                self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            except Exception as e:
                print(f"Error al cargar el modelo Whisper: {e}")
                print("Usando Google Speech Recognition como respaldo.")
                self.use_whisper = False
        
        if not self.use_whisper:
            self.recognizer = sr.Recognizer()

    def transcribe(self, audio_path):
        """
        Transcribes audio. 
        Note: The fallback (Google) does not provide word-level timestamps easily,
        so we will treat the whole audio as one big segment or split by silence if needed (simplified here).
        """
        if self.use_whisper:
            try:
                # faster_whisper returns a generator of segments and info
                segments, info = self.model.transcribe(audio_path, beam_size=5)
                result_segments = []
                for segment in segments:
                    result_segments.append({
                        'start': segment.start,
                        'end': segment.end,
                        'text': segment.text.strip()
                    })
                return result_segments
            except Exception as e:
                print(f"La inferencia de Whisper falló: {e}. Cambiando al método de respaldo.")
        
        # Fallback: Use SpeechRecognition (Online) with pydub chunking
        print("Transcribiendo con Google Speech Recognition (Online) usando fragmentación...")
        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence
        except ImportError:
            print("Error: pydub no está instalado. No se puede fragmentar el audio. Instálelo vía pip...")
            return []

        try:
            # We assume ffmpeg is in PATH or current dir (handled in main.py)
            sound = AudioSegment.from_file(audio_path)
            
            # Split on silence
            # min_silence_len: ms, silence_thresh: dBFS
            chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=sound.dBFS-14, keep_silence=500)
            
            # If no chunks found (continuous audio?), treat as one
            if not chunks:
                chunks = [sound]

            result_segments = []
            current_time_ms = 0
            
            # Reconstruct timing is hard with split_on_silence because it removes silence (mostly).
            # A better approach for timing preservation is to detect non-silent ranges, 
            # but split_on_silence is easier to implement. 
            # We will use a naive approach: accumulation. 
            # NOTE: usage of split_on_silence loses exact absolute timing relative to original video
            # because the silence gaps are shortened/removed.
            # To fix the "3:05 silence" issue, simpler chunking by fixed time might be safer 
            # to preserve "some" timing structure, or just hoping split works.
            #
            # BETTER APPROACH for "sync" preservation without Whisper:
            # Split by fixed interval (e.g. 30s) to keep API happy, and assume linear time.

            # Let's switch to Fixed 60s Chunks to preserve timing easiest.
            chunk_length_ms = 60 * 1000
            chunks = []
            for i in range(0, len(sound), chunk_length_ms):
                chunks.append(sound[i:i+chunk_length_ms])

            for i, chunk in enumerate(chunks):
                # Export chunk to stream/file
                chunk_filename = f"temp_chunk_{i}.wav"
                chunk.export(chunk_filename, format="wav")
                
                with sr.AudioFile(chunk_filename) as source:
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data, language="en-US")
                        start_sec = (i * chunk_length_ms) / 1000.0
                        duration_sec = len(chunk) / 1000.0
                        
                        result_segments.append({
                            'start': start_sec,
                            'end': start_sec + duration_sec,
                            'text': text
                        })
                    except sr.UnknownValueError:
                        pass # No speech in this chunk
                    except sr.RequestError:
                        print(f"El fragmento {i} falló en la solicitud")
                
                # Cleanup
                if os.path.exists(chunk_filename):
                    os.remove(chunk_filename)

            return result_segments
            
        except Exception as e:
            print(f"La transcripción de respaldo falló: {e}")
            return []
