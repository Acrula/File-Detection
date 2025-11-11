### 🚀 Panduan Penggunaan `deteksi_file.py` (Deteksi Penyamaran File)
1. Prasyarat Sistem

    Aplikasi ini memiliki dependensi eksternal, terutama untuk fitur pratinjau PDF.

    A. Instalasi Python dan Library

    Pastikan Anda sudah menginstal Python (disarankan versi 3.6 ke atas). Kemudian, instal library yang dibutuhkan:
    
        pip install ttkbootstrap filetype reportlab pillow pdf2image
    B. Instalasi Poppler (Penting untuk Pratinjau PDF)
    Modul `pdf2image` membutuhkan utilitas eksternal bernama Poppler untuk mengonversi PDF menjadi gambar.

    - Untuk Windows:
    
      Unduh Poppler untuk Windows (misalnya dari link ini).
    
      Ekstrak file zip ke lokasi yang mudah diingat, misalnya C:\poppler.
    
      Anda perlu mengedit baris kode di fungsi tampilkan_pdf skrip Anda:
   
              Ganti baris ini:
              self.pages = convert_from_path(path_pdf, poppler_path=r"C:\poppler\Library\bin")
              # Sesuaikan path ke folder 'bin' di dalam folder Poppler yang Anda ekstrak.
     - Untuk Linux/macOS:
       Poppler biasanya dapat diinstal melalui package manager sistem (misalnya `sudo apt install poppler-utils` di Debian/Ubuntu atau  `brew install poppler` di macOS). Jika diinstal melalui package manager, Anda mungkin tidak perlu menentukan `poppler_path`.
2. Menjalankan Aplikasi
   Jalankan skrip dari terminal atau command prompt:

        python deteksi_file.py
   
   Aplikasi dengan antarmuka grafis (GUI) akan muncul.

3. Cara Menggunakan Aplikasi
   Antarmuka Utama
   
   Langkah 1: Pilih Target
   
      1.  Di bagian "🧭 Pilih Target:", tentukan mode pemindaian:

          - Folder: Untuk menganalisis semua file dalam sebuah folder beserta sub-foldernya.
          
          - File: Untuk menganalisis satu file saja.

      2. Klik tombol "Browse" untuk memilih folder atau file yang akan dianalisis.
         <img width="1210" height="595" alt="image" src="https://github.com/user-attachments/assets/3b1f374e-211a-4b27-ad03-ce5eadebfa3c" />

      3. Path yang dipilih akan muncul di kolom isian.

    Langkah 2: Mulai Deteksi
      1. Klik tombol "🚀 Mulai Deteksi" (bootstyle: info).

      2. Aplikasi akan:

          - Menghitung hash (MD5 dan SHA256), mendapatkan metadata (ukuran, waktu dibuat/modifikasi), dan mendeteksi tipe asli file berdasarkan magic number untuk setiap file.
          
          - Membandingkan Ekstensi Tertulis (dari nama file) dengan Ekstensi Asli (dari tipe file).
          
          = Menampilkan status: Normal, Tersamar! (jika ekstensi berbeda), atau Tidak Dikenali.

    Langkah 3: Meninjau Hasil
      1. Tabel Hasil (Sisi Kiri):

          - Semua file yang dianalisis akan ditampilkan di Treeview ini.
          
          - Perhatikan kolom "Status" untuk melihat file yang Tersamar! atau Tidak Dikenali.
            
      2. Laporan PDF (Sisi Kanan):

          - Setelah pemindaian selesai, aplikasi secara otomatis membuat laporan PDF di folder reports/.
          
          - Laporan berisi ringkasan, tabel hasil lengkap, dan detail metadata untuk file yang Tersamar! atau Tidak Dikenali.
          
          - Pratinjau Laporan: Pratinjau PDF akan ditampilkan di sisi kanan. Anda bisa menavigasi halaman menggunakan tombol "⬅️ Sebelumnya" dan "➡️ Berikutnya".

      3. Membuka Laporan:

          - Klik tombol "📂 Buka Laporan di Aplikasi Lain" untuk membuka file PDF dengan viewer PDF bawaan sistem Anda

      Fitur Tambahan
          - Progress Bar: Saat memindai folder, progress bar dan label loading akan menunjukkan perkembangan analisis file.
          - Ganti Tema: Tombol "🌗 Ganti Tema" akan mengganti tema tampilan antara light (flatly) dan dark (darkly).

Output Gambar:
<img width="1006" height="595" alt="image" src="https://github.com/user-attachments/assets/f5393d46-d0c4-48df-b1c2-dfc834264fc6" />
