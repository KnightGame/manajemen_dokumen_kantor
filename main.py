'''
main.py - Sistem Manajemen Dokumen Kantor Berbasis QR Code
File ini adalah entry point utama aplikasi Streamlit
Berisi semua halaman UI dan logika navigasi
DENGAN ROLE-BASED ACCESS CONTROL
'''
# IMPORT LIBRARY STANDAR PYTHON
import streamlit as st                          # framework ui web
import pandas as pd                             # manipulasi data
import time                                     # fungsi waktu
import io                                       # manipulasi input/output
import base64                                   # encoding/decoding
import qrcode                                   # membuat qr code
from datetime import datetime                   # tanggal dan waktu    
from streamlit_option_menu import option_menu   # menu sidebar
import os                                       # manipulasi file dan folder

# IMPORT FUNGSI DARI FILE UTILS.PY
from utils import (
    # fungsi inisialisasi - membuat folder dan file csv jika belum ada
    init_folders, init_master_csv, init_log_csv, init_users_csv,
    # fungsi utama aplikasi
    load_data, save_data, tambah_dokumen, get_dokumen_by_id, update_dokumen,
    hapus_dokumen, get_semua_dokumen, 
    # fungsi log aktivitas
    tambah_log, get_semua_log,
    # fungsi qr code
    generate_qr_code,
    # fungsi statistik dan grafik
    get_statistik, get_dokumen_terbaru, get_log_terbaru,
    # fungsi pencarian, filter
    cari_dokumen, filter_dokumen,
    # fungsi login
    validasi_login, tambah_user, get_file_size,
    # konstanta
    JENIS_DOKUMEN, STATUS_DOKUMEN, LOKASI_LIST
)

# KONFIGURASI HALAMAN STREAMLIT
st.set_page_config(
    page_title="SMDOK - Sistem Manajemen Dokumen QR",   # judul tab browser
    page_icon="📄",                                     # icon tab browser
    layout="wide"                                       # layout lebar penuh
)

# KONSTANTA PATH FILE
FILE_DOKUMEN = "data/master.csv"        # database dokumen
FILE_LOG = "data/log.csv"               # log aktivitas
FILE_USERS = "data/users.csv"           # data user
FOLDER_QR = "qr"                        # folder menyimpan gambar qr code

# ============================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================
# Definisi akses untuk setiap role
ROLE_ACCESS = {
    'viewer': {
        'menu': ['Lobby', 'Dashboard', 'Scan QR', 'Laporan', 'Pengaturan'],
        'dashboard_aktivitas': False,       # tidak bisa lihat aktivitas terbaru
        'data_master_tabs': [],             # tidak ada akses ke data master
        'laporan_tabs': ['Grafik'],         # hanya grafik
        'pengaturan_tabs': ['Tentang'],     # hanya tentang
        'kelola_qr': False,                 # tidak bisa kelola QR
    },
    'staff': {
        'menu': ['Lobby', 'Dashboard', 'Data Master', 'Scan QR', 'Laporan', 'Pengaturan'],
        'dashboard_aktivitas': True,        # bisa lihat aktivitas terbaru
        'data_master_tabs': ['Lihat Data'], # hanya lihat data
        'laporan_tabs': ['Grafik', 'Log Aktivitas'],  # grafik dan log
        'pengaturan_tabs': ['Tentang'],     # hanya tentang
        'kelola_qr': False,                 # tidak bisa kelola QR
    },
    'admin': {
        'menu': ['Lobby', 'Dashboard', 'Data Master', 'Scan QR', 'Kelola QR', 'Laporan', 'Pengaturan'],
        'dashboard_aktivitas': True,        # bisa lihat aktivitas terbaru
        'data_master_tabs': ['Lihat Data', 'Tambah', 'Edit', 'Hapus'],  # semua tab
        'laporan_tabs': ['Grafik', 'Log Aktivitas', 'Export'],  # semua tab
        'pengaturan_tabs': ['Akun', 'Data', 'Tentang'],  # semua tab
        'kelola_qr': True,                  # bisa kelola QR
    }
}

def get_user_access():
    """
    Ambil konfigurasi akses berdasarkan role user yang login
    """
    role = st.session_state.get('role', 'viewer').lower()
    return ROLE_ACCESS.get(role, ROLE_ACCESS['viewer'])

def has_menu_access(menu_name):
    """
    Cek apakah user punya akses ke menu tertentu
    """
    access = get_user_access()
    return menu_name in access['menu']

