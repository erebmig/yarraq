# VORTEX — YouTube Downloader

Modern YouTube MP3/MP4 indirme uygulaması. Flask + yt-dlp.

## Render'a Deploy

1. Bu projeyi GitHub'a push'la
2. [render.com](https://render.com) → New → Web Service
3. GitHub repo'nu bağla
4. **Build Command:**
   ```
   apt-get install -y ffmpeg && pip install -r requirements.txt
   ```
5. **Start Command:**
   ```
   gunicorn app:app
   ```
6. Deploy — bitti.

> ⚠ **Yasal Uyarı:** İndirilen içeriklerin sorumluluğu tamamen kullanıcıya aittir.
