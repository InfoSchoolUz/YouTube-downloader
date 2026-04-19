import streamlit as st
import yt_dlp
import os, tempfile, shutil, time

st.set_page_config(page_title="Smart Video Downloader", layout="centered")
st.title("🎬 Smart Video Downloader (YouTube / Instagram)")
st.caption("1080p gacha yuklab olish")

url = st.text_input("🔗 Video linkni kiriting:")

# --- Session state for progress ---
if "progress" not in st.session_state:
    st.session_state.progress = 0.0
if "status" not in st.session_state:
    st.session_state.status = ""

progress_bar = st.progress(0.0, text="")

def progress_hook(d):
    if d.get("status") == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        downloaded = d.get("downloaded_bytes", 0)
        if total > 0:
            p = min(downloaded / total, 1.0)
            st.session_state.progress = p
            st.session_state.status = f"Yuklanmoqda… {int(p*100)}%"
    elif d.get("status") == "finished":
        st.session_state.progress = 1.0
        st.session_state.status = "Birlashtirilmoqda (audio+video)…"

def is_valid(u: str) -> bool:
    u = u.lower()
    return any(x in u for x in ["youtube.com", "youtu.be", "instagram.com"])

col1, col2 = st.columns([1,1])
quality = col1.selectbox("🎯 Sifat", ["Best (<=1080p)", "720p", "480p"])
cleanup = col2.checkbox("📂 Yuklab bo‘lgach faylni o‘chirish", value=True)

if st.button("⬇️ Download"):
    if not url:
        st.warning("Link kiriting.")
        st.stop()
    if not is_valid(url):
        st.error("Faqat YouTube yoki Instagram link qo‘llab-quvvatlanadi.")
        st.stop()

    # temp papka
    tmpdir = tempfile.mkdtemp(prefix="vdl_")

    try:
        st.session_state.progress = 0.0
        st.session_state.status = "Boshlanmoqda…"
        progress_bar.progress(0.0, text="Boshlanmoqda…")

        # format tanlash
        if quality == "Best (<=1080p)":
            fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality == "720p":
            fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        else:
            fmt = "bestvideo[height<=480]+bestaudio/best[height<=480]"

        ydl_opts = {
            "format": fmt,
            "outtmpl": os.path.join(tmpdir, "%(title).80s.%(ext)s"),
            "merge_output_format": "mp4",
            "noplaylist": True,
            "progress_hooks": [progress_hook],
            # Instagram ba’zi hollarda UA talab qiladi:
            "http_headers": {"User-Agent": "Mozilla/5.0"},
            "quiet": True,
        }

        with st.spinner("Yuklab olinmoqda…"):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

        # Agar merge bo‘lsa, ext mp4 bo‘lishi mumkin
        base, _ = os.path.splitext(filename)
        final_file = base + ".mp4" if os.path.exists(base + ".mp4") else filename

        progress_bar.progress(1.0, text="Tayyor!")

        st.success("✅ Tayyor!")

        # Thumbnail (agar bor bo‘lsa)
        thumb = info.get("thumbnail")
        if thumb:
            st.image(thumb, caption=info.get("title", "Preview"), use_column_width=True)

        with open(final_file, "rb") as f:
            st.download_button(
                label="📥 Video yuklab olish",
                data=f,
                file_name=os.path.basename(final_file),
                mime="video/mp4"
            )

    except Exception as e:
        st.error(f"❌ Xatolik: {e}")

    finally:
        # foydalanuvchi yuklab olgandan keyin tozalash (bir oz kechiktirib)
        if cleanup:
            time.sleep(2)
            try:
                shutil.rmtree(tmp
