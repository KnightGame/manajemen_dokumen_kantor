# 📄 Sistem Manajemen Dokumen Kantor Berbasis QR Code

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📖 Deskripsi Singkat

**Sistem Manajemen Dokumen Kantor Berbasis QR Code** adalah aplikasi berbasis web untuk mengelola dokumen fisik kantor secara efisien. Setiap dokumen memiliki QR Code unik yang dapat di-scan untuk melihat lokasi penyimpanan dan informasi detail dokumen.

### ✨ Fitur Utama
- 📝 **CRUD Dokumen** - Tambah, lihat, edit, dan hapus data dokumen
- 📱 **Generate QR Code** - Otomatis membuat QR Code untuk setiap dokumen
- 📷 **Scan QR Code** - Scan via kamera untuk mencari dokumen
- 📊 **Dashboard & Statistik** - Visualisasi data dengan grafik interaktif
- 🔐 **Sistem Login** - Autentikasi user dengan role-based access
- 💾 **Export & Backup** - Export ke Excel dan backup data ke ZIP
- 🎨 **Tema Custom** - Dark theme modern dengan CSS injection

---

## 🚀 Cara Menjalankan Aplikasi

### Prasyarat
- Python 3.8 atau lebih baru
- pip (Python package manager)

### Langkah Instalasi

1. **Clone atau Download Repository**
   ```bash
   git clone https://github.com/username/sistem-dokumen-qr.git
   cd sistem-dokumen-qr
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Atau install manual:
   ```bash
   pip install streamlit pandas numpy qrcode opencv-python pyzbar pillow plotly openpyxl streamlit-option-menu
   ```

3. **Jalankan Aplikasi**
   ```bash
   streamlit run main.py
   ```

4. **Buka Browser**
   
   Aplikasi akan otomatis terbuka di browser. Jika tidak, buka:
   ```
   http://localhost:8501
   ```

5. **Login**
   ```
   Username: admin
   Password: admin123
   username: staff
   password: staff123
   ```

---

## 📁 Struktur Folder

```
sistem-dokumen-qr/
│
├── 📂 data/                    # Folder penyimpanan data CSV
│   ├── master.csv              # Database utama dokumen
│   ├── log.csv                 # Log aktivitas pengguna
│   └── users.csv               # Data user untuk login
│
├── 📂 qr/                      # Folder penyimpanan gambar QR Code
│   ├── DOC001.png
│   ├── DOC002.png
│   └── ...
│
├── 📄 main.py                  # File utama aplikasi (UI & routing)
├── 📄 utils.py                 # Fungsi utilitas (CRUD, QR, grafik)
├── 📄 requirements.txt         # Daftar dependencies
└── 📄 README.md                # Dokumentasi proyek
```

### Penjelasan File

| File | Deskripsi |
|------|-----------|
| `main.py` | Entry point aplikasi, berisi semua halaman UI dan navigasi |
| `utils.py` | Berisi 41+ fungsi utilitas untuk CRUD, QR Code, grafik, dll |
| `data/master.csv` | Database dokumen dengan format CSV (delimiter: `;`) |
| `data/log.csv` | Menyimpan log aktivitas (CREATE, UPDATE, DELETE, SCAN) |
| `data/users.csv` | Data user untuk autentikasi login |

---

## 📸 Screenshot Aplikasi

### 1. Halaman Login
<img width="1365" height="680" alt="image" src="https://github.com/user-attachments/assets/67c21939-bedd-4351-947b-55b08ee10bb9" />

Halaman login dengan autentikasi username dan password. Default login: `admin` / `admin123`, `staff` / `staff123`

### 2. Dashboard
<img width="1365" height="679" alt="image" src="https://github.com/user-attachments/assets/7681da9b-6820-4e2a-93bd-8c9071c42462" />


Dashboard menampilkan:
- Total dokumen, aktivitas, jenis, dan lokasi
- Grafik pie chart distribusi jenis dokumen
- Grafik bar chart dokumen per lokasi
- Daftar dokumen dan aktivitas terbaru

### 3. Data Master (CRUD)
<img width="1365" height="682" alt="image" src="https://github.com/user-attachments/assets/8666f541-926c-44a6-8bdb-67910c3d2c84" />


Halaman CRUD dengan 4 tab:
- **Lihat Data** - Tabel dengan filter dan pencarian
- **Tambah** - Form input dengan preview dokumen dan QR Code
- **Edit** - Update data dokumen existing
- **Hapus** - Hapus dokumen dengan konfirmasi

### 4. Scan QR Code
<img width="1365" height="680" alt="image" src="https://github.com/user-attachments/assets/82e51e62-555d-4cd7-ba0d-f98ec447edf5" />


Fitur scan QR Code via webcam dengan:
- Auto-scan mode
- Status sukses (hijau) / error (merah)

### 5. Kelola QR Code
<img width="1365" height="679" alt="image" src="https://github.com/user-attachments/assets/492f12f4-7e0a-45fe-a836-4606d198b053" />


Halaman untuk generate dan download QR Code:
- Lihat QR per dokumen
- Generate batch untuk semua dokumen
- Download QR Code individual atau batch

---

## 🔧 Penjelasan Fitur

### 📝 Fitur CRUD (Create, Read, Update, Delete)

| Operasi | Fungsi | Deskripsi |
|---------|--------|-----------|
| **Create** | `tambah_dokumen()` | Menambah dokumen baru ke master.csv dengan ID otomatis (DOC001, DOC002, dst). QR Code otomatis di-generate. |
| **Read** | `get_semua_dokumen()`, `get_dokumen_by_id()` | Membaca semua dokumen atau dokumen spesifik berdasarkan ID. Mendukung filter dan pencarian. |
| **Update** | `update_dokumen()` | Mengubah data dokumen existing. Perubahan langsung disimpan ke CSV. |
| **Delete** | `hapus_dokumen()` | Menghapus dokumen dari database beserta file QR Code-nya. |

#### Alur CRUD:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  User Input │ ──▶ │  Validasi   │ ──▶ │  Simpan CSV │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Log Aksi   │
                    └─────────────┘
```

