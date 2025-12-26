'''
utils.py - Fungsi Utilitas Sistem Manajemen Dokumen QR Code
File ini berisi semua fungsi pendukung yang dipanggil dari main.py
Dipisahkan untuk menjaga kode tetap modular dan terorganisir
IMPORT LIBRARY
'''
import pandas as pd                     # untuk manipulasi data
import numpy as np                      # operasi array (untuk QR code scanning)
import qrcode                           # generate QR code
import cv2                              # baca gambar dan scan QR code
import os                               # operasi file dan folder
import shutil                           # operasi file dan folder
import zipfile                          # buat file ZIP untuk backup
from datetime import datetime           # tanggal dan waktu
from pyzbar.pyzbar import decode        # scan QR code dari gambar
from PIL import Image                   # manipulasi gambar
import plotly.graph_objects as go       # buat grafik

'''
KONSTANTA: adalah nilai tetap yang tidak berubah selama program berjalan
'''
COLUMNS_MASTER = ['ID',             # ID dokumen
                  'Judul',          # judul dokumen
                  'Jenis',          # jenis dokumen
                  'Lokasi_Fisik',   # lokasi fisik dokumen
                  'Tanggal_Upload', # tanggal dan waktu upload
                  'Keterangan',     # keterangan tambahan
                  'Status',         # status dokumen
                  'QR_Path']        # path file QR code

COLUMNS_LOG = ['ID_Log',        # ID log
               'ID_Dokumen',    # ID dokumen terkait
               'Aksi',          # aksi yang dilakukan
               'Waktu',         # tanggal dan waktu aksi
               'User']          # user yang melakukan aksi

COLUMNS_USERS = ['username',    # username untuk login
                 'password',    # password untuk login
                 'role']        # peran user (admin/staff)

JENIS_DOKUMEN = [
    "Surat Masuk", 
    "Surat Keluar", 
    "Laporan", 
    "Proposal", 
    "Kontrak", 
    "MoU", 
    "SK/Keputusan", 
    "Notulen", 
    "Memo", 
    "Lainnya"
]

STATUS_DOKUMEN = [
    "Aktif",          # dokumen aktif dan dapat diakses
    "Arsip",          # dokumen sudah diarsipkan
    "Dipinjam",       # dokumen sedang dipinjam
    "Dalam Proses",   # dokumen sedang diproses
    "Selesai"         # dokumen sudah selesai diproses
]

LOKASI_LIST = [
    "Rak A - Lantai 1", 
    "Rak B - Lantai 1", 
    "Rak C - Lantai 1", 
    "Rak A - Lantai 2", 
    "Rak B - Lantai 2", 
    "Lemari Arsip 1", 
    "Lemari Arsip 2", 
    "Brankas", 
    "Ruang Khusus"
]

# Warna untuk grafik
CHART_COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', 
                '#ef4444', '#ec4899', '#3b82f6', '#84cc16', '#f97316', '#6366f1']

# FUNGSI LOAD & SAVE DATA
def load_data(file_path):
    # Muat data dari file CSV dengan penanganan error yang lebih baik
    if os.path.exists(file_path):
        try:
            # Baca file CSV dengan pandas
            df = pd.read_csv(file_path, 
                             sep=';',               # gunakan pemisah titik koma
                             encoding='utf-8-sig')  # encoding UTF-8 dengan BOM
            # PERBAIKAN: Pastikan kolom ID adalah string jika ada
            if 'ID' in df.columns:
                df['ID'] = df['ID'].astype(str).str.strip()
            return df
        except Exception as e:
            # jika gagal, kembalikan DataFrame kosong
            print(f"Error loading {file_path}: {e}")
            return pd.DataFrame()
    
    # jika file tidak ada, kembalikan DataFrame kosong
    return pd.DataFrame()


def save_data(file_path, df):
    '''
    Simpan DataFrame ke file CSV
    DIPERBAIKI: Menambahkan try-except untuk penanganan error
    '''
    try:
        # Buat folder jika belum ada
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        
        # Simpan DataFrame ke file CSV dengan pandas
        df.to_csv(file_path,
                  index=False,          # tanpa index
                  sep=';',              # gunakan pemisah titik koma
                  encoding='utf-8-sig') # encoding UTF-8 dengan BOM
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

# FUNGSI INISIALISASI
def init_folders():
    """
    Buat folder yang diperlukan
    ---------------------------
    Folder yang dibuat:
    - data/: untuk menyimpan file data CSV 
    - qr/: untuk menyimpan file QR code
    """
    os.makedirs("data", exist_ok=True)  # buat folder data jika belum ada
    os.makedirs("qr", exist_ok=True)    # buat folder qr jika belum ada


