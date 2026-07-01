# CoreDoc - Tool Manajemen & Konversi Dokumen

CoreDoc adalah alat berbasis web yang komprehensif untuk manajemen dan konversi dokumen yang dibangun menggunakan Python dan Flask. Aplikasi ini menawarkan antarmuka pengguna yang ramping, modern, dan responsif dengan Tailwind CSS (dilengkapi juga dengan fitur *Dark Mode*).

## Fitur

- **Konversi Word ke PDF:** Ubah file `.docx` menjadi `.pdf` dengan mudah. Mendukung konversi banyak file sekaligus (*batch*).
- **Konversi PDF ke Word:** Ubah dokumen `.pdf` kembali menjadi file `.docx` yang dapat diedit. Mendukung konversi *batch*.
- **Smart OCR:** Ekstrak teks dari gambar (`.png`, `.jpg`, `.jpeg`) menggunakan teknologi *Optical Character Recognition* (OCR).
- **Riwayat Aktivitas (Activity History):** Pengelola riwayat bawaan yang mencatat semua konversi dan ekstraksi Anda, memungkinkan Anda mengunduh ulang file, melihat teks yang diekstrak, atau membersihkan riwayat lama.

## Prasyarat

Karena menggunakan pustaka dasar tertentu (seperti `docx2pdf` dan `pywin32`), aplikasi ini berjalan paling optimal di sistem operasi **Windows**. Anda membutuhkan:

- **Python 3.8+** terinstal pada sistem Anda.
- **Microsoft Word** terinstal pada sistem Anda (diperlukan oleh modul `docx2pdf` untuk melakukan konversi dari Word ke PDF).

## Cara Instalasi

1. **Clone atau Unduh Repository:**
   Unduh folder proyek ini ke komputer lokal Anda.

2. **Buka Direktori Proyek:**
   Buka terminal (Command Prompt atau PowerShell) dan arahkan ke direktori proyek:
   ```bash
   cd path\to\TUBES_PBO_PyDocSuite_Tool_Manajemen_dan_Konversi_Dokumen_Digital
   ```

3. **Buat Virtual Environment (Disarankan):**
   ```bash
   python -m venv .venv
   ```

4. **Aktifkan Virtual Environment:**
   - **Command Prompt:**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **PowerShell:**
     ```powershell
     .venv\Scripts\Activate.ps1
     ```

5. **Instal Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

   *Catatan: Jika Anda mengalami masalah dengan `easyocr` (digunakan untuk Smart OCR), modul tersebut mungkin perlu mengunduh model bahasa pada saat pertama kali dijalankan.*

## Cara Penggunaan

1. **Jalankan Aplikasi:**
   Dengan *virtual environment* yang sudah aktif, jalankan perintah berikut:
   ```bash
   python app.py
   ```

2. **Akses Antarmuka Web:**
   Buka *browser* web favorit Anda dan buka alamat:
   ```
   http://127.0.0.1:5000
   ```

3. **Petunjuk Penggunaan:**
   - Gunakan bilah navigasi di atas (atau di menu *hamburger* pada perangkat seluler) untuk berpindah antar alat/fitur.
   - Unggah file Anda, tunggu proses selesai, lalu unduh hasilnya.
   - Anda dapat mengubah tampilan ke mode Terang/Gelap menggunakan ikon Matahari/Bulan di pojok kanan atas.
   - Akses aktivitas dan file lama Anda dari tab "History".

## Struktur Proyek

```
├── app.py                  # File utama (entry point) aplikasi Flask
├── config.py               # Konfigurasi dan pengaturan aplikasi
├── requirements.txt        # Daftar dependensi modul Python
├── controllers/            # Pengelola rute (route handlers) untuk setiap fitur
├── models/                 # Logika alat konversi dan model database SQLite
├── storage/                # Folder penyimpanan sementara file yang diunggah dan dikonversi
└── templates/              # Template HTML (Jinja2) untuk antarmuka pengguna
```

## Penafian (Disclaimer)
Proyek ini dibangun sebagai bagian dari Tugas Besar (Tubes) mata kuliah Pemrograman Berorientasi Objek (PBO). Pastikan Anda memiliki aplikasi MS Office di OS Windows agar modul dan skrip konversi dapat berjalan dengan baik dan andal.
