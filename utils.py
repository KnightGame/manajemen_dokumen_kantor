import pandas as pd
import qrcode
import os
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode

# ============= FUNGSI LOAD & SAVE DATA =============

def load_data_dokumen(file_path):
    """
    Memuat data dokumen dari file CSV
    Parameter: file_path (string) - path ke file CSV
    Return: DataFrame pandas
    """
    try:
        if os.path.exists(file_path):
            # Baca dengan delimiter semicolon untuk kompatibilitas Excel
            df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
            return df
        else:
            # Buat DataFrame kosong dengan kolom yang diperlukan
            df = pd.DataFrame(columns=[
                'ID_Dokumen', 'Judul_Dokumen', 'Jenis_Dokumen', 
                'Lokasi_Penyimpanan', 'Tanggal_Input', 'Status', 'Keterangan'
            ])
            df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
            return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=[
            'ID_Dokumen', 'Judul_Dokumen', 'Jenis_Dokumen', 
            'Lokasi_Penyimpanan', 'Tanggal_Input', 'Status', 'Keterangan'
        ])

def save_data_dokumen(file_path, dataframe):
    """
    Menyimpan data dokumen ke file CSV
    Parameter: file_path (string), dataframe (DataFrame)
    Return: boolean (True jika berhasil)
    """
    try:
        # Simpan dengan encoding UTF-8 BOM dan semicolon sebagai delimiter
        # Agar bisa dibuka rapi di Excel
        dataframe.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

# ============= FUNGSI LOGGING =============

def create_log_entry(log_file, action, id_dokumen, details=""):
    """
    Membuat entri log untuk setiap aksi
    Parameter: log_file, action, id_dokumen, details
    Return: boolean
    """
    try:
        # Load atau buat log file
        if os.path.exists(log_file):
            df_log = pd.read_csv(log_file, sep=';', encoding='utf-8-sig')
        else:
            df_log = pd.DataFrame(columns=[
                'Timestamp', 'Action', 'ID_Dokumen', 'Details'
            ])
        
        # Buat entri baru
        new_log = {
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Action': action,
            'ID_Dokumen': id_dokumen,
            'Details': details
        }
        
        # Tambahkan ke DataFrame
        df_log = pd.concat([df_log, pd.DataFrame([new_log])], ignore_index=True)
        
        # Simpan ke CSV dengan delimiter semicolon
        df_log.to_csv(log_file, index=False, sep=';', encoding='utf-8-sig')
        return True
        
    except Exception as e:
        print(f"Error creating log: {e}")
        return False

def load_log_data(log_file):
    """
    Memuat data log dari file CSV
    Parameter: log_file
    Return: DataFrame
    """
    try:
        if os.path.exists(log_file):
            return pd.read_csv(log_file, sep=';', encoding='utf-8-sig')
        else:
            return pd.DataFrame(columns=['Timestamp', 'Action', 'ID_Dokumen', 'Details'])
    except Exception as e:
        print(f"Error loading log: {e}")
        return pd.DataFrame(columns=['Timestamp', 'Action', 'ID_Dokumen', 'Details'])

# ============= FUNGSI CRUD =============

def create_dokumen(file_path, log_file, id_dokumen, judul, jenis, lokasi, keterangan=""):
    """
    Menambah dokumen baru ke database CSV
    Parameter: file_path, log_file, id_dokumen, judul, jenis, lokasi, keterangan
    Return: boolean dan pesan
    """
    try:
        df = load_data_dokumen(file_path)
        
        # Cek apakah ID sudah ada
        if id_dokumen in df['ID_Dokumen'].values:
            return False, "ID Dokumen sudah ada!"
        
        # Buat data baru
        data_baru = {
            'ID_Dokumen': id_dokumen,
            'Judul_Dokumen': judul,
            'Jenis_Dokumen': jenis,
            'Lokasi_Penyimpanan': lokasi,
            'Tanggal_Input': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Status': 'Aktif',
            'Keterangan': keterangan
        }
        
        # Tambahkan ke DataFrame
        df = pd.concat([df, pd.DataFrame([data_baru])], ignore_index=True)
        
        # Simpan ke CSV
        if save_data_dokumen(file_path, df):
            # Buat log
            create_log_entry(log_file, "CREATE", id_dokumen, f"Dokumen '{judul}' ditambahkan")
            return True, "Dokumen berhasil ditambahkan!"
        else:
            return False, "Gagal menyimpan data"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def read_dokumen(file_path, id_dokumen=None):
    """
    Membaca data dokumen
    Parameter: file_path, id_dokumen (opsional)
    Return: DataFrame atau Series
    """
    try:
        df = load_data_dokumen(file_path)
        
        if id_dokumen:
            # Cari dokumen spesifik
            result = df[df['ID_Dokumen'] == id_dokumen]
            if not result.empty:
                return result.iloc[0]
            else:
                return None
        else:
            # Return semua data
            return df
            
    except Exception as e:
        print(f"Error reading data: {e}")
        return None