def init_master_csv(file_path):
    # Inisialisasi file master dokumen
    if not os.path.exists(file_path):
        # file belum ada, buat baru dengan kolom yang sudah didefinisikan
        df = pd.DataFrame(columns=COLUMNS_MASTER)
        save_data(file_path, df)
    return load_data(file_path)


def init_log_csv(file_path):
    # Inisialisasi file log aktivitas
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=COLUMNS_LOG)
        save_data(file_path, df)
    return load_data(file_path)


def init_users_csv(file_path):
    """
    Inisialisasi file users dengan default users (admin, staff)
    """
    if not os.path.exists(file_path):
        # Buat user default: admin, staff
        df = pd.DataFrame({
            'username': ['admin', 'staff'],
            'password': ['admin123', 'staff123'],
            'role': ['admin', 'staff']
        })
        save_data(file_path, df)
    return load_data(file_path)

# FUNGSI GENERATE ID
def generate_id_dokumen(df):
    # Generate ID dokumen baru
    if len(df) == 0 or 'ID' not in df.columns:
        return "DOC001"
    
    try:
        # PERBAIKAN: Pastikan ID adalah string
        df['ID'] = df['ID'].astype(str).str.strip()
        
        # Ambil ID terakhir (bukan kosong)
        last_id = df['ID'].dropna().iloc[-1] if len(df['ID'].dropna()) > 0 else "DOC000"
        
        # Ekstrak nomor dari ID terakhir dan tambah 1
        num = int(str(last_id).replace("DOC", "")) + 1
        
        # Format kembali dengan 3 digit
        return f"DOC{num:03d}"
    except:
        # Jika ada error, gunakan panjang df + 1
        return f"DOC{len(df)+1:03d}"


def generate_id_log(df):
    # Generate ID log baru
    if len(df) == 0 or 'ID_Log' not in df.columns:
        return 1    # mulai dari 1
    try:
        # Ambil ID_Log terbesar dan tambah 1
        return int(df['ID_Log'].max()) + 1
    except:
        return len(df) + 1

# FUNGSI CRUD DOKUMEN
def tambah_dokumen(file_path, data):
    # Tambah dokumen baru ke database
    # Muat data master
    df = load_data(file_path)
    
    # Buat ID dokumen baru
    new_id = generate_id_dokumen(df)
    qr_path = f"qr/{new_id}.png"    # path file QR code
    
    # Buat dictionary dokumen baru
    # PERBAIKAN: Menambahkan strip() untuk menghilangkan whitespace
    dokumen_baru = {
        'ID': new_id,
        'Judul': str(data.get('judul', '')).strip(),
        'Jenis': str(data.get('jenis', '')).strip(),
        'Lokasi_Fisik': str(data.get('lokasi', '')).strip(),
        'Tanggal_Upload': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Keterangan': str(data.get('keterangan', '')).strip(),
        'Status': str(data.get('status', 'Aktif')).strip(),
        'QR_Path': qr_path
    }
    
    # Konversi ke DataFrame 1 baris
    df_baru = pd.DataFrame([dokumen_baru])
    
    # Gabungkan dengan data master
    if len(df) == 0:
        df = df_baru
    else:
        df = pd.concat([df, df_baru], ignore_index=True)
    
    # Simpan data dan generate QR code
    save_data(file_path, df)
    generate_qr_code(new_id, qr_path)
    
    return new_id   # kembalikan ID dokumen baru untuk ditampilkan ke user


def get_dokumen_by_id(file_path, id_dokumen):
    # Ambil dokumen berdasarkan ID
    df = load_data(file_path)
    
    # Cek apakah ada data dan kolom ID
    if len(df) == 0 or 'ID' not in df.columns:
        return None
    
    # PERBAIKAN: Konversi ke string untuk perbandingan yang konsisten
    id_dokumen = str(id_dokumen).strip()
    df['ID'] = df['ID'].astype(str).str.strip()
    
    # Filter data berdasarkan ID
    result = df[df['ID'] == id_dokumen]
    
    if len(result) > 0:
        # Ambil baris pertama dan konversi ke dictionary
        return result.iloc[0].to_dict()
    return None


