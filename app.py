from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/ytdl_downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def cleanup_file(path, delay=60):
    def _delete():
        time.sleep(delay)
        try:
            os.remove(path)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL gerekli"}), 400

    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title", "Bilinmiyor"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", ""),
                "view_count": info.get("view_count", 0),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url", "").strip()
    fmt = data.get("format", "mp3")

    if not url:
        return jsonify({"error": "URL gerekli"}), 400

    file_id = str(uuid.uuid4())

    if fmt == "mp3":
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp3")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path.replace(".mp3", ".%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }
    else:
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": output_path,
            "quiet": True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")

        if not os.path.exists(output_path):
            candidates = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(file_id)]
            if candidates:
                output_path = os.path.join(DOWNLOAD_FOLDER, candidates[0])

        cleanup_file(output_path, delay=120)

        mime = "audio/mpeg" if fmt == "mp3" else "video/mp4"
        safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
        download_name = f"{safe_title[:50]}.{fmt}"

        return send_file(
            output_path,
            mimetype=mime,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