def update_dokumen(file_path, log_file, id_dokumen, judul=None, jenis=None, lokasi=None, status=None, keterangan=None):
    """
    Mengupdate data dokumen yang sudah ada
    Parameter: file_path, log_file, id_dokumen, dan field yang ingin diupdate
    Return: boolean dan pesan
    """
    try:
        df = load_data_dokumen(file_path)
        
        # Cek apakah ID ada
        if id_dokumen not in df['ID_Dokumen'].values:
            return False, "ID Dokumen tidak ditemukan!"
        
        # Update data
        idx = df[df['ID_Dokumen'] == id_dokumen].index[0]
        
        update_details = []
        
        if judul:
            df.at[idx, 'Judul_Dokumen'] = judul
            update_details.append(f"Judul: {judul}")
        if jenis:
            df.at[idx, 'Jenis_Dokumen'] = jenis
            update_details.append(f"Jenis: {jenis}")
        if lokasi:
            df.at[idx, 'Lokasi_Penyimpanan'] = lokasi
            update_details.append(f"Lokasi: {lokasi}")
        if status:
            df.at[idx, 'Status'] = status
            update_details.append(f"Status: {status}")
        if keterangan is not None:
            df.at[idx, 'Keterangan'] = keterangan
            update_details.append(f"Keterangan diupdate")
        
        # Simpan perubahan
        if save_data_dokumen(file_path, df):
            # Buat log
            create_log_entry(log_file, "UPDATE", id_dokumen, ", ".join(update_details))
            return True, "Dokumen berhasil diupdate!"
        else:
            return False, "Gagal menyimpan perubahan"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_dokumen(file_path, log_file, id_dokumen):
    """
    Menghapus dokumen dari database
    Parameter: file_path, log_file, id_dokumen
    Return: boolean dan pesan
    """
    try:
        df = load_data_dokumen(file_path)
        
        # Cek apakah ID ada
        if id_dokumen not in df['ID_Dokumen'].values:
            return False, "ID Dokumen tidak ditemukan!"
        
        # Ambil judul sebelum dihapus untuk log
        doc_data = df[df['ID_Dokumen'] == id_dokumen].iloc[0]
        judul_dokumen = doc_data['Judul_Dokumen']
        
        # Hapus baris
        df = df[df['ID_Dokumen'] != id_dokumen]
        
        # Simpan perubahan
        if save_data_dokumen(file_path, df):
            # Buat log
            create_log_entry(log_file, "DELETE", id_dokumen, f"Dokumen '{judul_dokumen}' dihapus")
            return True, "Dokumen berhasil dihapus!"
        else:
            return False, "Gagal menghapus data"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

# ============= FUNGSI QR CODE =============

def generate_qr_code(id_dokumen, output_folder="qr"):
    """
    Generate QR Code untuk dokumen
    Parameter: id_dokumen, output_folder
    Return: path file QR code
    """
    try:
        # Buat folder jika belum ada
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(id_dokumen)
        qr.make(fit=True)
        
        # Buat image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Simpan file
        file_path = os.path.join(output_folder, f"QR_{id_dokumen}.png")
        img.save(file_path)
        
        return file_path
        
    except Exception as e:
        print(f"Error generating QR: {e}")
        return None

def scan_qr_code_from_camera():
    """
    Scan QR Code menggunakan webcam
    Return: ID dokumen yang di-scan atau None
    """
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