def update_dokumen(file_path, id_dokumen, data):
    # Update dokumen berdasarkan ID
    df = load_data(file_path)
    if len(df) == 0 or 'ID' not in df.columns:
        return False
    
    # PERBAIKAN: Konversi ke string
    id_dokumen = str(id_dokumen).strip()
    df['ID'] = df['ID'].astype(str).str.strip()
    
    # Cari index dokumen berdasarkan ID
    idx = df[df['ID'] == id_dokumen].index
    
    if len(idx) > 0:
        # Update kolom yang ada di data
        for key, value in data.items():
            if key in df.columns:
                df.loc[idx[0], key] = value
        # Simpan data
        save_data(file_path, df)
        return True
    return False


def hapus_dokumen(file_path, id_dokumen):
    # Hapus dokumen berdasarkan ID
    df = load_data(file_path)
    if len(df) == 0 or 'ID' not in df.columns:
        return False
    
    # Konversi ID ke string dan strip whitespace
    id_dokumen = str(id_dokumen).strip()
    
    # Pastikan kolom ID juga string
    df['ID'] = df['ID'].astype(str).str.strip()
    
    # Cek apakah ID ada di database
    if id_dokumen not in df['ID'].values:
        print(f"ID {id_dokumen} tidak ditemukan di database")
        return False  # ID tidak ditemukan
    
    # Simpan jumlah data sebelum hapus untuk validasi
    jumlah_sebelum = len(df)
    
    # Hapus file QR terlebih dahulu jika ada
    qr_path = f"qr/{id_dokumen}.png"
    if os.path.exists(qr_path):
        try:
            os.remove(qr_path)
        except Exception as e:
            print(f"Warning: Gagal menghapus QR file: {e}")
    
    # Filter dengan perbandingan string yang benar
    df_filtered = df[df['ID'] != id_dokumen].copy()
    
    # Validasi - pastikan hanya 1 data yang terhapus
    jumlah_sesudah = len(df_filtered)
    jumlah_terhapus = jumlah_sebelum - jumlah_sesudah
    
    if jumlah_terhapus != 1:
        # Sesuatu yang salah terjadi
        print(f"Warning: Expected 1 deletion, got {jumlah_terhapus}")
        
        # Jika tidak ada yang terhapus, return False
        if jumlah_terhapus == 0:
            return False
        
        # Jika lebih dari 1 terhapus, ini bug serius - jangan simpan!
        if jumlah_terhapus > 1:
            print("CRITICAL: Multiple deletions detected, aborting save!")
            return False
    
    # Simpan data yang sudah difilter
    save_data(file_path, df_filtered)
    return True


def get_semua_dokumen(file_path):
    # Ambil semua dokumen dari database
    return load_data(file_path)

# FUNGSI LOG AKTIVITAS
def tambah_log(file_path, id_dokumen, aksi, user="Admin"):
    # Tambah log aktivitas
    df = load_data(file_path)
    
    # Buat dictionary log baru
    log_baru = {
        'ID_Log': generate_id_log(df),
        'ID_Dokumen': str(id_dokumen).strip(),  # PERBAIKAN: strip whitespace
        'Aksi': aksi,
        'Waktu': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'User': user
    }
    
    # Konversi ke DataFrame dan gabungkan
    df_baru = pd.DataFrame([log_baru])
    
    if len(df) == 0:
        df = df_baru
    else:
        df = pd.concat([df, df_baru], ignore_index=True)
    
    save_data(file_path, df)


def get_semua_log(file_path):
    # Ambil semua log aktivitas
    return load_data(file_path)

# FUNGSI QR CODE
def generate_qr_code(data, output_path):
    # Generate QR Code dan simpan ke file

    # Buat folder jika belum ada
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Buat objek QR Code
    qr = qrcode.QRCode(
        version=1,                                          # ukuran QR code (1 = paling kecil)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # tingkat koreksi kesalahan
        box_size=10,                                        # ukuran tiap kotak dalam pixel
        border=4                                            # lebar border dalam kotak
    )
    
    # Tambahkan data ke QR code
    qr.add_data(data)
    qr.make(fit=True)   # sesuaikan ukuran QR code dengan data
    
    # Buat gambar QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Simpan gambar ke file
    img.save(output_path)
    
    return output_path


def scan_qr_code(image_file):
    # Scan QR Code dari file gambar (upload atau camera input)
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None, "Tidak dapat mengakses kamera"
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Decode QR Code
            decoded_objects = decode(frame)
            
            for obj in decoded_objects:
                # Ambil data dari QR Code
                qr_data = obj.data.decode('utf-8')
                cap.release()
                cv2.destroyAllWindows()
                return qr_data, "Berhasil scan QR Code"
            
            # Tampilkan frame
            cv2.imshow('Scan QR Code - Tekan Q untuk keluar', frame)
            
            # Tekan 'q' untuk keluar
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return None, "Scan dibatalkan"
        
    except Exception as e:
        return None, f"Error: {str(e)}"


