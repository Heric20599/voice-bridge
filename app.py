from flask import Flask, render_template, request, send_file
import os
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
from gtts import gTTS
from googletrans import Translator
from textblob import TextBlob

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/text-to-speech', methods=['GET', 'POST'])
def text_to_speech():
    if request.method == 'POST':
        text = request.form['text']
        tts = gTTS(text=text, lang='en')

        # Create a temporary file to save the speech
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            return send_file(temp_file.name, as_attachment=True, download_name='speech.mp3')
    return render_template('text_to_speech.html')


@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text():
    if request.method == 'POST':
        try:
            audio_file = request.files['audio']

            # Create a temporary file to save the uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                audio_path = temp_file.name
                audio_file.save(audio_path)

            # Convert audio file to WAV format if necessary
            audio = AudioSegment.from_file(audio_path)
            audio.export(audio_path, format="wav")

            # Initialize the recognizer and perform speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Delete the temporary file
            os.remove(audio_path)

            return render_template('speech_to_text.html', text=text)
        except Exception as e:
            # Handle exceptions (e.g., file errors, recognition errors)
            return render_template('speech_to_text.html', text="Error: " + str(e))

    return render_template('speech_to_text.html')


@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == 'POST':
        text = request.form['text']
        target_language = request.form['language']
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        return render_template('translate.html', translated_text=translated.text)
    return render_template('translate.html')


@app.route('/sentiment-analysis', methods=['GET', 'POST'])
def sentiment_analysis():
    if request.method == 'POST':
        text = request.form['text']
        blob = TextBlob(text)
        sentiment = blob.sentiment
        return render_template('sentiment_analysis.html', polarity=sentiment.polarity,
                               subjectivity=sentiment.subjectivity)
    return render_template('sentiment_analysis.html')


@app.route('/voice-to-sentiment', methods=['GET', 'POST'])
def voice_to_sentiment():
    if request.method == 'POST':
        try:
            audio_file = request.files['audio']

            # Create a temporary file to save the uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                audio_path = temp_file.name
                audio_file.save(audio_path)

            # Convert audio file to WAV format if necessary
            audio = AudioSegment.from_file(audio_path)
            audio.export(audio_path, format="wav")

            # Initialize the recognizer and perform speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Perform sentiment analysis on the transcribed text
            blob = TextBlob(text)
            sentiment = blob.sentiment

            # Delete the temporary file
            os.remove(audio_path)

            return render_template('voice_to_sentiment.html', text=text, polarity=sentiment.polarity,
                                   subjectivity=sentiment.subjectivity)
        except Exception as e:
            # Handle exceptions (e.g., file errors, recognition errors)
            return render_template('voice_to_sentiment.html', text="Error: " + str(e))

    return render_template('voice_to_sentiment.html')


@app.route('/file-upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        try:
            file = request.files['file']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                file_path = temp_file.name
                file.save(file_path)

            # Read the uploaded file and translate its content
            with open(file_path, 'r') as f:
                text = f.read()

            # For simplicity, let's assume target language is Spanish
            target_language = 'es'
            translator = Translator()
            translated = translator.translate(text, dest=target_language)

            # Save the translated content to a new file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                with open(temp_file.name, 'w') as f:
                    f.write(translated.text)

                # Delete the original file
                os.remove(file_path)

                return send_file(temp_file.name, as_attachment=True, download_name='translated.txt')
        except Exception as e:
            # Handle exceptions (e.g., file errors, translation errors)
            return render_template('file_upload.html', text="Error: " + str(e))

    return render_template('file_upload.html')


if __name__ == '__main__':
    app.run(debug=True)
