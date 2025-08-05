from flask import Flask, render_template, request, flash, redirect, url_for
from gtts import gTTS
from deep_translator import GoogleTranslator
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key'

AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Mapping of language names to codes
LANGUAGES = {
    'English': 'en',
    'Tamil': 'ta',
    'Hindi': 'hi',
    'Malayalam': 'ml',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Telugu': 'te',
    'Kannada': 'kn',
    'Gujarati': 'gu'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        lang_name = request.form.get('lang', '').strip()
        text = request.form.get('text', '').strip()

        if not lang_name or not text:
            flash("⚠️ Please select a language and enter some text.", "error")
            return redirect(url_for('index'))

        if lang_name not in LANGUAGES:
            flash("❌ Invalid language selection.", "error")
            return redirect(url_for('index'))

        lang_code = LANGUAGES[lang_name]

        try:
            # Translate text
            translated = GoogleTranslator(source='auto', target=lang_code).translate(text)

            # Generate unique audio file
            audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
            audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
            tts = gTTS(text=translated, lang=lang_code)
            tts.save(audio_path)

            # Remove old files (keep only last 3)
            audio_files = sorted(
                [f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.mp3')],
                key=lambda x: os.path.getmtime(os.path.join(AUDIO_FOLDER, x))
            )
            for old_file in audio_files[:-3]:
                os.remove(os.path.join(AUDIO_FOLDER, old_file))

            audio_url = f'audio/{audio_filename}'

            return render_template('application.html',
                                   translation=translated,
                                   audio_file=audio_url,
                                   languages=LANGUAGES.keys(),
                                   selected_lang=lang_name)

        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('index'))

    return render_template('application.html', languages=LANGUAGES.keys())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
