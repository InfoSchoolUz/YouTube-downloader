import streamlit as st
import yt_dlp
import os
import tempfile
import shutil
import time

st.set_page_config(page_title="Smart Video Downloader", layout="centered")

st.title("🎬 Smart Video Downloader")
st.write("YouTube va Instagram videolarni yuklab olish (1080p gacha)")

url = st.text_input("🔗 Video linkni kiriting:")

# Progress
progress_bar = st.progress(0)
status_text = st.empty()

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
        downloaded = d.get('downloaded_bytes', 0)
        percent = int(downloaded / total * 100)
        progress_bar.progress(percent)
        status_text.text(f"Yuklanmoqda... {percent}%")
    elif d['status'] == 'finished':
        progress_bar.progress(100)
        status_text.text("Birlashtirilmoqda...")

def is_valid(u):
    return "youtube" in u or "youtu.be" in u or "instagram" in u

quality = st.selectbox("🎯 Sifatni tanlang", ["1080p", "720p", "480p"])
cleanup = st.checkbox("📂 Yuklab bo‘lgach faylni o‘chirish", value=True)

if st.button("⬇️ Download"):
    if not url:
        st.warning("Link kiriting!")
        st.stop()

    if not is_valid(url):
        st.error("Faqat YouTube yoki Instagram link qo‘llab-quvvatlanadi!")
        st.stop()

    tmpdir = tempfile.mkdtemp()

    try:
        if quality == "1080p":
            fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality == "720p":
            fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        else:
            fmt = "bestvideo[height<=480]+bestaudio/best[height<=480]"

        ydl_opts = {
            "format": fmt,
            "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "progress_hooks": [progress_hook],
            "noplaylist": True,
            "quiet": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            }
        }

        with st.spinner("⏳ Yuklab olinmoqda..."):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

        # Agar mp4 merge bo‘lsa
        base, _ = os.path.splitext(filename)
        final_file = base + ".mp4" if os.path.exists(base + ".mp4") else filename

        st.success("✅ Tayyor!")

        # Thumbnail
        if "thumbnail" in info:
            st.image(info["thumbnail"], caption=info.get("title", ""), use_column_width=True)

        # Download button
        with open(final_file, "rb") as f:
            st.download_button(
                label="📥 Yuklab olish",
                data=f,
                file_name=os.path.basename(final_file),
                mime="video/mp4"
            )

    except Exception as e:
        st.error(f"❌ Xatolik: {e}")

    finally:
        if cleanup:
            time.sleep(2)
            try:
                shutil.rmtree(tmpdir, ignore_errors=True)
            except:
                pass
