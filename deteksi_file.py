import os
import hashlib
import datetime
import filetype
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X
from pdf2image import convert_from_path
from PIL import ImageTk, Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# =====================================================
# UTILITAS
# =====================================================
def hitung_hash(filepath, mode='md5'):
    h = hashlib.md5() if mode == 'md5' else hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def dapatkan_metadata(filepath):
    stat = os.stat(filepath)
    return {
        "Ukuran (bytes)": stat.st_size,
        "Waktu Dibuat": datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "Waktu Modifikasi": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "Hash MD5": hitung_hash(filepath, 'md5'),
        "Hash SHA256": hitung_hash(filepath, 'sha256')
    }

def deteksi_tipe_asli(filepath):
    kind = filetype.guess(filepath)
    if kind is None:
        return None, None
    return kind.mime, kind.extension

def analisis_file(filepath):
    nama_file = os.path.basename(filepath)
    ekstensi_tertulis = os.path.splitext(nama_file)[1].lower().replace('.', '')
    mime_asli, ekstensi_asli = deteksi_tipe_asli(filepath)

    if ekstensi_asli is None:
        status = "Tidak Dikenali"
    elif ekstensi_tertulis != ekstensi_asli:
        status = "Tersamar!"
    else:
        status = "Normal"

    metadata = dapatkan_metadata(filepath)
    return {
        "nama_file": nama_file,
        "ekstensi_tertulis": ekstensi_tertulis if ekstensi_tertulis else "(tidak ada)",
        "ekstensi_asli": ekstensi_asli if ekstensi_asli else "(tidak diketahui)",
        "status": status,
        "metadata": metadata
    }

def analisis_folder(path_folder, progress_callback=None):
    hasil = []
    semua_file = []
    for root, _, files in os.walk(path_folder):
        for f in files:
            semua_file.append(os.path.join(root, f))

    total_file = len(semua_file)
    for i, filepath in enumerate(semua_file, 1):
        hasil.append(analisis_file(filepath))
        if progress_callback:
            progress_callback(i, total_file)
    return hasil


