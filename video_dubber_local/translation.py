from deep_translator import GoogleTranslator

class Translator:
    def __init__(self, source='en', target='es'):
        self.translator = GoogleTranslator(source=source, target=target)

    def translate(self, text):
        """Translates text from source to target language."""
        if not text:
            return ""
        return self.translator.translate(text)