def generate_qr_batch(file_path, output_folder):
    # Generate QR Code untuk semua dokumen sekaligus
    df = load_data(file_path)
    os.makedirs(output_folder, exist_ok=True)
    
    generated = []
    
    # Loop tiap baris dokumen
    for _, row in df.iterrows():
        if 'ID' in row:
            qr_path = f"{output_folder}/{row['ID']}.png"
            generate_qr_code(row['ID'], qr_path)
            generated.append(row['ID'])
    
    return generated

# FUNGSI STATISTIK
def get_statistik(file_path):
    # Ambil statistik dokumen
    df = load_data(file_path)
    
    # Return statistik kosong jika data kosong
    if len(df) == 0:
        return {
            'total': 0,
            'per_jenis': {},
            'per_status': {},
            'per_lokasi': {}
        }
    
    # Hitung statistik menggunakan value_counts()
    # value_counts() menghitung frekuensi setiap nilai unik
    # to_dict() mengkonversi ke dictionary
    stats = {
        'total': len(df),
        'per_jenis': df['Jenis'].value_counts().to_dict() if 'Jenis' in df.columns else {},
        'per_status': df['Status'].value_counts().to_dict() if 'Status' in df.columns else {},
        'per_lokasi': df['Lokasi_Fisik'].value_counts().to_dict() if 'Lokasi_Fisik' in df.columns else {}
    }
    
    return stats


