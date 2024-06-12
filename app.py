from flask import Flask, render_template, request, send_file
import os
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from gtts import gTTS
from pytube import YouTube
import fitz  # PyMuPD


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/yt')
def yt():
    return render_template('yt.html')


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/tts')
def tts():
    return render_template('tts.html')

@app.route('/audibook')
def audibook():
    return render_template('audibook.html')


@app.route('/generate', methods=['POST'])
def generate():
    # Get the data from the form
    barcode_text = request.form['barcode_text']
    barcode_type = request.form['barcode_type']

    # Generate the barcode
    BARCODE = getattr(barcode, barcode_type)
    barcode_io = BytesIO()
    my_code = BARCODE(barcode_text, writer=ImageWriter())
    my_code.write(barcode_io)
    barcode_io.seek(0)

    # Set the filename for the download
    filename = f"{barcode_text}.png"

    return send_file(barcode_io, as_attachment=True, download_name=filename, mimetype='image/png')


@app.route('/speak', methods=['POST'])
def speak():
    text = request.form['text']
    tts = gTTS(text=text, lang='en')
    tts.save("static/speech.mp3")
    return send_file("static/speech.mp3", as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return "No file part"
    file = request.files['pdf']
    if file.filename == '':
        return "No selected file"
    if file:
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)
        text = extract_text_from_pdf(file_path)
        tts = gTTS(text=text, lang='en')
        audio_path = os.path.join("static", "audiobook.mp3")
        tts.save(audio_path)
        return send_file(audio_path, as_attachment=True)

@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        url = request.form['url']
        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path='downloads')
            filename = yt.title + '.mp4'
            return send_file('downloads/' + filename, as_attachment=True)
        except Exception as e:
            return str(e)


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