### 📱 Fitur QR Code

| Fitur | Fungsi | Deskripsi |
|-------|--------|-----------|
| **Generate QR** | `generate_qr_code()` | Membuat QR Code dari ID dokumen, disimpan di folder `/qr` |
| **Generate Batch** | `generate_qr_batch()` | Generate QR untuk semua dokumen sekaligus |
| **Scan QR** | `scan_qr_code()` | Scan QR via webcam menggunakan pyzbar + OpenCV |
| **Preview QR** | Di halaman Tambah & Kelola QR | Preview QR sebelum disimpan |
| **Download QR** | Tombol download | Download file PNG QR Code |

#### Alur Scan QR:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Kamera    │ ──▶ │  Decode QR  │ ──▶ │  Cari di DB │ ──▶ │ Tampil Data │
│   Input     │     │  (pyzbar)   │     │   (CSV)     │     │  Dokumen    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Tidak Ada?  │
                                        │ Tampil Error│
                                        └─────────────┘
```

### 📊 Fitur Tambahan

| Fitur | Deskripsi |
|-------|-----------|
| **Dashboard** | Statistik real-time dengan 4 grafik Plotly interaktif |
| **Login System** | Autentikasi dengan session state, role-based (admin/staff/viewer) |
| **Export Excel** | Export data master ke file .xlsx |
| **Backup ZIP** | Backup seluruh folder data ke file ZIP |
| **Log Aktivitas** | Mencatat semua aksi (CREATE, UPDATE, DELETE, SCAN) |
| **Tema Custom** | Dark theme modern dengan CSS injection |

---

## 👥 Pembagian Tugas Tim

| Nama | NPM | Tugas | Kontribusi |
|------|-----|-------|------------|
| **Ahmad Farid Zulkarnain** | 24020063 | Project Lead & Backend | Arsitektur sistem, fungsi CRUD, integrasi modul |
| **Apriliano Hasta Asfirza** | 24020070 | QR Code Developer | Fungsi generate & scan QR, integrasi pyzbar |
| **Falista Nabila Saputra** | 24020052 | Frontend Developer | UI/UX design, CSS styling, halaman Lobby & Dashboard |
| **Iqma Komala Jaya** | 24020056 | Data & Reporting | Fungsi statistik, grafik Plotly, export Excel |
| **Muhammad Rosyid** | 24020077 | Testing & Documentation | Testing fitur, dokumentasi, README, backup system |

### Rincian Tugas

#### 1. Ahmad Farid Zulkarnain (Project Lead & Backend)
- Merancang arsitektur sistem
- Membuat fungsi `load_data()`, `save_data()`
- Membuat fungsi CRUD dokumen
- Membuat sistem login dan session management
- Integrasi semua modul

#### 2. Apriliano Hasta Asfirza (QR Code Developer)
- Membuat fungsi `generate_qr_code()`
- Membuat fungsi `scan_qr_code()` dengan OpenCV + pyzbar
- Membuat fungsi `generate_qr_batch()`
- Halaman Scan QR dengan auto-scan mode
- Halaman Kelola QR

#### 3. Falista Nabila Saputra (Dashboard & Visualization)
- Halaman Dashboard layout
- Membuat grafik dengan Plotly (`buat_pie_chart()`, `buat_bar_chart()`, `buat_line_chart()`)
- Fungsi `get_statistik()` untuk ringkasan data
- Fungsi `cari_dokumen()`
- CSS custom (dark theme)
- Desain UI/UX keseluruhan

#### 4. Iqma Komala Jaya (Pages & Export)
- Halaman Login dengan form styling
- Halaman Lobby dengan menu cards
- Halaman Laporan dengan visualisasi
- Fungsi `filter_dokumen()`
- Fungsi `export_excel()`

#### 5. Muhammad Rosyid (Testing & Documentation)
- Testing semua fitur CRUD
- Testing fitur scan QR Code
- Membuat dokumentasi README.md
- Fungsi `buat_backup()` untuk backup ZIP
- Halaman Pengaturan dan info sistem

---

## 📋 Requirements

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
qrcode>=7.4.0
opencv-python>=4.8.0
pyzbar>=0.1.9
pillow>=10.0.0
plotly>=5.18.0
openpyxl>=3.1.0
streamlit-option-menu>=0.3.6
```

---

## 🔒 Informasi Login Default

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | admin |
| staff | staff123 | staff |

---

## 🎓 Informasi Akademik

- **Mata Kuliah:** Pemrograman Terstruktur
- **Program Studi:** Sistem Informasi
- **Tahun:** 2025

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan tugas akademik.

---

<div align="center">
  <p>© 2025 Sistem Manajemen Dokumen Kantor | v1.0.0</p>
  <p>Made with using Python & Streamlit</p>
</div>
