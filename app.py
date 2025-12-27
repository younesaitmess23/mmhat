from flask import Flask, after_this_request, render_template, request, send_file
import os
import re
import uuid
import yt_dlp

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")

DOWNLOAD_FOLDER = "/tmp/youtube_downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\s.-]", "", name, flags=re.UNICODE).strip()
    return cleaned or "video"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template("index.html", error="يرجى إدخال رابط فيديو صحيح.")

    download_id = uuid.uuid4().hex
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{download_id}.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")
            ext = info.get("ext", "mp4")
    except Exception as exc:
        return render_template(
            "index.html",
            error=f"تعذر تحميل الفيديو. تأكد من الرابط وحاول مرة أخرى. ({exc})",
        )

    filename = f"{_safe_filename(title)}.{ext}"
    downloaded_path = os.path.join(DOWNLOAD_FOLDER, f"{download_id}.{ext}")

    if not os.path.exists(downloaded_path):
        return render_template(
            "index.html",
            error="تم التحميل ولكن لم يتم العثور على الملف. حاول مرة أخرى.",
        )

    @after_this_request
    def cleanup(response):
        try:
            os.remove(downloaded_path)
        except OSError:
            pass
        return response

    return send_file(downloaded_path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