# =====================================================
# LAPORAN PDF
# =====================================================
def buat_laporan_pdf(hasil):
    os.makedirs("reports", exist_ok=True)
    waktu = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join("reports", f"laporan_deteksi_{waktu}.pdf")

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Laporan Deteksi Penyamaran File</b>", styles['Title']))
    story.append(Spacer(1, 12))

    total = len(hasil)
    tersamar = sum(1 for x in hasil if x['status'] == "Tersamar!")
    tidak_dikenali = sum(1 for x in hasil if x['status'] == "Tidak Dikenali")
    story.append(Paragraph(f"Total file diperiksa: {total}", styles['Normal']))
    story.append(Paragraph(f"File tersamar: {tersamar}", styles['Normal']))
    story.append(Paragraph(f"File tidak dikenali: {tidak_dikenali}", styles['Normal']))
    story.append(Spacer(1, 12))

    data = [["Nama File", "Ekstensi Tertulis", "Ekstensi Asli", "Status"]]
    for x in hasil:
        data.append([x["nama_file"], x["ekstensi_tertulis"], x["ekstensi_asli"], x["status"]])

    table = Table(data, colWidths=[180, 120, 120, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Detail Metadata File Tersamar / Tidak Dikenali</b>", styles['Heading2']))
    for x in hasil:
        if x['status'] in ("Tersamar!", "Tidak Dikenali"):
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>{x['nama_file']}</b>", styles['Heading3']))
            for k, v in x['metadata'].items():
                story.append(Paragraph(f"{k}: {v}", styles['Normal']))

    doc.build(story)
    return output_path


# =====================================================
# GUI
# =====================================================
class DeteksiApp:
    def __init__(self, root):
        self.root = root
        self.style = Style(theme="flatly")
        self.mode = "light"
        self.root.title("🔍 Deteksi Penyamaran File")
        self.root.geometry("1300x750")
        self.laporan_path = None
        self.pages = []
        self.current_page_index = 0

        self.var_mode = tk.StringVar(value="folder")
        self.progress_var = tk.IntVar()
        self.loading_text = tk.StringVar(value="")

        self.buat_gui()

    def buat_gui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Kiri: Upload dan tabel hasil
        frame_kiri = ttk.Frame(main_frame)
        frame_kiri.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))

        # Kanan: PDF Preview
        frame_kanan = ttk.Frame(main_frame)
        frame_kanan.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

        # ======== BAGIAN KIRI ========
        frame_top = ttk.Frame(frame_kiri, padding=10)
        frame_top.pack(fill=X)
        ttk.Label(frame_top, text="🧭 Pilih Target:", font=("Poppins", 11, "bold")).pack(side=LEFT, padx=5)
        ttk.Radiobutton(frame_top, text="Folder", variable=self.var_mode, value="folder").pack(side=LEFT, padx=5)
        ttk.Radiobutton(frame_top, text="File", variable=self.var_mode, value="file").pack(side=LEFT, padx=5)
        ttk.Button(frame_top, text="🌗 Ganti Tema", command=self.toggle_theme, bootstyle="secondary-outline").pack(side=RIGHT, padx=5)

        frame_path = ttk.Frame(frame_kiri, padding=10)
        frame_path.pack(fill=X)
        self.entry_path = ttk.Entry(frame_path, width=70)
        self.entry_path.pack(side=LEFT, padx=5)
        ttk.Button(frame_path, text="Browse", command=self.pilih_target, bootstyle="success").pack(side=LEFT)

        self.btn_scan = ttk.Button(frame_kiri, text="🚀 Mulai Deteksi", command=self.mulai_deteksi_thread, bootstyle="info", width=25)
        self.btn_scan.pack(pady=10)

        self.progress_bar = ttk.Progressbar(frame_kiri, variable=self.progress_var, maximum=100, length=500)
        self.progress_bar.pack(pady=5)
        self.lbl_loading = ttk.Label(frame_kiri, textvariable=self.loading_text, font=("Poppins", 10, "italic"))
        self.lbl_loading.pack()

        columns = ("Nama File", "Ekstensi Tertulis", "Ekstensi Asli", "Status")
        self.tree = ttk.Treeview(frame_kiri, columns=columns, show="headings", height=18)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="w", stretch=True)
        self.tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

        # ======== BAGIAN KANAN ========
        self.frame_pdf = ttk.Labelframe(frame_kanan, text="📄 Preview Laporan PDF", padding=10)
        self.frame_pdf.pack(fill=BOTH, expand=True)

        self.label_pdf = ttk.Label(self.frame_pdf, text="Belum ada laporan untuk ditampilkan.")
        self.label_pdf.pack(expand=True)

        nav_frame = ttk.Frame(frame_kanan)
        nav_frame.pack(pady=5)
        self.btn_prev = ttk.Button(nav_frame, text="⬅️ Sebelumnya", command=self.prev_page, state="disabled")
        self.btn_prev.pack(side=LEFT, padx=5)
        self.lbl_page_info = ttk.Label(nav_frame, text="Halaman 0/0")
        self.lbl_page_info.pack(side=LEFT, padx=5)
        self.btn_next = ttk.Button(nav_frame, text="➡️ Berikutnya", command=self.next_page, state="disabled")
        self.btn_next.pack(side=LEFT, padx=5)

        self.btn_open_pdf = ttk.Button(frame_kanan, text="📂 Buka Laporan di Aplikasi Lain", command=self.buka_laporan, bootstyle="primary")
        self.btn_open_pdf.pack(pady=10)

        ttk.Label(frame_kanan, text="© 2025 File Analyzer | Dibuat dengan Python", font=("Poppins", 9)).pack(pady=5)

    def pilih_target(self):
        if self.var_mode.get() == "folder":
            path = filedialog.askdirectory(title="Pilih Folder yang Akan Diperiksa")
        else:
            path = filedialog.askopenfilename(title="Pilih File yang Akan Diperiksa")
        if path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)

    def toggle_theme(self):
        self.style.theme_use("darkly" if self.mode == "light" else "flatly")
        self.mode = "dark" if self.mode == "light" else "light"
        if hasattr(self, "pages") and self.pages:
            self.show_pdf_page()

    def update_progress(self, current, total):
        self.progress_var.set(int((current / total) * 100))
        self.loading_text.set(f"Scanning... ({current}/{total}) file")
        self.root.update_idletasks()

    def mulai_deteksi_thread(self):
        threading.Thread(target=self.mulai_deteksi).start()

    def mulai_deteksi(self):
        path = self.entry_path.get().strip()
        if not path:
            messagebox.showwarning("Peringatan", "Silakan pilih target terlebih dahulu!")
            return
        if not os.path.exists(path):
            messagebox.showerror("Error", "Path tidak ditemukan!")
            return

        self.progress_var.set(0)
        self.btn_scan.config(state="disabled")
        self.loading_text.set("Sedang menganalisis...")

        if self.var_mode.get() == "folder":
            hasil = analisis_folder(path, progress_callback=self.update_progress)
        else:
            hasil = [analisis_file(path)]
            self.update_progress(1, 1)

        self.loading_text.set("Membuat laporan PDF...")
        self.tampilkan_hasil(hasil)
        self.laporan_path = buat_laporan_pdf(hasil)
        self.tampilkan_pdf(self.laporan_path)

        self.loading_text.set("Selesai ✅")
        self.progress_var.set(100)
        self.btn_scan.config(state="normal")

    def tampilkan_hasil(self, hasil):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for x in hasil:
            self.tree.insert("", "end", values=(x["nama_file"], x["ekstensi_tertulis"], x["ekstensi_asli"], x["status"]))

    def tampilkan_pdf(self, path_pdf):
        for widget in self.frame_pdf.winfo_children():
            widget.destroy()

        try:
            self.pages = convert_from_path(path_pdf, poppler_path=r"C:\poppler\Library\bin")
            self.current_page_index = 0
            self.show_pdf_page()
            self.update_nav_buttons()
        except Exception as e:
            ttk.Label(self.frame_pdf, text=f"Gagal menampilkan preview: {e}").pack()

    def show_pdf_page(self):
        if not self.pages:
            return
        for w in self.frame_pdf.winfo_children():
            w.destroy()

        page = self.pages[self.current_page_index]
        frame_w, frame_h = self.frame_pdf.winfo_width(), self.frame_pdf.winfo_height()
        page.thumbnail((frame_w * 0.9, frame_h * 0.9))
        img = ImageTk.PhotoImage(page)
        label_img = ttk.Label(self.frame_pdf, image=img)
        label_img.image = img
        label_img.pack(expand=True)
        self.lbl_page_info.config(text=f"Halaman {self.current_page_index+1}/{len(self.pages)}")

    def update_nav_buttons(self):
        self.btn_prev.config(state="normal" if self.current_page_index > 0 else "disabled")
        self.btn_next.config(state="normal" if self.current_page_index < len(self.pages)-1 else "disabled")

    def next_page(self):
        if self.current_page_index < len(self.pages)-1:
            self.current_page_index += 1
            self.show_pdf_page()
            self.update_nav_buttons()

    def prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.show_pdf_page()
            self.update_nav_buttons()

    def buka_laporan(self):
        if self.laporan_path and os.path.exists(self.laporan_path):
            webbrowser.open_new(self.laporan_path)
        else:
            messagebox.showwarning("Tidak ditemukan", "Laporan belum dibuat atau file hilang.")


# =====================================================
# Jalankan Aplikasi
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DeteksiApp(root)
    root.mainloop()