def get_dokumen_terbaru(file_path, limit=5):
    # Ambil dokumen terbaru
    df = load_data(file_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    # tail() ambil n baris terakhir, iloc[::-1] balik urutan
    return df.tail(limit).iloc[::-1]


def get_log_terbaru(file_path, limit=5):
    # Ambil log aktivitas terbaru
    df = load_data(file_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    return df.tail(limit).iloc[::-1]

# FUNGSI GRAFIK
def buat_pie_chart(df, kolom, judul):
    # Buat pie chart (donut chart)
    if len(df) == 0 or kolom not in df.columns:
        return None
    
    # Hitung frekuensi nilai di kolom
    data = df[kolom].value_counts()
    if len(data) == 0:
        return None
    
    # Buat pie chart menggunakan Plotly
    fig = go.Figure(data=[go.Pie(
        labels=data.index.tolist(),                     # label dari nilai unik
        values=data.values.tolist(),                    # nilai dari frekuensi
        hole=0.4,                                       # buat donut chart (lubang di tengah)
        marker=dict(colors=CHART_COLORS[:len(data)])    # warna chart custom
    )])
    
    # Update layout chart agar sesuai tema gelap
    fig.update_layout(
        title=dict(text=judul, font=dict(color='#fafafa', size=16)),
        paper_bgcolor='#1a1d24',                    # background luar
        plot_bgcolor='#1a1d24',                     # background area plot
        font=dict(color='#fafafa'),                 # warna teks
        legend=dict(font=dict(color='#fafafa')),    # warna legend
        margin=dict(l=20, r=20, t=50, b=20)         # margin chart
    )
    
    return fig


def buat_bar_chart(df, kolom, judul):
    # Buat bar chart
    if len(df) == 0 or kolom not in df.columns:
        return None
    
    data = df[kolom].value_counts()
    if len(data) == 0:
        return None
    
    # Buat bar chart menggunakan Plotly
    fig = go.Figure(data=[go.Bar(
        x=data.index.tolist(),                          # kategori di sumbu x
        y=data.values.tolist(),                         # nilai di sumbu y
        marker=dict(color=CHART_COLORS[:len(data)])     # warna bar
    )])
    
    # Update layout untuk tema gelap
    fig.update_layout(
        title=dict(text=judul, font=dict(color='#fafafa', size=16)),
        paper_bgcolor='#1a1d24',
        plot_bgcolor='#1a1d24',
        font=dict(color='#fafafa'),
        xaxis=dict(tickfont=dict(color='#b0b8c4'), gridcolor='#2d3139'),    # warna grid sumbu x
        yaxis=dict(tickfont=dict(color='#b0b8c4'), gridcolor='#2d3139'),    # warna grid sumbu y
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def buat_line_chart(df, judul):
    # Buat line chart aktivitas per hari
    if len(df) == 0 or 'Waktu' not in df.columns:
        return None
    
    try:
        # Ekstrak tanggal dari kolom Waktu
        df_temp = df.copy()
        df_temp['Tanggal'] = pd.to_datetime(df_temp['Waktu']).dt.date
        
        # Hitung jumlah aktivitas per tanggal
        data = df_temp.groupby('Tanggal').size()
        
        if len(data) == 0:
            return None
        
        # Buat line chart dengan area fill
        fig = go.Figure(data=[go.Scatter(
            x=data.index.tolist(),
            y=data.values.tolist(),
            mode='lines+markers',           # garis dengan marker titik
            fill='tozeroy',                 # fill area sampai sumbu y = 0
            line=dict(color='#8b5cf6', width=3),
            marker=dict(size=8, color='#8b5cf6')
        )])
        
        fig.update_layout(
            title=dict(text=judul, font=dict(color='#fafafa', size=16)),
            paper_bgcolor='#1a1d24',
            plot_bgcolor='#1a1d24',
            font=dict(color='#fafafa'),
            xaxis=dict(tickfont=dict(color='#b0b8c4'), gridcolor='#2d3139'),
            yaxis=dict(tickfont=dict(color='#b0b8c4'), gridcolor='#2d3139'),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    except:
        return None

# FUNGSI PENCARIAN & FILTER
def cari_dokumen(file_path, keyword):
    # Cari dokumen berdasarkan keyword
    df = load_data(file_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    # Fungsi untuk cek apakah keyword ada di salah satu kolom
    # apply() menerapkan fungsi ke setiap baris
    # lambda row: ... adalah fungsi anonim
    # astype(str) mengkonversi semua nilai ke string
    # str.contains() cek apakah mengandung keyword
    # case=False: tidak case sensitive
    # .any(): True jika ada minimal 1 kolom yang cocok
    mask = df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
    
    return df[mask]     # axis=1 berarti cek per baris


def filter_dokumen(file_path, kolom, nilai):
    # Filter dokumen berdasarkan kolom dan nilai tertentu
    df = load_data(file_path)
    if len(df) == 0 or kolom not in df.columns:
        return df
    
    # Jika nilai adalah "Semua", kembalikan semua data
    if nilai == "Semua":
        return df
    
    # Filter data berdasarkan kolom dan nilai
    return df[df[kolom] == nilai]

# FUNGSI EXPORT & BACKUP
def export_excel(file_path, output_path):
    # Export data ke file Excel
    df = load_data(file_path)
    
    # Buat folder jika belum ada
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Export ke Excel menggunakan openpyxl engine
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    return output_path


def buat_backup(source_folder, backup_name):
    # Buat backup folder ke file ZIP
    backup_path = f"{backup_name}.zip"
    
    # Buat file zip dengan kompresi
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk melalui semua file di folder sumber
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # arcname: nama file di dalam zip relatif terhadap folder sumber
                arcname = os.path.relpath(file_path, source_folder)
                zipf.write(file_path, arcname)
    
    return backup_path

# FUNGSI LOGIN
def validasi_login(file_path, username, password):
    # Validasi login user
    df = load_data(file_path)
    
    if len(df) == 0:
        return {'valid': False, 'message': 'Database user kosong'}
    
    # Cari user dengan username dan password sesuai
    user = df[(df['username'] == username) & (df['password'] == password)]
    
    if len(user) > 0:
        return {
            'valid': True,
            'username': username,
            'role': user.iloc[0]['role'],
            'message': 'Login berhasil'
        }
    
    return {'valid': False, 'message': 'Username atau password salah'}


def tambah_user(file_path, username, password, role):
    # Tambah user baru
    df = load_data(file_path)
    
    # Cek apakah username sudah ada
    if len(df) > 0 and username in df['username'].values:
        return False    # username sudah ada, gagal tambah
    
    # Buat user baru
    user_baru = pd.DataFrame([{
        'username': username,
        'password': password,
        'role': role
    }])
    
    # Gabungkan dengan data user existing
    if len(df) == 0:
        df = user_baru
    else:
        df = pd.concat([df, user_baru], ignore_index=True)
    
    save_data(file_path, df)
    return True

# FUNGSI UTILITAS
def get_file_size(file_path):
    # Ambil ukuran file dalam format yang mudah dibaca
    if not os.path.exists(file_path):
        return "0 B"
    
    # Ambil ukuran file dalam bytes
    size = os.path.getsize(file_path)
    
    # Konversi ke format yang lebih mudah dibaca
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"     # format 1 desimal
        size /= 1024
    
    return f"{size:.1f} TB"