import asyncio
import edge_tts
import os

VOICE_MAPPING = {
    "es": {"male": "es-ES-AlvaroNeural", "female": "es-MX-DaliaNeural"},
    "en": {"male": "en-US-GuyNeural", "female": "en-US-EmmaNeural"},
    "fr": {"male": "fr-FR-HenriNeural", "female": "fr-FR-DeniseNeural"},
    "it": {"male": "it-IT-DiegoNeural", "female": "it-IT-ElsaNeural"},
    "de": {"male": "de-DE-ConradNeural", "female": "de-DE-KatjaNeural"},
    "pt": {"male": "pt-PT-DuarteNeural", "female": "pt-BR-FranciscaNeural"},
    "ja": {"male": "ja-JP-KeitaNeural", "female": "ja-JP-NanamiNeural"},
    "zh": {"male": "zh-CN-YunxiNeural", "female": "zh-CN-XiaoxiaoNeural"}
}

class TTSEngine:
    def __init__(self, voice="es", gender="male"):
        # If the input is a language code, map it to a specific voice based on gender
        if voice in VOICE_MAPPING:
            # Default to male if gender is not found
            self.voice = VOICE_MAPPING[voice].get(gender, VOICE_MAPPING[voice]["male"])
        else:
            self.voice = voice # Raw voice string

    async def _generate_audio(self, text, output_file):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_file)

    def generate(self, text, output_file):
        """Synchronous wrapper for generating audio."""
        if not text:
            return
        asyncio.run(self._generate_audio(text, output_file))

