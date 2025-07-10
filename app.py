import os
from flask import Flask, request, jsonify, render_template, send_file
from mutagen import File as MutagenFile
import pandas as pd

app = Flask(__name__)

def get_audio_metadata(file_path):
    audio = MutagenFile(file_path, easy=True)
    if not audio or not audio.info:
        return None

    tags = audio.tags or {}

    duration_sec = round(audio.info.length, 2)

    def format_hhmmss(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"

    def format_mmss(seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02}"

    return {
        "file_name": os.path.basename(file_path),
        "duration_hhmmss": format_hhmmss(duration_sec),
        "duration_mmss": format_mmss(duration_sec),
        "duration_sec": duration_sec,
        "sample_rate": getattr(audio.info, 'sample_rate', 'N/A'),
        "bitrate": getattr(audio.info, 'bitrate', 'N/A'),
        "channels": getattr(audio.info, 'channels', 'N/A'),
        "size_kb": round(os.path.getsize(file_path) / 1024, 2),
        "album": tags.get('album', [''])[0],
        "album_artist": tags.get('albumartist', [''])[0],
        "track_number": tags.get('tracknumber', [''])[0]
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
        os.remove(filepath)

    return jsonify(results)

@app.route("/export_excel", methods=["POST"])
def export_excel():
    data = request.json
    df = pd.DataFrame(data)
    output_path = "audio_metadata.xlsx"
    df.to_excel(output_path, index=False)
    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