# CSS STYLING
st.markdown("""
<style>
    /* Dark Theme: mengubah background utama menjadi gelap */
    .stApp { background-color: #0e1117; }
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a1d24; }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Typography: mengatur warna teks agar kontras dengan background gelap */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { color: #fafafa !important; }
    
    /* Metric Cards: Card untuk menampilkan angka statistik dengan gradient */
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    /* variasi warna untuk metric cards */
    .metric-card h2 { color: white !important; font-size: 32px !important; margin: 0; }
    .metric-card p { color: rgba(255,255,255,0.9) !important; margin: 5px 0 0 0; }
    .metric-card.green { background: linear-gradient(135deg, #10b981, #059669); }
    .metric-card.blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .metric-card.orange { background: linear-gradient(135deg, #f59e0b, #d97706); }
    
    /* Form Elements: styling untuk input teks */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #262730 !important;
        color: #fafafa !important;
        border: 1px solid #3d4050 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 25px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Cards */
    .info-card {
        background: #1a1d24;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3139;
        margin: 10px 0;
    }
    
    /* Menu Cards untuk Lobby */
    .menu-card {
        background: linear-gradient(135deg, #1a1d24, #2d3139);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #3d4050;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .menu-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .menu-card .icon { font-size: 48px; margin-bottom: 15px; }
    .menu-card .title { font-size: 20px; font-weight: 600; color: #fafafa; }
    .menu-card .desc { font-size: 14px; color: #b0b8c4; margin-top: 8px; }
    
    /* Disabled Menu Card */
    .menu-card.disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    .menu-card.disabled:hover {
        transform: none;
        box-shadow: none;
    }
    
    /* Scan Result: card hijau untuk sukses, merah untuk error */
    .scan-success {
        background: rgba(16, 185, 129, 0.15);
        border: 2px solid #10b981;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
    }
    .scan-error {
        background: rgba(239, 68, 68, 0.15);
        border: 2px solid #ef4444;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
    }
    
    /* Role Badge */
    .role-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .role-admin { background: #ef4444; color: white; }
    .role-staff { background: #3b82f6; color: white; }
    .role-viewer { background: #10b981; color: white; }
    
    /* Hide camera button */
    [data-testid="stCameraInput"] > button,
    [data-testid="stCameraInput"] button[kind="secondary"],
    .stCameraInput > button,
    div[data-testid="stCameraInput"] > div > button {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# FUNGSI INISIALISASI APLIKASI
def init_app():
    """
    Inisialisasi aplikasi
    ---------------------
    Fungsi ini dipanggil sekali saat aplikasi dimulai.
    Membuat folder dan file CSV jika belum ada.
    
    Langkah yang dilakukan:
    1. Membuat folder /data dan /qr
    2. Membuat file master.csv (database dokumen)
    3. Membuat file log.csv (log aktivitas)
    4. Membuat file users.csv (data user dengan default admin)
    """
    init_folders()                      # buat folder data dan qr
    init_master_csv(FILE_DOKUMEN)       # buat master.csv jika belum ada
    init_log_csv(FILE_LOG)              # buat log.csv jika belum ada
    init_users_csv(FILE_USERS)          # buat users.csv dengan admin default jika belum ada

def get_role_badge(role):
    """
    Mendapatkan badge HTML untuk role user
    """
    role_lower = role.lower()
    if role_lower == 'admin':
        return '<span class="role-badge role-admin">Admin</span>'
    elif role_lower == 'staff':
        return '<span class="role-badge role-staff">Staff</span>'
    else:
        return '<span class="role-badge role-viewer">Viewer</span>'

# HALAMAN DALAM PENGEMBANGAN
def halaman_dalam_pengembangan(nama_fitur, icon):
    """
    Halaman placeholder untuk fitur yang sedang dalam pengembangan
    --------------------------------------------------------------
    Menampilkan pesan bahwa fitur sedang dikembangkan
    
    Parameter:
    - nama_fitur: nama fitur yang sedang dikembangkan
    - icon: emoji icon untuk fitur tersebut
    """
    st.header(f"{icon} {nama_fitur}")
    
    # Card utama dengan animasi
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1d24 0%, #2d3139 100%);
        padding: 60px 40px;
        border-radius: 20px;
        text-align: center;
        margin: 50px 0;
        border: 2px dashed #f59e0b;
        box-shadow: 0 10px 40px rgba(245, 158, 11, 0.1);
    ">
        <div style="font-size: 80px; margin-bottom: 20px;">🚧</div>
        <h2 style="color: #f59e0b; font-size: 32px; margin-bottom: 15px;">
            Fitur Sedang Dalam Pengembangan
        </h2>
        <p style="color: #b0b8c4; font-size: 18px; margin-bottom: 25px;">
            Halaman <strong style="color: #fafafa;">{icon} {nama_fitur}</strong> sedang dalam tahap pengembangan.
        </p>
        <p style="color: #6b7280; font-size: 14px;">
            Tim pengembang sedang bekerja keras untuk menghadirkan fitur ini.<br>
            Silakan kembali lagi nanti! 🙏
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Info tambahan
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("💡 **Tips:** Anda dapat menggunakan menu lain yang sudah tersedia seperti **Lobby**, **Dashboard**, **Data Master**, dan **Pengaturan**.")
    
    # Tombol kembali ke lobby
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🏠 Kembali ke Lobby", use_container_width=True, type="primary"):
            st.session_state['menu'] = 'Lobby'
            st.rerun()

# HALAMAN LOGIN
def halaman_login():
    """
    Tampilkan halaman login
    -----------------------
    Halaman ini ditampilkan jika user belum login.
    Terdapat form untuk input username dan password.
    """
    # Header dengan styling
    st.markdown("""
    <div style="text-align: center; padding: 50px 0;">
        <h1 style="font-size: 48px;">📄 Sistem Manajemen Dokumen</h1>
        <p style="font-size: 20px; color: #b0b8c4;">Berbasis QR Code</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout 3 kolom, form di tengah
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        
        with st.form("form_login"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            submit = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submit:
                if username and password:
                    # Validasi login menggunakan fungsi dari utils.py
                    hasil = validasi_login(FILE_USERS, username, password)
                    if hasil['valid']:
                        # Login berhasil, simpan ke session state
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = hasil['username']
                        st.session_state['role'] = hasil['role']
                        st.success(f"✅ Login berhasil sebagai {hasil['role'].upper()}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")
                else:
                    st.warning("⚠️ Harap isi username dan password!")
        
        # Info default login
        st.markdown("---")
        st.markdown("#### 💡 Akun Default:")
        st.markdown("""
        | Username | Password | Role |
        |----------|----------|------|
        | admin | admin123 | Admin |
        | staff | staff123 | Staff |
        | viewer | viewer123 | Viewer |
        """)

# HALAMAN LOBBY
def halaman_lobby():
    """
    Tampilkan halaman lobby dengan menu utama
    -----------------------------------------
    Halaman ini adalah halaman utama setelah login.
    Menampilkan menu-menu yang dapat diakses berdasarkan role user.
    """
    access = get_user_access()
    role = st.session_state.get('role', 'viewer')

    # Header dengan gradient
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px;">
        <h1 style="color: white; font-size: 36px; margin: 0;">📄 Sistem Manajemen Dokumen Kantor</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 18px; margin-top: 10px;">Berbasis QR Code - Offline System</p>
    </div>
    
    <div style="background: #1a1d24; padding: 20px; border-radius: 12px; margin-bottom: 30px; border-left: 4px solid #8b5cf6;">
        <h3 style="margin: 0;">👋 Selamat Datang, <span style="color: #8b5cf6;">{st.session_state.get('username', 'Admin')}</span>! {get_role_badge(role)}</h3>
        <p style="color: #b0b8c4; margin: 5px 0 0 0;">📅 {datetime.now().strftime("%A, %d %B %Y - %H:%M WIB")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu Cards
    st.markdown("### 🚀 Menu Utama")
    
    # Definisi semua menu items
    all_menu_items = [
        {"icon": "📊", "title": "Dashboard", "desc": "Statistik & Ringkasan", "color": "#8b5cf6"},
        {"icon": "📁", "title": "Data Master", "desc": "Kelola Dokumen", "color": "#3b82f6"},
        {"icon": "📷", "title": "Scan QR", "desc": "Scan QR Code", "color": "#10b981"},
        {"icon": "📱", "title": "Kelola QR", "desc": "Generate QR Code", "color": "#f59e0b"},
        {"icon": "📈", "title": "Laporan", "desc": "Grafik & Export", "color": "#ec4899"},
        {"icon": "⚙️", "title": "Pengaturan", "desc": "Akun & Backup", "color": "#6366f1"},
    ]
    
    # Filter menu - hanya tampilkan menu yang bisa diakses oleh user
    menu_items = [item for item in all_menu_items if item['title'] in access['menu']]
    
    # Hitung jumlah kolom berdasarkan jumlah menu yang tersedia
    num_items = len(menu_items)
    num_cols = 3 if num_items >= 3 else num_items  # maksimal 3 kolom
    
    # Tampilkan menu dalam grid dinamis
    if num_items > 0:
        cols = st.columns(num_cols)
        for i, item in enumerate(menu_items):
            with cols[i % num_cols]:
                st.markdown(f"""
                <div class="menu-card" style="border-top: 4px solid {item['color']};">
                    <div class="icon">{item['icon']}</div>
                    <div class="title">{item['title']}</div>
                    <div class="desc">{item['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Tombol untuk navigasi
                if st.button(f"Buka {item['title']}", key=f"btn_{item['title']}", use_container_width=True):
                    st.session_state['menu'] = item['title']
                    st.rerun()
    
    # Statistik cepat di bawah menu
    st.markdown("---")
    st.markdown("### 📊 Statistik Cepat")
    
    # Ambil data statistik dari utils.py
    stats = get_statistik(FILE_DOKUMEN)
    df_log = get_semua_log(FILE_LOG)
    
    # Tampilkan statistik dalam 4 kolom
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{stats['total']}</h2>
            <p>📄 Total Dokumen</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Aktivitas hanya ditampilkan untuk staff dan admin
        if access['dashboard_aktivitas']:
            st.markdown(f"""
            <div class="metric-card green">
                <h2>{len(df_log)}</h2>
                <p>📝 Total Aktivitas</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card green" style="opacity: 0.5;">
                <h2>🔒</h2>
                <p>📝 Total Aktivitas</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card blue">
            <h2>{len(stats['per_jenis'])}</h2>
            <p>📁 Jenis Dokumen</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card orange">
            <h2>{len(stats['per_lokasi'])}</h2>
            <p>📍 Lokasi Aktif</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Info akses role
    st.markdown("---")
    st.markdown("### 🔐 Akses Role Anda")
    
    role_info = {
        'admin': "Anda memiliki akses penuh ke semua fitur aplikasi.",
        'staff': "Anda dapat melihat data, log aktivitas, dan scan QR. Tidak dapat menambah/edit/hapus dokumen atau mengelola QR.",
        'viewer': "Anda dapat melihat dashboard, scan QR, dan melihat grafik laporan."
    }
    
    st.info(f"**Role: {role.upper()}** - {role_info.get(role.lower(), 'Akses terbatas')}")

# HALAMAN DASHBOARD
def halaman_dashboard():
    """
    Halaman dashboard dengan statistik dan grafik
    ---------------------------------------------
    Menampilkan ringkasan data dokumen dan aktivitas terbaru.
    Aktivitas terbaru hanya ditampilkan untuk staff dan admin.
    """
    access = get_user_access()
    
    st.header("📊 Dashboard")
    
    # Ambil data statistik dari utils.py
    stats = get_statistik(FILE_DOKUMEN)
    df_log = get_semua_log(FILE_LOG)
    
    # Bagian statistik atas dalam 4 kolom
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="metric-card"><h2>{stats["total"]}</h2><p>📄 Total Dokumen</p></div>', unsafe_allow_html=True)
    with col2:
        if access['dashboard_aktivitas']:
            st.markdown(f'<div class="metric-card green"><h2>{len(df_log)}</h2><p>📝 Aktivitas</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-card green" style="opacity: 0.5;"><h2>🔒</h2><p>📝 Aktivitas</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card blue"><h2>{len(stats["per_jenis"])}</h2><p>📁 Jenis</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card orange"><h2>{len(stats["per_lokasi"])}</h2><p>📍 Lokasi</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")  # garis pemisah
    
    # Data Terbaru dalam 2 kolom
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Dokumen Terbaru")
        # Tampilkan 5 dokumen terbaru
        df_terbaru = get_dokumen_terbaru(FILE_DOKUMEN, 5)
        if len(df_terbaru) > 0:
            st.dataframe(df_terbaru[['ID', 'Judul', 'Jenis', 'Status']], use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada dokumen")
    
    with col2:
        st.subheader("📝 Aktivitas Terbaru")
        # Cek akses untuk melihat aktivitas
        if access['dashboard_aktivitas']:
            df_log_terbaru = get_log_terbaru(FILE_LOG, 5)
            if len(df_log_terbaru) > 0:
                st.dataframe(df_log_terbaru[['ID_Dokumen', 'Aksi', 'Waktu']], use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada aktivitas")
        else:
            st.warning("🔒 Anda tidak memiliki akses untuk melihat aktivitas terbaru.")

# HALAMAN DATA MASTER
def halaman_data_master():
    """
    Halaman CRUD data dokumen dengan ROLE-BASED ACCESS
    ---------------------------------------------------
    Terdiri dari 4 tab:
    1. Lihat Data - menampilkan semua dokumen dengan filter dan pencarian
    2. Tambah - form untuk menambah dokumen baru dengan preview
    3. Edit - form untuk mengubah data dokumen
    4. Hapus - menghapus dokumen dengan konfirmasi
    
    Akses berdasarkan Role:
    - Viewer: Tidak ada akses
    - Staff: Hanya tab Lihat Data
    - Admin: Semua tab (Lihat Data, Tambah, Edit, Hapus)
    """
    access = get_user_access()
    allowed_tabs = access['data_master_tabs']
    
    st.header("📁 Data Master Dokumen")
    
    # Jika tidak ada akses sama sekali
    if not allowed_tabs:
        st.error("🔒 Anda tidak memiliki akses ke halaman ini.")
        return
    
    # Buat tab berdasarkan akses
    tab_names = []
    tab_icons = {"Lihat Data": "📋", "Tambah": "➕", "Edit": "✏️", "Hapus": "🗑️"}
    
    for tab in allowed_tabs:
        tab_names.append(f"{tab_icons.get(tab, '')} {tab}")
    
    tabs = st.tabs(tab_names)
    
    # TAB: LIHAT DATA
    if "Lihat Data" in allowed_tabs:
        tab_index = allowed_tabs.index("Lihat Data")
        with tabs[tab_index]:
            # Baris filter dan pencarian
            col1, col2, col3 = st.columns(3)
            with col1:
                # Input pencarian
                keyword = st.text_input("🔍 Cari", placeholder="Masukkan keyword...")
            with col2:
                # Dropdown filter jenis
                filter_jenis = st.selectbox("Filter Jenis", ["Semua"] + JENIS_DOKUMEN)
            with col3:
                # Dropdown filter status
                filter_status = st.selectbox("Filter Status", ["Semua"] + STATUS_DOKUMEN)
            
            # Ambil dan filter data
            if keyword:
                df = cari_dokumen(FILE_DOKUMEN, keyword)    # fungsi cari dari utils.py
            else:
                df = get_semua_dokumen(FILE_DOKUMEN)        # fungsi ambil semua data dari utils.py
            
            # Terapkan filter jika bukan "Semua"
            if filter_jenis != "Semua" and len(df) > 0 and 'Jenis' in df.columns:
                df = df[df['Jenis'] == filter_jenis]
            if filter_status != "Semua" and len(df) > 0 and 'Status' in df.columns:
                df = df[df['Status'] == filter_status]
            
            # Tampilkan tabel hasil
            if len(df) > 0:
                st.dataframe(df, use_container_width=True, hide_index=True, height=400)
                st.info(f"📊 Total: {len(df)} dokumen")
            else:
                st.warning("Tidak ada data dokumen")
    
    # TAB: TAMBAH DOKUMEN dengan PREVIEW (hanya Admin)
    if "Tambah" in allowed_tabs:
        tab_index = allowed_tabs.index("Tambah")
        with tabs[tab_index]:
            st.subheader("➕ Tambah Dokumen Baru")
            
            # Layout dua kolom: form input dan preview
            col_form, col_preview = st.columns([1, 1])
            
            with col_form:
                st.markdown("#### 📝 Form Input")
                
                # Input judul, jenis, lokasi, status, keterangan
                judul = st.text_input("Judul Dokumen *", placeholder="Masukkan judul dokumen", key="input_judul")
                jenis = st.selectbox("Jenis Dokumen *", JENIS_DOKUMEN, key="input_jenis")
                lokasi = st.selectbox("Lokasi Penyimpanan *", LOKASI_LIST, key="input_lokasi")
                status = st.selectbox("Status *", STATUS_DOKUMEN, key="input_status")
                keterangan = st.text_area("Keterangan", placeholder="Keterangan tambahan...", height=100, key="input_keterangan")
            
            # Preview Dokumen dan QR Code
            with col_preview:
                st.markdown("#### 👁️ Preview Dokumen")
                
                df_preview = get_semua_dokumen(FILE_DOKUMEN)
                
                # Logika generate ID baru untuk preview
                if len(df_preview) == 0 or 'ID' not in df_preview.columns:
                    preview_id = "DOC001"
                else:
                    try:
                        last_id = df_preview['ID'].dropna().iloc[-1] if len(df_preview['ID'].dropna()) > 0 else "DOC000"
                        num = int(str(last_id).replace("DOC", "")) + 1
                        preview_id = f"DOC{num:03d}"
                    except:
                        preview_id = f"DOC{len(df_preview)+1:03d}"
                
                # Set preview values
                preview_judul = judul if judul else "Judul belum diisi"
                preview_judul_style = "" if judul else "color: #6b7280; font-style: italic;"
                preview_keterangan = keterangan if keterangan else "Tidak ada keterangan"
                preview_ket_style = "" if keterangan else "color: #6b7280; font-style: italic;"
                
                # Preview Card - dalam satu blok HTML
                html_preview = f"""
                <div style="background: linear-gradient(135deg, #1a1d24, #2d3139); padding: 25px; border-radius: 15px; border: 1px solid #3d4050; border-left: 4px solid #8b5cf6;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <span style="background: #8b5cf6; color: white; padding: 5px 15px; border-radius: 20px; font-weight: 600;">🆔 {preview_id}</span>
                        <span style="color: #b0b8c4; font-size: 12px;">📅 {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
                    </div>
                    <h3 style="color: #fafafa; margin: 10px 0; font-size: 20px; {preview_judul_style}">📄 {preview_judul}</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                        <div style="background: #262730; padding: 12px; border-radius: 8px;">
                            <p style="color: #8b5cf6; font-size: 12px; margin: 0;">📁 Jenis</p>
                            <p style="color: #fafafa; margin: 5px 0 0 0; font-weight: 500;">{jenis}</p>
                        </div>
                        <div style="background: #262730; padding: 12px; border-radius: 8px;">
                            <p style="color: #10b981; font-size: 12px; margin: 0;">📊 Status</p>
                            <p style="color: #fafafa; margin: 5px 0 0 0; font-weight: 500;">{status}</p>
                        </div>
                        <div style="background: #262730; padding: 12px; border-radius: 8px; grid-column: span 2;">
                            <p style="color: #f59e0b; font-size: 12px; margin: 0;">📍 Lokasi Fisik</p>
                            <p style="color: #fafafa; margin: 5px 0 0 0; font-weight: 500;">{lokasi}</p>
                        </div>
                    </div>
                    <div style="background: #262730; padding: 12px; border-radius: 8px; margin-top: 10px;">
                        <p style="color: #3b82f6; font-size: 12px; margin: 0;">📝 Keterangan</p>
                        <p style="color: #fafafa; margin: 5px 0 0 0; {preview_ket_style}">{preview_keterangan}</p>
                    </div>
                </div>
                """
                st.markdown(html_preview, unsafe_allow_html=True)
                
                # Preview QR Code
                st.markdown("#### 📱 Preview QR Code")
                
                # Generate temporary QR for preview
                qr = qrcode.QRCode(
                    version=1,                                          # ukuran qr code (1 = paling kecil)
                    error_correction=qrcode.constants.ERROR_CORRECT_L,  # tingkat koreksi kesalahan
                    box_size=8,                                         # ukuran tiap kotak
                    border=3                                            # lebar border
                )
                qr.add_data(preview_id)     # data yang akan di-encode
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="#8b5cf6", back_color="white")
                
                # Konversi ke bytes untuk ditampilkan di streamlit
                buffer = io.BytesIO()
                qr_img.save(buffer, format='PNG')
                buffer.seek(0)
                
                # Tampilkan QR Code di tengah
                col_qr1, col_qr2, col_qr3 = st.columns([1, 2, 1])
                with col_qr2:
                    st.image(buffer, width=180, caption=f"QR Code: {preview_id}")
            
            # Tombol Simpan
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💾 Simpan Dokumen", use_container_width=True, type="primary", key="btn_simpan_dokumen"):
                    if judul:
                        # Panggil fungsi tambah_dokumen dari utils.py
                        new_id = tambah_dokumen(FILE_DOKUMEN, {
                            'judul': judul,
                            'jenis': jenis,
                            'lokasi': lokasi,
                            'status': status,
                            'keterangan': keterangan
                        })
                        
                        # Catat log aktivitas
                        tambah_log(FILE_LOG, new_id, "CREATE", st.session_state.get('username', 'Admin'))
                        st.success(f"✅ Dokumen berhasil ditambahkan dengan ID: **{new_id}**")
                        st.balloons()   # efek balon saat sukses
                    else:
                        st.error("❌ Judul dokumen harus diisi!")
    
    # TAB: EDIT DOKUMEN (hanya Admin)
    if "Edit" in allowed_tabs:
        tab_index = allowed_tabs.index("Edit")
        with tabs[tab_index]:
            st.subheader("✏️ Edit Dokumen")
            
            df = get_semua_dokumen(FILE_DOKUMEN)
            
            if len(df) > 0 and 'ID' in df.columns:
                # Dropdown pilih ID dokumen
                id_list = df['ID'].tolist()
                selected_id = st.selectbox("Pilih ID Dokumen", id_list, key="edit_select_id")
                
                if selected_id:
                    # Ambil data dokumen berdasarkan ID
                    dok = get_dokumen_by_id(FILE_DOKUMEN, selected_id)
                    
                    if dok:
                        with st.form("form_edit"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_judul = st.text_input("Judul", value=dok.get('Judul', ''))
                                new_jenis = st.selectbox("Jenis", JENIS_DOKUMEN, 
                                    index=JENIS_DOKUMEN.index(dok['Jenis']) if dok.get('Jenis') in JENIS_DOKUMEN else 0)
                                new_lokasi = st.selectbox("Lokasi", LOKASI_LIST,
                                    index=LOKASI_LIST.index(dok['Lokasi_Fisik']) if dok.get('Lokasi_Fisik') in LOKASI_LIST else 0)
                            
                            with col2:
                                new_status = st.selectbox("Status", STATUS_DOKUMEN,
                                    index=STATUS_DOKUMEN.index(dok['Status']) if dok.get('Status') in STATUS_DOKUMEN else 0)
                                new_keterangan = st.text_area("Keterangan", value=dok.get('Keterangan', ''), height=118)
                            
                            submit = st.form_submit_button("💾 Update", use_container_width=True)
                            
                            if submit:
                                # Panggil fungsi update dari utils.py
                                update_dokumen(FILE_DOKUMEN, selected_id, {
                                    'Judul': new_judul,
                                    'Jenis': new_jenis,
                                    'Lokasi_Fisik': new_lokasi,
                                    'Status': new_status,
                                    'Keterangan': new_keterangan
                                })
                                # Catat log aktivitas
                                tambah_log(FILE_LOG, selected_id, "UPDATE", st.session_state.get('username', 'Admin'))
                                st.success(f"✅ Dokumen {selected_id} berhasil diupdate!")
                                st.rerun()
            else:
                st.warning("Belum ada data dokumen")
    
    # TAB: HAPUS DOKUMEN (hanya Admin)
    if "Hapus" in allowed_tabs:
        tab_index = allowed_tabs.index("Hapus")
        with tabs[tab_index]:
            st.subheader("🗑️ Hapus Dokumen")
            
            df = get_semua_dokumen(FILE_DOKUMEN)
            
            if len(df) > 0 and 'ID' in df.columns:
                id_list = df['ID'].tolist()
                selected_id = st.selectbox("Pilih ID Dokumen untuk dihapus", id_list, key="hapus_id")
                
                if selected_id:
                    dok = get_dokumen_by_id(FILE_DOKUMEN, selected_id)
                    
                    if dok:
                        # Tampilkan info dokumen yang akan dihapus
                        st.markdown(f"""
                        <div class="info-card">
                            <p><strong>ID:</strong> {dok['ID']}</p>
                            <p><strong>Judul:</strong> {dok['Judul']}</p>
                            <p><strong>Jenis:</strong> {dok['Jenis']}</p>
                            <p><strong>Lokasi:</strong> {dok['Lokasi_Fisik']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Peringatan hapus
                        st.warning("⚠️ Tindakan ini tidak dapat dibatalkan!")
                        
                        konfirmasi = st.checkbox("Saya yakin ingin menghapus dokumen ini")
                        
                        if konfirmasi:
                            if st.button("🗑️ Hapus Permanen", type="primary", key="btn_hapus_permanen"):
                                # Catat log aktivitas sebelum hapus
                                tambah_log(FILE_LOG, selected_id, "DELETE", st.session_state.get('username', 'Admin'))
                                # Hapus dokumen (tanpa menghapus file QR - fitur dalam pengembangan)
                                hapus_dokumen(FILE_DOKUMEN, selected_id)
                                st.success(f"✅ Dokumen {selected_id} berhasil dihapus!")
                                time.sleep(1)
                                st.rerun()
            else:
                st.warning("Belum ada data dokumen")

# HALAMAN SCAN QR (DALAM PENGEMBANGAN)
def halaman_scan_qr():
    """
    Halaman scan QR code
    --------------------
    FITUR SEDANG DALAM PENGEMBANGAN
    """
    halaman_dalam_pengembangan("Scan QR", "📷")

# HALAMAN KELOLA QR (DALAM PENGEMBANGAN)
def halaman_kelola_qr():
    """
    Halaman kelola QR Code (hanya Admin)
    ------------------------------------
    FITUR SEDANG DALAM PENGEMBANGAN
    """
    halaman_dalam_pengembangan("Kelola QR", "📱")

# HALAMAN LAPORAN (DALAM PENGEMBANGAN)
def halaman_laporan():
    """
    Halaman laporan dan grafik
    --------------------------
    FITUR SEDANG DALAM PENGEMBANGAN
    """
    halaman_dalam_pengembangan("Laporan", "📈")

# HALAMAN PENGATURAN
def halaman_pengaturan():
    """
    Halaman pengaturan dengan ROLE-BASED ACCESS
    --------------------------------------------
    Terdiri dari 3 tab:
    1. Akun - manajemen user (hanya Admin)
    2. Data - info penyimpanan (hanya Admin)
    3. Tentang - informasi aplikasi (semua role)
    
    Akses berdasarkan Role:
    - Viewer: Hanya tab Tentang
    - Staff: Hanya tab Tentang
    - Admin: Semua tab (Akun, Data, Tentang)
    """
    access = get_user_access()
    allowed_tabs = access['pengaturan_tabs']
    
    st.header("⚙️ Pengaturan")
    
    if not allowed_tabs:
        st.error("🔒 Anda tidak memiliki akses ke halaman ini.")
        return
    
    # Buat tab berdasarkan akses
    tab_names = []
    tab_icons = {"Akun": "👤", "Data": "💾", "Tentang": "ℹ️"}
    
    for tab in allowed_tabs:
        tab_names.append(f"{tab_icons.get(tab, '')} {tab}")
    
    tabs = st.tabs(tab_names)
    
    # TAB: AKUN (hanya Admin)
    if "Akun" in allowed_tabs:
        tab_index = allowed_tabs.index("Akun")
        with tabs[tab_index]:
            st.subheader("👤 Manajemen Akun")
            
            role = st.session_state.get('role', 'viewer')
            st.markdown(f"👤 Login sebagai: **{st.session_state.get('username', 'Admin')}** {get_role_badge(role)}", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### ➕ Tambah User Baru")
            
            # Form tambah user
            with st.form("form_user"):
                new_user = st.text_input("Username")
                new_pass = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["admin", "staff", "viewer"])
                
                if st.form_submit_button("💾 Tambah User", use_container_width=True):
                    if new_user and new_pass:
                        # Panggil fungsi tambah_user dari utils.py
                        if tambah_user(FILE_USERS, new_user, new_pass, new_role):
                            st.success(f"✅ User {new_user} berhasil ditambahkan!")
                        else:
                            st.error("❌ Username sudah ada!")
                    else:
                        st.warning("⚠️ Harap isi semua field!")
            
            # Daftar user yang ada
            st.markdown("---")
            st.markdown("#### 📋 Daftar User")
            df_users = load_data(FILE_USERS)
            if len(df_users) > 0:
                # Sembunyikan kolom password
                df_display = df_users.copy()
                df_display['password'] = '********'
                st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # TAB: DATA (hanya Admin)
    if "Data" in allowed_tabs:
        tab_index = allowed_tabs.index("Data")
        with tabs[tab_index]:
            st.subheader("💾 Info Penyimpanan")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Display ukuran file master.csv
                st.metric("Master CSV", get_file_size(FILE_DOKUMEN))
            with col2:
                # Display ukuran file log.csv
                st.metric("Log CSV", get_file_size(FILE_LOG))
            with col3:
                # Hitung jumlah file QR di folder qr/
                qr_count = len([f for f in os.listdir(FOLDER_QR) if f.endswith('.png')]) if os.path.exists(FOLDER_QR) else 0
                st.metric("QR Files", f"{qr_count} files")
    
    # TAB: TENTANG (semua role)
    if "Tentang" in allowed_tabs:
        tab_index = allowed_tabs.index("Tentang")
        with tabs[tab_index]:
            # Header dengan gradient
            st.markdown("""
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 15px; margin-bottom: 20px;">
                <h1 style="color: white; font-size: 32px;">📄 Sistem Manajemen Dokumen Kantor</h1>
                <p style="color: rgba(255,255,255,0.9); font-size: 18px;">Berbasis QR Code - Offline System</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Deskripsi aplikasi
            st.markdown("""
            ### 📖 Tentang Aplikasi
            
            **Sistem Manajemen Dokumen Kantor Berbasis QR Code** adalah aplikasi untuk mengelola 
            dokumen fisik secara efisien. Setiap dokumen memiliki QR Code unik yang dapat di-scan 
            untuk melihat lokasi penyimpanan dan informasi dokumen.
            
            ### ✨ Fitur Utama
            - 📝 CRUD Data Dokumen
            - 📱 Generate QR Code Otomatis
            - 📷 Scan QR Code via Kamera (Realtime & Foto)
            - 📊 Dashboard & Statistik
            - 📈 Grafik Interaktif
            - 💾 Export & Backup Data
            - 🔐 Role-Based Access Control (Admin, Staff, Viewer)
            
            ### 🔐 Hak Akses Role
            
            | Fitur | Viewer | Staff | Admin |
            |-------|--------|-------|-------|
            | Lobby | ✅ | ✅ | ✅ |
            | Dashboard | ✅ (tanpa log) | ✅ | ✅ |
            | Data Master - Lihat | ❌ | ✅ | ✅ |
            | Data Master - Tambah/Edit/Hapus | ❌ | ❌ | ✅ |
            | Scan QR | ✅ | ✅ | ✅ |
            | Kelola QR | ❌ | ❌ | ✅ |
            | Laporan - Grafik | ✅ | ✅ | ✅ |
            | Laporan - Log Aktivitas | ❌ | ✅ | ✅ |
            | Laporan - Export | ❌ | ❌ | ✅ |
            | Pengaturan - Akun | ❌ | ❌ | ✅ |
            | Pengaturan - Data | ❌ | ❌ | ✅ |
            | Pengaturan - Tentang | ✅ | ✅ | ✅ |
            
            ### 👥 Tim Pengembang
            """)
            
            # Daftar pengembang
            developers = [
                {"name": "Ahmad Farid Zulkarnain", "npm": "24020063"},
                {"name": "Apriliano Hasta Asfirza", "npm": "24020070"},
                {"name": "Falista Nabila Saputra", "npm": "24020052"},
                {"name": "Iqma Komala Jaya", "npm": "24020056"},
                {"name": "Muhammad Rosyid", "npm": "24020077"}
            ]
            
            for dev in developers:
                st.markdown(f"""
                <div style="background: #1a1d24; padding: 15px 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #8b5cf6;">
                    <span style="font-size: 18px; font-weight: 600;">{dev['name']}</span>
                    <span style="float: right; color: #8b5cf6; font-weight: 600;">{dev['npm']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Informasi akademik
            st.markdown("""
            ### 🎓 Informasi Akademik
            - **Mata Kuliah:** Pemrograman Terstruktur
            - **Program Studi:** Sistem Informasi
            - **Tahun:** 2025
            """)
            
            # Teknologi yang digunakan
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1a1d24 0%, #2d3139 100%); 
                        padding: 35px; 
                        border-radius: 15px; 
                        margin-bottom: 30px;
                        border-left: 5px solid #14b8a6;
                        box-shadow: 0 5px 20px rgba(0,0,0,0.3);'>
                <h2 style='color: #14b8a6; font-size: 28px !important; margin-bottom: 25px !important;'>
                    💻 Teknologi yang Digunakan
                </h2>
                <div style='display: flex; flex-wrap: wrap; gap: 15px;'>
                    <span style='background: rgba(20, 184, 166, 0.15); color: #14b8a6; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #14b8a6;'>🐍 Python</span>
                    <span style='background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #ef4444;'>🎯 Streamlit</span>
                    <span style='background: rgba(59, 130, 246, 0.15); color: #3b82f6; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #3b82f6;'>🐼 Pandas</span>
                    <span style='background: rgba(168, 85, 247, 0.15); color: #a855f7; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #a855f7;'>📊 Plotly</span>
                    <span style='background: rgba(34, 197, 94, 0.15); color: #22c55e; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #22c55e;'>📱 QRCode</span>
                    <span style='background: rgba(249, 115, 22, 0.15); color: #f97316; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #f97316;'>📷 Pyzbar</span>
                    <span style='background: rgba(236, 72, 153, 0.15); color: #ec4899; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #ec4899;'>🖼️ Pillow</span>
                    <span style='background: rgba(99, 102, 241, 0.15); color: #6366f1; padding: 12px 24px; border-radius: 25px; font-size: 18px !important; font-weight: 500; border: 1px solid #6366f1;'>📑 OpenPyXL</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Footer copyright
            st.markdown("""
            <div style="text-align: center; padding: 20px; margin-top: 20px;">
                <p style="color: #b0b8c4;">© 2025 Sistem Manajemen Dokumen Kantor | v1.0.0</p>
            </div>
            """, unsafe_allow_html=True)


# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """
    Fungsi utama aplikasi
    ---------------------
    Langkah-langkah:
    1. Inisialisasi folder dan file
    2. Cek status login
    3. Routing ke halaman yang sesuai berdasarkan role
    """
    # Step 1: Inisialisasi
    init_app()
    
    # Step 2: Cek status login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Step 3: Routing berdasarkan status login
    if not st.session_state['logged_in']:
        # Belum login, tampilkan halaman login
        halaman_login()
    else:
        # Sudah login, tampilkan sidebar dan halaman utama
        # Ambil akses berdasarkan role
        access = get_user_access()
        role = st.session_state.get('role', 'viewer')
        
        with st.sidebar:
            # Logo dan judul
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h2 style="color: #8b5cf6;">📄 Dokumen QR</h2>
                <p style="margin-top: 10px;">{get_role_badge(role)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Buat daftar menu berdasarkan akses
            menu_options = access['menu']
            
            # Icon mapping
            icon_map = {
                "Lobby": "house",
                "Dashboard": "speedometer2",
                "Data Master": "folder",
                "Scan QR": "qr-code-scan",
                "Kelola QR": "qr-code",
                "Laporan": "bar-chart",
                "Pengaturan": "gear"
            }
            
            menu_icons = [icon_map.get(m, "circle") for m in menu_options]
            
            # Menu navigasi menggunakan streamlit_option_menu
            menu = option_menu(
                menu_title=None,
                options=menu_options,
                icons=menu_icons,
                default_index=0,
                styles={
                    "container": {"padding": "0", "background-color": "transparent"},
                    "icon": {"color": "#8b5cf6", "font-size": "18px"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "5px 0", "padding": "10px 15px", "border-radius": "10px"},
                    "nav-link-selected": {"background-color": "#8b5cf6", "color": "white"}
                }
            )
            
            # Update menu dari session state jika ada (dari tombol di lobby)
            if 'menu' in st.session_state:
                if st.session_state['menu'] in menu_options:
                    menu = st.session_state['menu']
                del st.session_state['menu']
            
            st.markdown("---")
            # Tampilkan info user dan tombol logout
            st.markdown(f"👤 **{st.session_state.get('username', 'Admin')}**")
            st.markdown(f"🔑 Role: **{role.upper()}**")
            
            # Tombol logout
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state['logged_in'] = False
                st.session_state.pop('username', None)
                st.session_state.pop('role', None)
                st.rerun()
        
        # Routing/render halaman berdasarkan menu yang dipilih
        if menu == "Lobby":
            halaman_lobby()
        elif menu == "Dashboard":
            halaman_dashboard()
        elif menu == "Data Master":
            halaman_data_master()
        elif menu == "Scan QR":
            halaman_scan_qr()
        elif menu == "Kelola QR":
            halaman_kelola_qr()
        elif menu == "Laporan":
            halaman_laporan()
        elif menu == "Pengaturan":
            halaman_pengaturan()

# ENTRY POINT
# Blok ini hanya dijalankan jika file dieksekusi langsung
# Tidak dijalankan jika file di-import sebagai modul
if __name__ == "__main__":
    main()
