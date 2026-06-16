import os
import subprocess
from flask import Flask, render_template_string, request, send_file, jsonify

app = Flask(__name__)

# Tampilan HTML + CSS Tailwind yang Mewah dan Responsive
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ YT Clip - Pemotong Video YouTube Gratis</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: radial-gradient(circle at top right, #1e1b4b, #0f172a); }
    </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col justify-between font-sans">

    <!-- Header / Navbar -->
    <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
            <div class="flex items-center gap-2 font-bold text-xl tracking-tight text-white">
                <span class="bg-gradient-to-r from-red-500 to-amber-500 bg-clip-text text-transparent flex items-center gap-2">
                    <i class="fa-solid fa-scissors text-red-500"></i> YTCLIP
                </span>
            </div>
            <span class="text-xs bg-slate-800 text-slate-400 px-2.5 py-1 rounded-full border border-slate-700">Versi Gratis v2.0</span>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-3xl mx-auto px-4 py-12 flex-1 w-full">
        <div class="text-center mb-10">
            <h1 class="text-4xl md:text-5xl font-black tracking-tight text-white mb-4">
                Potong Video YouTube <br>
                <span class="bg-gradient-to-r from-red-400 via-pink-500 to-amber-400 bg-clip-text text-transparent">Tanpa Batasan & Watermark</span>
            </h1>
            <p class="text-slate-400 text-base md:text-lg max-w-xl mx-auto">
                Tempel link, tentukan durasi, dan unduh klip video mp4 resolusi tinggi langsung ke perangkat Anda secara gratis.
            </p>
        </div>

        <!-- Card Form Utama -->
        <div class="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-2xl backdrop-blur-xl">
            <form id="clipForm" class="space-y-6">
                <!-- Input URL -->
                <div>
                    <label class="block text-sm font-semibold text-slate-300 mb-2">URL Video YouTube</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                            <i class="fa-brands fa-youtube text-lg"></i>
                        </div>
                        <input type="url" name="url" required placeholder="https://www.youtube.com/watch?v=..." 
                            class="w-full pl-11 pr-4 py-3.5 bg-slate-950/80 border border-slate-800 rounded-xl focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 text-white placeholder-slate-600 transition">
                    </div>
                </div>

                <!-- Input Waktu & Durasi -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-semibold text-slate-300 mb-2">Waktu Mulai (Start)</label>
                        <input type="text" name="start" required placeholder="00:01:20 atau detik" value="00:00:00"
                            class="w-full px-4 py-3.5 bg-slate-950/80 border border-slate-800 rounded-xl focus:outline-none focus:border-red-500 text-white transition text-center">
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-300 mb-2">Durasi Klip (Detik)</label>
                        <input type="number" name="duration" required placeholder="Misal: 30" value="30" min="1" max="120"
                            class="w-full px-4 py-3.5 bg-slate-950/80 border border-slate-800 rounded-xl focus:outline-none focus:border-red-500 text-white transition text-center">
                    </div>
                </div>

                <!-- Tombol Submit -->
                <button type="submit" id="btnSubmit"
                    class="w-full py-4 px-6 bg-gradient-to-r from-red-600 via-red-500 to-amber-500 hover:from-red-500 hover:to-amber-400 font-bold rounded-xl shadow-lg shadow-red-900/30 transition transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 text-white">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Proses & Gunting Video
                </button>
            </form>

            <!-- Loading & Status State -->
            <div id="statusArea" class="hidden mt-8 border-t border-slate-800/80 pt-6 text-center animate-fade-in">
                <div id="loader" class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-slate-700 border-t-red-500 mb-3"></div>
                <p id="statusText" class="text-sm text-slate-300 font-medium">Menghubungkan ke server YouTube...</p>
            </div>

            <!-- Download Button State -->
            <div id="downloadArea" class="hidden mt-8 border-t border-slate-800/80 pt-6 text-center">
                <div class="bg-emerald-950/30 border border-emerald-500/30 rounded-2xl p-4 mb-4 flex items-center justify-center gap-3 text-emerald-400">
                    <i class="fa-solid fa-circle-check text-xl"></i>
                    <span class="text-sm font-semibold">Video Berhasil Dipotong!</span>
                </div>
                <a id="btnDownload" href="#" download="youtube_clip.mp4"
                    class="inline-flex items-center gap-2 py-3.5 px-8 bg-slate-100 hover:bg-white text-slate-950 font-bold rounded-xl shadow-xl transition transform hover:-translate-y-0.5">
                    <i class="fa-solid fa-cloud-arrow-down"></i> Unduh File MP4
                </a>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-900 bg-slate-950/40 py-6 text-center text-xs text-slate-500">
        <p>&copy; 2026 YTClip Engine. Cloud processing bertenaga AI.</p>
    </footer>

    <!-- Logika Antarmuka (JavaScript) -->
    <script>
        const form = document.getElementById('clipForm');
        const btnSubmit = document.getElementById('btnSubmit');
        const statusArea = document.getElementById('statusArea');
        const statusText = document.getElementById('statusText');
        const downloadArea = document.getElementById('downloadArea');
        const btnDownload = document.getElementById('btnDownload');

        form.onsubmit = async (e) => {
            e.preventDefault();
            
            // Atur UI saat loading
            btnSubmit.disabled = true;
            btnSubmit.classList.add('opacity-50', 'cursor-not-allowed');
            downloadArea.classList.add('hidden');
            statusArea.classList.remove('hidden');
            
            const formData = new FormData(form);
            
            // Efek teks status berganti-ganti
            const infoTexts = [
                "Menghubungkan ke server YouTube...",
                "Mengunduh video asli (proses background)...",
                "Memotong bagian video dengan FFmpeg...",
                "Sedikit lagi, sedang merapikan file mp4..."
            ];
            let textIdx = 0;
            statusText.innerText = infoTexts[textIdx];
            const textInterval = setInterval(() => {
                if(textIdx < infoTexts.length - 1) {
                    textIdx++;
                    statusText.innerText = infoTexts[textIdx];
                }
            }, 5000);

            try {
                const response = await fetch('/api/clip', {
                    method: 'POST',
                    body: formData
                });
                
                clearInterval(textInterval);

                if (response.ok) {
                    // Jika sukses, ubah response blob menjadi link download
                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    btnDownload.href = downloadUrl;
                    
                    statusArea.classList.add('hidden');
                    downloadArea.classList.remove('hidden');
                } else {
                    const errData = await response.json();
                    alert("Gagal: " + (errData.error || "Terjadi kesalahan internal"));
                    statusArea.classList.add('hidden');
                }
            } catch (err) {
                clearInterval(textInterval);
                alert("Terjadi kesalahan koneksi ke server.");
                statusArea.classList.add('hidden');
            } finally {
                btnSubmit.disabled = false;
                btnSubmit.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/clip', methods=['POST'])
def clip_video():
    video_url = request.form.get('url')
    start_time = request.form.get('start', '00:00:00')
    duration = request.form.get('duration', '30')
    
    temp_download = "video_asli.mp4"
    output_filename = "clip.mp4"
    
    # Bersihkan file sisa
    for f in [temp_download, output_filename]:
        if os.path.exists(f):
            os.remove(f)
            
    try:
        # Unduh Video
        download_command = [
            "yt-dlp",
            "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
            "--max-filesize", "60M",
            "-o", temp_download,
            video_url
        ]
        subprocess.run(download_command, check=True)
        
        if os.path.exists(temp_download):
            # Potong Video dengan FFmpeg
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
            
            if os.path.exists(output_filename):
                return send_file(output_filename, as_attachment=True, download_name="youtube_clip.mp4")
                
        return jsonify({"error": "Gagal memproses file di server"}), 500
        
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Sistem gagal memproses video. Code: {e.returncode}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_download):
            os.remove(temp_download)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
