import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Video Downloader", layout="centered")

st.title("🎬 Smart Video Downloader")
st.write("YouTube va Instagram videolarni yuklab olish")

url = st.text_input("Video linkni kiriting:")

if st.button("Download"):
    if url:
        with st.spinner("Yuklab olinmoqda..."):
            try:
                ydl_opts = {
                    'format': 'best[height<=1080]',
                    'outtmpl': 'video.%(ext)s',
                    'merge_output_format': 'mp4'
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                st.success("Yuklab olindi!")

                with open(filename, "rb") as f:
                    st.download_button(
                        label="📥 Download video",
                        data=f,
                        file_name=os.path.basename(filename),
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"Xatolik: {e}")
    else:
        st.warning("Link kiriting!")
