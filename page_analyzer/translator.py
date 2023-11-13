from googletrans import Translator


def translate(text, language='ru'):
    translator = Translator()
    return translator.translate(text, dest=language).text
