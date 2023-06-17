import os
import subprocess
import vosk
import wave
import json
from flask import Flask, render_template, request, send_file, redirect, url_for

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Define the Vosk model path
model_path = "./vosk-model-en-us-0.30"

# Load the Vosk model
model = vosk.Model(model_path)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for file upload and transcription
@app.route('/upload', methods=['POST'])
def upload():
    # Get the uploaded file
    video_file = request.files['video']

    # Save the video file to the upload folder
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
    video_file.save(video_path)

    # Define the output audio file path
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_audio.wav")

    # Extract audio from the video file using ffmpeg
    subprocess.call(['ffmpeg', '-i', video_path, '-vn', '-ac', '1', '-ar', '16000', '-f', 'wav', audio_path])

    # Create a Vosk recognizer
    recognizer = vosk.KaldiRecognizer(model, 16000)

    # Open the audio file
    with wave.open(audio_path, 'rb') as audio_file:
        # Read audio data
        audio_data = audio_file.readframes(audio_file.getnframes())

        # Perform speech recognition
        recognizer.AcceptWaveform(audio_data)
        result = json.loads(recognizer.Result())

        # Get the transcription
        transcription = result['text']

    # Remove the temporary audio file
    os.remove(audio_path)

    # Save the transcription to a file
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], "transcription.txt")
    with open(output_file, 'w') as file:
        file.write(transcription)

    # Redirect to the thank you page
    return redirect(url_for('thankyou'))

# Route for the thank you page
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

if __name__ == '__main__':
    app.run()
