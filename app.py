from flask import Flask, render_template, request, jsonify
from mutagen import File as MutagenFile
import os

app = Flask(__name__)

def extract_metadata(file_storage):
    file_storage.seek(0)  # Make sure pointer is at start
    temp_path = os.path.join("temp", file_storage.filename)
    os.makedirs("temp", exist_ok=True)
    file_storage.save(temp_path)

    audio = MutagenFile(temp_path, easy=True)
    if not audio or not hasattr(audio, "info"):
        return None

    return {
        "file_name": file_storage.filename,
        "duration": round(audio.info.length, 2),
        "sample_rate": getattr(audio.info, 'sample_rate', 'N/A'),
        "bitrate": getattr(audio.info, 'bitrate', 'N/A'),
        "channels": getattr(audio.info, 'channels', 'N/A'),
        "size_kb": round(os.path.getsize(temp_path) / 1024, 2)
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    results = [extract_metadata(file) for file in files if file.filename]
    return jsonify([r for r in results if r])

if __name__ == "__main__":
    app.run(debug=True)

