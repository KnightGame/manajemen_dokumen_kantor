'''
utils.py - Fungsi Utilitas Sistem Manajemen Dokumen QR Code
File ini berisi semua fungsi pendukung yang dipanggil dari main.py
Dipisahkan untuk menjaga kode tetap modular dan terorganisir

CATATAN: Beberapa fitur masih dalam pengembangan:
- Scan QR Code - DALAM PENGEMBANGAN
- Kelola QR / Generate Batch - DALAM PENGEMBANGAN
- Laporan (Grafik, Export, Backup) - DALAM PENGEMBANGAN

IMPORT LIBRARY
'''
import pandas as pd                     # untuk manipulasi data
import qrcode                           # generate QR code (untuk preview di Data Master)
import os                               # operasi file dan folder
from datetime import datetime           # tanggal dan waktu

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
                 'role']        # peran user (admin/staff/user)

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


# ============================================
# FUNGSI LOAD & SAVE DATA
# ============================================
def load_data(file_path):
    """
    Muat data dari file CSV dengan penanganan error yang lebih baik
    
    Parameter:
    - file_path: path ke file CSV yang akan dibaca
    
    Return:
    - DataFrame berisi data dari file CSV, atau DataFrame kosong jika gagal
    """
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
    """
    Simpan DataFrame ke file CSV
    
    Parameter:
    - file_path: path ke file CSV tujuan
    - df: DataFrame yang akan disimpan
    
    Return:
    - True jika berhasil, False jika gagal
    
    DIPERBAIKI: Menambahkan try-except untuk penanganan error
    """
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


# ============================================
# FUNGSI INISIALISASI
# ============================================
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
    """
    Inisialisasi file master dokumen
    
    Parameter:
    - file_path: path ke file CSV master
    
    Return:
    - DataFrame dari file master (kosong jika baru dibuat)
    """
    if not os.path.exists(file_path):
        # file belum ada, buat baru dengan kolom yang sudah didefinisikan
        df = pd.DataFrame(columns=COLUMNS_MASTER)
        save_data(file_path, df)
    return load_data(file_path)


def init_log_csv(file_path):
    """
    Inisialisasi file log aktivitas
    
    Parameter:
    - file_path: path ke file CSV log
    
    Return:
    - DataFrame dari file log (kosong jika baru dibuat)
    """
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=COLUMNS_LOG)
        save_data(file_path, df)
    return load_data(file_path)


def init_users_csv(file_path):
    """
    Inisialisasi file users dengan default users (admin, staff, viewer)
    
    Parameter:
    - file_path: path ke file CSV users
    
    Return:
    - DataFrame dari file users
    """
    if not os.path.exists(file_path):
        # Buat user default: admin, staff, viewer
        df = pd.DataFrame({
            'username': ['admin', 'staff', 'viewer'],
            'password': ['admin123', 'staff123', 'viewer123'],
            'role': ['admin', 'staff', 'viewer']
        })
        save_data(file_path, df)
    return load_data(file_path)


# ============================================
# FUNGSI GENERATE ID
# ============================================
def generate_id_dokumen(df):
    """
    Generate ID dokumen baru dengan format DOC001, DOC002, dst
    
    Parameter:
    - df: DataFrame master dokumen
    
    Return:
    - string ID baru (contoh: "DOC001", "DOC002", dst)
    """
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
    """
    Generate ID log baru (auto increment)
    
    Parameter:
    - df: DataFrame log aktivitas
    
    Return:
    - integer ID log baru
    """
    if len(df) == 0 or 'ID_Log' not in df.columns:
        return 1    # mulai dari 1
    try:
        # Ambil ID_Log terbesar dan tambah 1
        return int(df['ID_Log'].max()) + 1
    except:
        return len(df) + 1


# ============================================
# FUNGSI CRUD DOKUMEN
# ============================================
def tambah_dokumen(file_path, data):
    """
    Tambah dokumen baru ke database
    
    Parameter:
    - file_path: path ke file CSV master
    - data: dictionary berisi judul, jenis, lokasi, status, keterangan
    
    Return:
    - new_id: ID dokumen yang baru dibuat
    """
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
    """
    Ambil dokumen berdasarkan ID
    
    Parameter:
    - file_path: path ke file CSV master
    - id_dokumen: ID dokumen yang dicari
    
    Return:
    - dictionary data dokumen atau None jika tidak ditemukan
    """
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
    """
    Update dokumen berdasarkan ID
    
    Parameter:
    - file_path: path ke file CSV master
    - id_dokumen: ID dokumen yang akan diupdate
    - data: dictionary berisi kolom dan nilai baru
    
    Return:
    - True jika berhasil, False jika gagal
    """
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
    """
    Hapus dokumen berdasarkan ID (tanpa menghapus file QR)
    
    Parameter:
    - file_path: path ke file CSV master
    - id_dokumen: ID dokumen yang akan dihapus
    
    Return:
    - True jika berhasil, False jika gagal
    
    CATATAN: Logika penghapusan file QR dihapus karena fitur Kelola QR
    masih dalam pengembangan
    """
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
    """
    Ambil semua dokumen dari database
    
    Parameter:
    - file_path: path ke file CSV master
    
    Return:
    - DataFrame berisi semua dokumen
    """
    return load_data(file_path)


