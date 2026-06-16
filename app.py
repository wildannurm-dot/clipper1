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
        st.info("Sedang memproses... Langkah ini mengunduh video terlebih dahulu, mohon tunggu beberapa saat.")
        
        temp_download = "video_asli.mp4"
        output_filename = "clip.mp4"
        
        # Hapus file lama jika ada agar tidak bentrok
        for f in [temp_download, output_filename]:
            if os.path.exists(f):
                os.remove(f)
                
        try:
            # Langkah 1: Unduh video YouTube dengan format terbaik yang sudah menggabungkan video+audio (maksimal 720p agar cepat dan ramah server gratisan)
            st.write("📥 Mengunduh video asli dari YouTube...")
            download_command = [
                "yt-dlp",
                "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]", # Cari mp4 terbaik yang ada audio+video
                "--max-filesize", "50M", # Batasi ukuran agar server Streamlit tidak crash
                "-o", temp_download,
                video_url
            ]
            subprocess.run(download_command, check=True)
            
            # Cek apakah file asli berhasil diunduh
            if os.path.exists(temp_download):
                st.write("✂️ Memotong video sesuai durasi...")
                
                # Langkah 2: Potong video lokal menggunakan FFmpeg
                ffmpeg_command = [
                    "ffmpeg",
                    "-ss", start_time,
                    "-i", temp_download,
                    "-t", duration,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-async", "1",
                    output_filename
                ]
                subprocess.run(ffmpeg_command, check=True)
                
                # Langkah 3: Sediakan tombol download jika berhasil
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
                    st.error("Gagal memotong video setelah diunduh.")
            else:
                st.error("Gagal mengunduh video dari YouTube. Format tidak didukung atau video terlalu besar.")
                
        except subprocess.CalledProcessError as e:
            st.error(f"Terjadi kesalahan pada sistem pemotong (FFmpeg/yt-dlp). Error code: {e.returncode}")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
        finally:
            # Bersihkan file sampah di server setelah selesai
            if os.path.exists(temp_download):
                os.remove(temp_download)
    else:
        st.warning("Silakan masukkan URL YouTube terlebih dahulu.")
