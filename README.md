# Generator Subtitle Video - Auto Subtitle Generator

Aplikasi web untuk auto-generate dan sinkronisasi subtitle dari video menggunakan teknologi AI dan speech recognition.

## 🚀 Fitur Utama

- **Auto Speech-to-Text**: Menggunakan Whisper AI dan Google Speech Recognition
- **Sinkronisasi Otomatis**: Subtitle disinkronkan dengan timestamp video
- **Multiple Format Export**: Mendukung format SRT dan VTT
- **Modern Web Interface**: UI responsif dengan drag & drop upload
- **Real-time Processing**: Progress tracking dengan status update
- **Multi-format Support**: MP4, AVI, MOV, MKV, WMV

## 🛠️ Teknologi yang Digunakan

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: OpenAI Whisper, Google Speech Recognition
- **Audio Processing**: librosa, pydub, moviepy
- **UI Framework**: Modern CSS dengan Flexbox/Grid

## 📋 Persyaratan Sistem

- Python 3.10–3.11 direkomendasikan (Whisper/Torch lebih stabil).
- Python 3.12/3.13 dapat menyebabkan error build pada Whisper/Torch di Windows.
- FFmpeg (untuk pemrosesan audio/video)
- Koneksi internet (untuk Google Speech Recognition)
- RAM minimum 4GB (8GB direkomendasikan untuk Whisper)
- (Opsional) GPU NVIDIA + CUDA untuk percepatan inferensi Whisper

## 🔧 Instalasi

### 1. Clone Repository
```bash
git clone <https://github.com/RifqiArdian09/Generator-Subtitle-Video.git>
cd Generator-Subtitle-Video
```

### 2. Install FFmpeg
**Windows (disarankan):**
- Unduh FFmpeg build (release full) dari https://www.gyan.dev/ffmpeg/builds/
- Ekstrak, lalu copy folder `bin` ke lokasi tetap, mis. `C:\ffmpeg\bin`
- Tambahkan `C:\ffmpeg\bin` ke Environment Variables → Path
- Tutup dan buka ulang terminal

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Install Dependencies Python
Ada dua cara:

1) Cepat (coba dulu):
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2) Jika gagal (Windows/Python 3.12/3.13), instal manual bertahap:
```bash
python -m pip install --upgrade pip setuptools wheel

# CPU only (stabil di Windows). Jika ada GPU/CUDA, instal varian sesuai CUDA dari pytorch.org
pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

# Whisper versi stabil untuk Windows
pip install openai-whisper==20230314

# Paket lainnya
pip install Flask==2.3.3 Werkzeug==2.3.7 SpeechRecognition==3.10.0 \
            pydub==0.25.1 moviepy==1.0.3 numpy==1.24.3 librosa==0.10.0 \
            soundfile==0.12.1 ffmpeg-python==0.2.0
```

### 4. Jalankan Aplikasi
```bash
python subtitle_generator.py
```

Aplikasi akan berjalan di: http://localhost:5000

## 📖 Cara Penggunaan

### 1. Upload Video
- Buka browser dan akses http://localhost:5000
- Drag & drop video atau klik "Pilih Video"
- Pilih file video (MP4, AVI, MOV, MKV, WMV)
- Maksimal ukuran file: 500MB

### 2. Generate Subtitle
- Klik tombol "Generate Subtitle"
- Tunggu proses ekstraksi audio dan speech recognition
- Monitor progress melalui progress bar dan status

### 3. Preview & Download
- Preview subtitle yang telah digenerate
- Download dalam format SRT atau VTT
- Gunakan subtitle di video player favorit Anda

## 🏗️ Struktur Project

```
subtitle_generator/
├── subtitle_generator.py      # Main Flask application
├── requirements.txt           # Python dependencies
├── README.md                 # Documentation
├── templates/
│   └── index.html            # Main HTML template
├── static/
│   ├── style.css             # CSS styling
│   └── script.js             # JavaScript functionality
└── uploads/                  # Temporary upload directory
```

## ⚙️ Konfigurasi


### Konfigurasi Model Whisper
Aplikasi menggunakan model Whisper "base" secara default. Untuk akurasi lebih tinggi:

```python
# Di subtitle_generator.py, ubah:
self.whisper_model = whisper.load_model("large")  # Model lebih akurat tapi lambat
```

Model yang tersedia:
- `tiny`: Cepat, akurasi rendah
- `base`: Seimbang (default)
- `small`: Akurasi sedang
- `medium`: Akurasi tinggi
- `large`: Akurasi tertinggi, lambat

## 🔍 API Endpoints

### POST /upload
Upload video untuk diproses
- **Body**: FormData dengan file video
- **Response**: `{task_id: string, status: string}`

### GET /status/{task_id}
Cek status pemrosesan
- **Response**: `{status: string, progress: number, error?: string}`

### GET /preview/{task_id}
Preview subtitle yang telah digenerate
- **Response**: `{subtitles: Array<{start, end, text}>}`

### GET /export/{task_id}/{format}
Download subtitle dalam format tertentu
- **Formats**: `srt`, `vtt`
- **Response**: File download

## 🐛 Troubleshooting

### Error: "FFmpeg not found"
- Pastikan FFmpeg terinstall dan ada di PATH
- Windows: Restart command prompt setelah install FFmpeg

### Error: "No module named 'whisper'"
```bash
pip install openai-whisper
```

### Error saat install Whisper (KeyError `__version__`, build gagal)
- Gunakan Python 3.10/3.11 dan virtualenv baru
- Instal Torch terlebih dahulu (CPU):
  ```bash
  pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
  ```
- Lalu:
  ```bash
  pip install openai-whisper==20230314
  ```

### Python 3.12/3.13 di Windows
- Beberapa wheel belum tersedia atau tidak stabil untuk Whisper/Torch
- Solusi cepat: gunakan Python 3.10/3.11 di virtualenv terpisah untuk project ini

### Error: "Google Speech Recognition failed"
- Pastikan koneksi internet stabil
- Aplikasi akan fallback ke Whisper jika Google API gagal

### Torch + CUDA (opsional, untuk GPU)
- Kunjungi https://pytorch.org/get-started/locally/ dan ikuti perintah instal sesuai versi CUDA Anda
- Setelah Torch/torchaudio terpasang, barulah instal `openai-whisper`

### Video tidak bisa diproses
- Pastikan format video didukung (MP4, AVI, MOV, MKV, WMV)
- Cek ukuran file tidak melebihi 500MB
- Pastikan video memiliki audio track

### Subtitle tidak akurat
- Gunakan model Whisper yang lebih besar (`medium` atau `large`)
- Pastikan audio video berkualitas baik
- Hindari background noise yang berlebihan

## 🎯 Tips Penggunaan

1. **Kualitas Audio**: Video dengan audio jernih menghasilkan subtitle lebih akurat
2. **Bahasa**: Aplikasi dioptimalkan untuk Bahasa Indonesia dan Inggris
3. **Durasi Video**: Video pendek (< 10 menit) diproses lebih cepat
4. **Format Output**: Gunakan SRT untuk kompatibilitas maksimal