# ============================================
# FUNGSI LOG AKTIVITAS
# ============================================
def tambah_log(file_path, id_dokumen, aksi, user="Admin"):
    """
    Tambah log aktivitas
    
    Parameter:
    - file_path: path ke file CSV log
    - id_dokumen: ID dokumen terkait
    - aksi: jenis aksi (CREATE, UPDATE, DELETE, dll)
    - user: username yang melakukan aksi
    """
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
    """
    Ambil semua log aktivitas
    
    Parameter:
    - file_path: path ke file CSV log
    
    Return:
    - DataFrame berisi semua log aktivitas
    """
    return load_data(file_path)


# ============================================
# FUNGSI QR CODE (DASAR - untuk Preview di Data Master)
# ============================================
def generate_qr_code(data, output_path):
    """
    Generate QR Code dan simpan ke file
    
    Parameter:
    - data: data yang akan di-encode ke QR code (biasanya ID dokumen)
    - output_path: path file output untuk menyimpan gambar QR
    
    Return:
    - output_path: path file yang sudah disimpan
    
    CATATAN: Fungsi ini digunakan untuk generate QR saat tambah dokumen
    di halaman Data Master. Fitur Kelola QR (batch generate, download, dll)
    masih dalam pengembangan.
    """
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


# ============================================
# FUNGSI STATISTIK (untuk Dashboard)
# ============================================
def get_statistik(file_path):
    """
    Ambil statistik dokumen untuk dashboard
    
    Parameter:
    - file_path: path ke file CSV master
    
    Return:
    - dictionary berisi total, per_jenis, per_status, per_lokasi
    """
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
    """
    Ambil dokumen terbaru untuk dashboard
    
    Parameter:
    - file_path: path ke file CSV master
    - limit: jumlah dokumen yang diambil (default 5)
    
    Return:
    - DataFrame berisi n dokumen terbaru
    """
    df = load_data(file_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    # tail() ambil n baris terakhir, iloc[::-1] balik urutan
    return df.tail(limit).iloc[::-1]


def get_log_terbaru(file_path, limit=5):
    """
    Ambil log aktivitas terbaru untuk dashboard
    
    Parameter:
    - file_path: path ke file CSV log
    - limit: jumlah log yang diambil (default 5)
    
    Return:
    - DataFrame berisi n log terbaru
    """
    df = load_data(file_path)
    if len(df) == 0:
        return pd.DataFrame()
    
    return df.tail(limit).iloc[::-1]


# ============================================
# FUNGSI PENCARIAN & FILTER
# ============================================
def cari_dokumen(file_path, keyword):
    """
    Cari dokumen berdasarkan keyword
    
    Parameter:
    - file_path: path ke file CSV master
    - keyword: kata kunci pencarian
    
    Return:
    - DataFrame hasil pencarian
    """
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
    """
    Filter dokumen berdasarkan kolom dan nilai tertentu
    
    Parameter:
    - file_path: path ke file CSV master
    - kolom: nama kolom untuk filter
    - nilai: nilai yang dicari
    
    Return:
    - DataFrame hasil filter
    """
    df = load_data(file_path)
    if len(df) == 0 or kolom not in df.columns:
        return df
    
    # Jika nilai adalah "Semua", kembalikan semua data
    if nilai == "Semua":
        return df
    
    # Filter data berdasarkan kolom dan nilai
    return df[df[kolom] == nilai]


# ============================================
# FUNGSI LOGIN & USER
# ============================================
def validasi_login(file_path, username, password):
    """
    Validasi login user
    
    Parameter:
    - file_path: path ke file CSV users
    - username: username yang diinput
    - password: password yang diinput
    
    Return:
    - dictionary berisi valid (bool), username, role, message
    """
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
    """
    Tambah user baru
    
    Parameter:
    - file_path: path ke file CSV users
    - username: username baru
    - password: password baru
    - role: role user (admin/staff/viewer)
    
    Return:
    - True jika berhasil, False jika username sudah ada
    """
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


# ============================================
# FUNGSI UTILITAS
# ============================================
def get_file_size(file_path):
    """
    Ambil ukuran file dalam format yang mudah dibaca
    
    Parameter:
    - file_path: path ke file
    
    Return:
    - string ukuran file (contoh: "1.5 KB")
    """
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
