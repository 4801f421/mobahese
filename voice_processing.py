import speech_recognition as sr
import difflib


def convert_voice_to_text(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ar-SA")
            if not text.strip():
                return "صوت شما بسیار کوتاه یا نامفهوم بود. لطفاً دوباره تلاش کنید."
            return text
    except sr.UnknownValueError:
        return "صوت شما قابل تشخیص نبود. لطفاً دوباره تلاش کنید."
    except sr.RequestError as e:
        return f"خطا در برقراری ارتباط با سرویس تشخیص گفتار: {e}"
    except Exception as e:
        return f"خطای غیرمنتظره رخ داد: {e}"


def compare_texts(user_text, quran_text):
    user_words = user_text.split()
    quran_words = quran_text.split()

    matcher = difflib.SequenceMatcher(None, quran_words, user_words)
    differences = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                differences.append((i, quran_words[i], user_words[j]))
        elif tag == "delete":
            for i in range(i1, i2):
                differences.append((i, quran_words[i], None))
        elif tag == "insert":
            for j in range(j1, j2):
                differences.append((None, None, user_words[j]))

    return differences