# ============= FUNGSI VALIDASI =============

def validate_input_dokumen(id_dokumen, judul, jenis, lokasi):
    """
    Validasi input data dokumen
    Parameter: id_dokumen, judul, jenis, lokasi
    Return: boolean dan pesan error (jika ada)
    """
    errors = []
    
    # Validasi ID
    if not id_dokumen or id_dokumen.strip() == "":
        errors.append("ID Dokumen tidak boleh kosong")
    
    # Validasi Judul
    if not judul or judul.strip() == "":
        errors.append("Judul Dokumen tidak boleh kosong")
    
    # Validasi Jenis
    if not jenis or jenis.strip() == "":
        errors.append("Jenis Dokumen tidak boleh kosong")
    
    # Validasi Lokasi
    if not lokasi or lokasi.strip() == "":
        errors.append("Lokasi Penyimpanan tidak boleh kosong")
    
    if errors:
        return False, "\n".join(errors)
    else:
        return True, "Validasi berhasil"

# ============= FUNGSI PENCARIAN & FILTER =============

def search_dokumen(file_path, keyword):
    """
    Mencari dokumen berdasarkan keyword
    Parameter: file_path, keyword
    Return: DataFrame hasil pencarian
    """
    try:
        df = load_data_dokumen(file_path)
        
        if keyword:
            # Cari di semua kolom text
            mask = (
                df['ID_Dokumen'].str.contains(keyword, case=False, na=False) |
                df['Judul_Dokumen'].str.contains(keyword, case=False, na=False) |
                df['Jenis_Dokumen'].str.contains(keyword, case=False, na=False) |
                df['Lokasi_Penyimpanan'].str.contains(keyword, case=False, na=False)
            )
            return df[mask]
        else:
            return df
            
    except Exception as e:
        print(f"Error searching: {e}")
        return pd.DataFrame()

def filter_by_jenis(file_path, jenis_dokumen):
    """
    Filter dokumen berdasarkan jenis
    Parameter: file_path, jenis_dokumen
    Return: DataFrame hasil filter
    """
    try:
        df = load_data_dokumen(file_path)
        
        if jenis_dokumen and jenis_dokumen != "Semua":
            return df[df['Jenis_Dokumen'] == jenis_dokumen]
        else:
            return df
            
    except Exception as e:
        print(f"Error filtering: {e}")
        return pd.DataFrame()

def filter_by_status(file_path, status):
    """
    Filter dokumen berdasarkan status
    Parameter: file_path, status
    Return: DataFrame hasil filter
    """
    try:
        df = load_data_dokumen(file_path)
        
        if status and status != "Semua":
            return df[df['Status'] == status]
        else:
            return df
            
    except Exception as e:
        print(f"Error filtering: {e}")
        return pd.DataFrame()

# ============= FUNGSI STATISTIK =============

def get_statistics(file_path):
    """
    Mendapatkan statistik data dokumen
    Parameter: file_path
    Return: dictionary statistik
    """
    try:
        df = load_data_dokumen(file_path)
        
        stats = {
            'total_dokumen': len(df),
            'dokumen_aktif': len(df[df['Status'] == 'Aktif']),
            'dokumen_arsip': len(df[df['Status'] == 'Arsip']),
            'jenis_dokumen': df['Jenis_Dokumen'].value_counts().to_dict() if len(df) > 0 else {},
            'lokasi_dokumen': df['Lokasi_Penyimpanan'].value_counts().to_dict() if len(df) > 0 else {}
        }
        
        return stats
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            'total_dokumen': 0,
            'dokumen_aktif': 0,
            'dokumen_arsip': 0,
            'jenis_dokumen': {},
            'lokasi_dokumen': {}
        }

# ============= FUNGSI EXPORT =============

def export_to_excel(file_path, output_file="laporan_dokumen.xlsx"):
    """
    Export data ke Excel
    Parameter: file_path, output_file
    Return: boolean dan pesan
    """
    try:
        df = load_data_dokumen(file_path)
        df.to_excel(output_file, index=False)
        return True, f"Data berhasil di-export ke {output_file}"
    except Exception as e:
        return False, f"Error export: {str(e)}"