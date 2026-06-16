import streamlit as st
import os
import subprocess

st.set_page_config(page_title="YouTube Clipper Gratis", page_icon="🎬")
st.title("🎬 YouTube Video Clipper")
st.write("Potong video YouTube langsung secara gratis tanpa watermark!")

# Input dari pengguna
video_url = st.text_input("Masukkan URL Video YouTube:")
start_time = st.text_input("Waktu Mulai (Format: HH:MM:SS atau detik, misal: 00:01:20):", "00:00:00")
duration = st.text_input("Durasi Klip (dalam detik, misal: 30):", "30")

if st.button("Gunting Video ✂️"):
    if video_url:
        st.info("Sedang memproses video... Mohon tunggu (proses ini bergantung pada durasi dan server).")
        
        output_filename = "clip.mp4"
        
        # Hapus file lama jika ada
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
        try:
            # Perintah yt-dlp yang efisien menggunakan external downloader ffmpeg untuk memotong langsung
            # Ini menghemat kuota server dan mempercepat proses
            command = [
                "yt-dlp",
                "-g",  # Mengambil URL streaming mentah dari YouTube
                video_url
            ]
            
            # Jalankan yt-dlp untuk mendapatkan URL video asli
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            urls = result.stdout.strip().split('\n')
            
            if urls:
                video_stream_url = urls[0] # Ambil stream pertama (biasanya sudah include audio/video gabungan di format tertentu)
                
                # Proses pemotongan menggunakan FFmpeg langsung dari URL streaming
                ffmpeg_command = [
                    "ffmpeg",
                    "-ss", start_time,
                    "-i", video_stream_url,
                    "-t", duration,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-strict", "experimental",
                    output_filename
                ]
                
                subprocess.run(ffmpeg_command, check=True)
                
                if os.path.exists(output_filename):
                    st.success("Video berhasil dipotong!")
                    with open(output_filename, "rb") as file:
                        st.download_button(
                            label="📥 Download Hasil Klip",
                            data=file,
                            file_name="youtube_clip.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Gagal membuat file klip.")
            else:
                st.error("Gagal mendapatkan stream URL dari YouTube.")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
    else:
        st.warning("Silakan masukkan URL YouTube terlebih dahulu.")
