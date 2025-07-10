import os
from flask import Flask, request, jsonify, render_template
from mutagen import File as MutagenFile

app = Flask(__name__)

def get_audio_metadata(file_path):
    audio = MutagenFile(file_path, easy=True)
    if not audio or not audio.info:
        return None
    return {
        "file_name": os.path.basename(file_path),
        "duration": round(audio.info.length, 2),
        "sample_rate": getattr(audio.info, 'sample_rate', 'N/A'),
        "bitrate": getattr(audio.info, 'bitrate', 'N/A'),
        "channels": getattr(audio.info, 'channels', 'N/A'),
        "size_kb": round(os.path.getsize(file_path) / 1024, 2)
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")
    results = []
    os.makedirs("temp", exist_ok=True)

    for file in files:
        filepath = os.path.join("temp", file.filename)
        file.save(filepath)
        meta = get_audio_metadata(filepath)
        if meta:
            results.append(meta)
        os.remove(filepath)  # cleanup

    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
