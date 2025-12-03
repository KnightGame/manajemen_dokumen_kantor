import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Import fungsi dari utils.py
from utils import (
    load_data_dokumen, save_data_dokumen,
    create_dokumen, read_dokumen, update_dokumen, delete_dokumen,
    generate_qr_code, scan_qr_code_from_camera,
    validate_input_dokumen, search_dokumen, filter_by_jenis, filter_by_status,
    get_statistics, export_to_excel,
    create_log_entry, load_log_data
)

# ============= KONFIGURASI =============

# Path file CSV
DATA_FILE = "data/master.csv"
LOG_FILE = "data/log.csv"
QR_FOLDER = "qr"

# Buat folder jika belum ada
os.makedirs("data", exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem Manajemen Dokumen Kantor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= STYLING CSS =============

st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Dark Background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Streamlit elements dark theme */
    .stTextInput > div > div > input {
        background-color: #2d2d44;
        color: #ffffff;
        border: 1px solid #4a4a6a;
    }
    
    .stSelectbox > div > div > select {
        background-color: #2d2d44;
        color: #ffffff;
        border: 1px solid #4a4a6a;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #2d2d44;
        color: #ffffff;
        border: 1px solid #4a4a6a;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d44;
        color: #ffffff;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4a4a6a;
    }
    
    /* Lobby styling */
    .lobby-title {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .lobby-subtitle {
        font-size: 1.2rem;
        color: #b8b8d1;
        margin-top: 0.5rem;
    }
    
    /* Menu Cards - Dark */
    .menu-card {
        background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 3px solid transparent;
        height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }
    
    .menu-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0,212,255,0.4);
        border: 3px solid #00d4ff;
        background: linear-gradient(135deg, #3d3d54 0%, #2a2a3e 100%);
    }
    
    .menu-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .menu-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .menu-desc {
        font-size: 0.95rem;
        color: #b8b8d1;
        line-height: 1.5;
    }
    
    /* Stats card - Dark */
    .stat-card {
        background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,212,255,0.3);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Info box - Dark */
    .info-box {
        background: #2d2d44;
        border: 2px solid #00d4ff;
        border-left: 5px solid #00d4ff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        box-shadow: 0 5px 15px rgba(0,212,255,0.2);
    }
    
    .info-box h4 {
        color: #00d4ff;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    
    .info-box p {
        color: #e0e0e0;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .info-box ul {
        color: #b8b8d1;
        font-size: 0.95rem;
        line-height: 1.8;
        margin-left: 1.5rem;
    }
    
    .info-box ul li {
        margin-bottom: 0.5rem;
    }
    
    .info-box strong {
        color: #00d4ff;
        font-weight: 600;
    }
    
    /* Header styling - Dark */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00d4ff;
        text-align: center;
        padding: 1rem;
        background: #2d2d44;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(0,212,255,0.2);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Footer - Dark */
    .lobby-footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 2px solid #4a4a6a;
        color: #b8b8d1;
    }
    
    /* Developer card */
    .dev-card {
        background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
        border: 2px solid #00d4ff;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,212,255,0.2);
        transition: all 0.3s ease;
    }
    
    .dev-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,212,255,0.4);
        border-color: #7b2ff7;
    }
    
    .dev-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    
    .dev-nim {
        font-size: 0.95rem;
        color: #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# ============= FUNGSI HALAMAN =============

def show_lobby():
    """Menampilkan halaman lobby utama"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 5px 15px rgba(0,212,255,0.2); border: 2px solid #00d4ff;">
        <div style="font-size: 5rem; margin-bottom: 1rem;">📄</div>
        <div class="lobby-title">Sistem Manajemen Dokumen Kantor</div>
        <div class="lobby-subtitle">Kelola Dokumen Kantor dengan Mudah Menggunakan QR Code</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load statistik
    stats = get_statistics(DATA_FILE)
    
    # Tampilkan statistik
    st.markdown("### 📊 Ringkasan Data")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_dokumen']}</div>
            <div class="stat-label">Total Dokumen</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['dokumen_aktif']}</div>
            <div class="stat-label">Dokumen Aktif</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['dokumen_arsip']}</div>
            <div class="stat-label">Dokumen Arsip</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(stats['jenis_dokumen'])}</div>
            <div class="stat-label">Jenis Dokumen</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu utama
    st.markdown("### 🎯 Menu Utama")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Baris 1: Menu utama
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">📊</div>
            <div class="menu-title">Dashboard</div>
            <div class="menu-desc">Lihat statistik dan visualisasi data dokumen secara lengkap</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buka Dashboard", key="btn_dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">📁</div>
            <div class="menu-title">Data Master</div>
            <div class="menu-desc">Kelola data dokumen (Lihat, Tambah, Edit, Hapus)</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Kelola Data", key="btn_master", use_container_width=True):
            st.session_state.page = "data_master"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">📲</div>
            <div class="menu-title">Generate QR Code</div>
            <div class="menu-desc">Buat QR Code untuk setiap dokumen yang terdaftar</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Generate QR", key="btn_generate", use_container_width=True):
            st.session_state.page = "generate_qr"
            st.rerun()
    
    with col4:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">📷</div>
            <div class="menu-title">Scan QR Code</div>
            <div class="menu-desc">Scan QR Code untuk melihat detail dokumen secara cepat</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Scan QR", key="btn_scan", use_container_width=True):
            st.session_state.page = "scan_qr"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Baris 2: Menu tambahan
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">📈</div>
            <div class="menu-title">Laporan</div>
            <div class="menu-desc">Lihat laporan lengkap dan export data ke Excel</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Lihat Laporan", key="btn_laporan", use_container_width=True):
            st.session_state.page = "laporan"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">🔍</div>
            <div class="menu-title">Pencarian</div>
            <div class="menu-desc">Cari dokumen berdasarkan kata kunci atau filter</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Cari Dokumen", key="btn_search", use_container_width=True):
            st.session_state.page = "pencarian"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">⚙️</div>
            <div class="menu-title">Pengaturan</div>
            <div class="menu-desc">Atur konfigurasi sistem dan preferensi aplikasi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Pengaturan", key="btn_settings", use_container_width=True):
            st.session_state.page = "pengaturan"
            st.rerun()
    
    with col4:
        st.markdown("""
        <div class="menu-card">
            <div class="menu-icon">ℹ️</div>
            <div class="menu-title">Tentang</div>
            <div class="menu-desc">Informasi aplikasi, panduan, dan dokumentasi</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Info Aplikasi", key="btn_about", use_container_width=True):
            st.session_state.page = "tentang"
            st.rerun()
    
    # Info box
    st.markdown("""
    <div class="info-box">
        <h4>ℹ️ Informasi Penting</h4>
        <p><strong>Cara Menggunakan Aplikasi:</strong></p>
        <ul>
            <li><strong>Dashboard:</strong> Melihat statistik dan grafik data dokumen</li>
            <li><strong>Data Master:</strong> Mengelola data dokumen (CRUD)</li>
            <li><strong>Generate QR Code:</strong> Membuat QR Code untuk setiap dokumen</li>
            <li><strong>Scan QR Code:</strong> Memindai QR Code untuk melihat detail dokumen</li>
            <li><strong>Laporan:</strong> Melihat laporan lengkap dan export data</li>
        </ul>
        <p><strong>Fitur Utama:</strong></p>
        <ul>
            <li>✅ CRUD Lengkap (Create, Read, Update, Delete)</li>
            <li>✅ Generate QR Code otomatis</li>
            <li>✅ Scan QR Code dengan webcam</li>
            <li>✅ Visualisasi data dengan grafik interaktif</li>
            <li>✅ Export data ke Excel</li>
            <li>✅ Pencarian dan filter data</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="lobby-footer">
        <p><strong>Sistem Manajemen Dokumen Kantor Berbasis QR Code</strong></p>
        <p>Versi 1.0.0 | © 2025 | Pemrograman Terstruktur</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">
            Dikembangkan dengan Python & Streamlit<br>
            📧 faridfreejpn@gmail.com | 📞 +62 858-3277-7692
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_data_master():
    """Menampilkan halaman data master dengan CRUD"""
    
    st.markdown('<div class="main-header">📁 Data Master Dokumen</div>', unsafe_allow_html=True)
    
    # Tombol kembali
    if st.button("⬅️ Kembali ke Lobby"):
        st.session_state.page = "lobby"
        st.rerun()
    
    st.markdown("---")
    
    # Tab untuk operasi
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Lihat Data", "➕ Tambah", "✏️ Edit", "🗑️ Hapus", "📜 Log Aktivitas"])
    
    # TAB 1: LIHAT DATA
    with tab1:
        st.subheader("Daftar Dokumen")
        
        # Filter dan Pencarian
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            search_keyword = st.text_input("🔍 Cari Dokumen", placeholder="Masukkan kata kunci...", key="search_master")
        
        with col2:
            df_temp = load_data_dokumen(DATA_FILE)
            jenis_list = ["Semua"] + sorted(list(df_temp['Jenis_Dokumen'].unique())) if not df_temp.empty else ["Semua"]
            filter_jenis = st.selectbox("Filter Jenis", jenis_list, key="filter_jenis_master")
        
        with col3:
            status_list = ["Semua", "Aktif", "Arsip"]
            filter_status = st.selectbox("Filter Status", status_list, key="filter_status_master")
        
        with col4:
            st.write("")
            st.write("")
            if st.button("🔄 Refresh", key="refresh_master"):
                st.rerun()
        
        # Tampilkan data dengan filter
        df = load_data_dokumen(DATA_FILE)
        
        if search_keyword:
            df = search_dokumen(DATA_FILE, search_keyword)
        
        if filter_jenis != "Semua":
            df = df[df['Jenis_Dokumen'] == filter_jenis]
        
        if filter_status != "Semua":
            df = df[df['Status'] == filter_status]
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=400, hide_index=True)
            st.info(f"📊 Menampilkan {len(df)} dokumen")
        else:
            st.warning("Tidak ada data yang ditemukan")
    
    # TAB 2: TAMBAH
    with tab2:
        st.subheader("Tambah Dokumen Baru")
        
        with st.form("form_tambah", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                id_dokumen = st.text_input("ID Dokumen *", placeholder="Contoh: DOC001")
                judul = st.text_input("Judul Dokumen *", placeholder="Contoh: Laporan Tahunan 2024")
                jenis = st.selectbox("Jenis Dokumen *", [
                    "Surat", "Laporan", "Proposal", "Kontrak", 
                    "Invoice", "Memo", "Sertifikat", "Lainnya"
                ])
            
            with col2:
                lokasi = st.text_input("Lokasi Penyimpanan *", placeholder="Contoh: Lemari A - Rak 3")
                keterangan = st.text_area("Keterangan", placeholder="Keterangan tambahan (opsional)")
            
            submitted = st.form_submit_button("💾 Simpan Dokumen", type="primary", use_container_width=True)
            
            if submitted:
                # Validasi input
                valid, msg = validate_input_dokumen(id_dokumen, judul, jenis, lokasi)
                
                if valid:
                    # Simpan data
                    success, message = create_dokumen(DATA_FILE, LOG_FILE, id_dokumen, judul, jenis, lokasi, keterangan)
                    
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.error(msg)
    
    # TAB 3: EDIT
    with tab3:
        st.subheader("Edit Dokumen")
        
        df = load_data_dokumen(DATA_FILE)
        
        if not df.empty:
            # Pilih dokumen
            col1, col2 = st.columns([2, 1])
            with col1:
                id_list = df['ID_Dokumen'].tolist()
                selected_id = st.selectbox("Pilih ID Dokumen yang akan diedit", id_list, key="edit_select")
            
            with col2:
                st.write("")
                st.write("")
                if st.button("🔄 Muat Data", key="load_edit"):
                    st.rerun()
            
            if selected_id:
                # Ambil data dokumen
                doc_data = read_dokumen(DATA_FILE, selected_id)
                
                if doc_data is not None:
                    st.info(f"📝 Mengedit: **{doc_data['Judul_Dokumen']}**")
                    
                    with st.form("form_edit"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_judul = st.text_input("Judul Dokumen", value=doc_data['Judul_Dokumen'])
                            new_jenis = st.selectbox("Jenis Dokumen", [
                                "Surat", "Laporan", "Proposal", "Kontrak", 
                                "Invoice", "Memo", "Sertifikat", "Lainnya"
                            ], index=["Surat", "Laporan", "Proposal", "Kontrak", 
                                      "Invoice", "Memo", "Sertifikat", "Lainnya"].index(doc_data['Jenis_Dokumen']) if doc_data['Jenis_Dokumen'] in ["Surat", "Laporan", "Proposal", "Kontrak", "Invoice", "Memo", "Sertifikat", "Lainnya"] else 7)
                        
                        with col2:
                            new_lokasi = st.text_input("Lokasi Penyimpanan", value=doc_data['Lokasi_Penyimpanan'])
                            new_status = st.selectbox("Status", ["Aktif", "Arsip"], 
                                                     index=0 if doc_data['Status'] == "Aktif" else 1)
                        
                        new_keterangan = st.text_area("Keterangan", value=doc_data['Keterangan'])
                        
                        submitted_edit = st.form_submit_button("💾 Update Data", type="primary", use_container_width=True)
                        
                        if submitted_edit:
                            success, message = update_dokumen(
                                DATA_FILE, LOG_FILE, selected_id, 
                                judul=new_judul, 
                                jenis=new_jenis, 
                                lokasi=new_lokasi, 
                                status=new_status, 
                                keterangan=new_keterangan
                            )
                            
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
        else:
            st.warning("Belum ada data dokumen")
    
    # TAB 4: HAPUS
    with tab4:
        st.subheader("Hapus Dokumen")
        
        df = load_data_dokumen(DATA_FILE)
        
        if not df.empty:
            # Pilih dokumen
            col1, col2 = st.columns([2, 1])
            with col1:
                id_list = df['ID_Dokumen'].tolist()
                selected_id_delete = st.selectbox("Pilih ID Dokumen yang akan dihapus", id_list, key="delete_select")
            
            if selected_id_delete:
                # Tampilkan data dokumen
                doc_data = read_dokumen(DATA_FILE, selected_id_delete)
                
                if doc_data is not None:
                    st.warning(f"⚠️ Anda akan menghapus:")
                    
                    # Tampilkan detail
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {doc_data['ID_Dokumen']}")
                        st.write(f"**Judul:** {doc_data['Judul_Dokumen']}")
                        st.write(f"**Jenis:** {doc_data['Jenis_Dokumen']}")
                    with col2:
                        st.write(f"**Lokasi:** {doc_data['Lokasi_Penyimpanan']}")
                        st.write(f"**Status:** {doc_data['Status']}")
                        st.write(f"**Tanggal Input:** {doc_data['Tanggal_Input']}")
                    
                    st.markdown("---")
                    
                    # Konfirmasi hapus
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button("🗑️ Ya, Hapus", type="primary", use_container_width=True):
                            success, message = delete_dokumen(DATA_FILE, LOG_FILE, selected_id_delete)
                            
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col2:
                        if st.button("❌ Batal", use_container_width=True):
                            st.info("Penghapusan dibatalkan")
        else:
            st.warning("Belum ada data dokumen")
    
    # TAB 5: LOG AKTIVITAS
    with tab5:
        st.subheader("Log Aktivitas")
        
        df_log = load_log_data(LOG_FILE)
        
        if not df_log.empty:
            # Filter log
            col1, col2, col3 = st.columns(3)
            
            with col1:
                action_filter = st.selectbox("Filter Aksi", ["Semua", "CREATE", "UPDATE", "DELETE"])
            
            with col2:
                search_log = st.text_input("Cari ID Dokumen", placeholder="Masukkan ID...")
            
            with col3:
                st.write("")
                st.write("")
                if st.button("🔄 Refresh Log"):
                    st.rerun()
            
            # Filter data
            df_filtered = df_log.copy()
            
            if action_filter != "Semua":
                df_filtered = df_filtered[df_filtered['Action'] == action_filter]
            
            if search_log:
                df_filtered = df_filtered[df_filtered['ID_Dokumen'].str.contains(search_log, case=False, na=False)]
            
            # Tampilkan log (terbaru di atas)
            df_filtered = df_filtered.sort_values('Timestamp', ascending=False)
            st.dataframe(df_filtered, use_container_width=True, height=400, hide_index=True)
            st.info(f"📊 Total log: {len(df_filtered)} aktivitas")
        else:
            st.info("Belum ada aktivitas yang tercatat")

def show_tentang():
    """Menampilkan halaman tentang aplikasi"""
    
    st.markdown('<div class="main-header">ℹ️ Tentang Aplikasi</div>', unsafe_allow_html=True)
    
    # Tombol kembali
    if st.button("⬅️ Kembali ke Lobby"):
        st.session_state.page = "lobby"
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background: #2d2d44; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,212,255,0.2); border: 2px solid #00d4ff; color: #e0e0e0;">
    
    <h2 style="color: #00d4ff; text-align: center;">📄 Sistem Manajemen Dokumen Kantor Berbasis QR Code</h2>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">📖 Deskripsi</h3>
    <p>Aplikasi ini adalah sistem manajemen dokumen kantor yang menggunakan QR Code untuk 
    memudahkan pelacakan dan pengelolaan dokumen fisik.</p>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">✨ Fitur Utama</h3>
    <ul style="color: #b8b8d1;">
        <li>✅ <strong style="color: #00d4ff;">CRUD Lengkap:</strong> Tambah, Lihat, Edit, dan Hapus data dokumen</li>
        <li>✅ <strong style="color: #00d4ff;">Generate QR Code:</strong> Buat QR Code untuk setiap dokumen</li>
        <li>✅ <strong style="color: #00d4ff;">Scan QR Code:</strong> Scan QR Code untuk melihat detail dokumen</li>
        <li>✅ <strong style="color: #00d4ff;">Statistik Real-time:</strong> Lihat statistik dokumen secara langsung</li>
        <li>✅ <strong style="color: #00d4ff;">Pencarian & Filter:</strong> Cari dan filter dokumen dengan mudah</li>
        <li>✅ <strong style="color: #00d4ff;">Log Aktivitas:</strong> Semua aksi tercatat otomatis di log.csv</li>
    </ul>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">🛠️ Teknologi yang Digunakan</h3>
    <ul style="color: #b8b8d1;">
        <li><strong style="color: #00d4ff;">Python:</strong> Bahasa pemrograman utama</li>
        <li><strong style="color: #00d4ff;">Streamlit:</strong> Framework untuk antarmuka web</li>
        <li><strong style="color: #00d4ff;">Pandas:</strong> Pengolahan data CSV</li>
        <li><strong style="color: #00d4ff;">QRCode:</strong> Generate QR Code</li>
        <li><strong style="color: #00d4ff;">OpenCV & Pyzbar:</strong> Scan QR Code</li>
    </ul>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">📂 Struktur Data</h3>
    <p><strong style="color: #00d4ff;">master_dokumen.csv</strong> berisi kolom:</p>
    <ul style="color: #b8b8d1;">
        <li>ID_Dokumen</li>
        <li>Judul_Dokumen</li>
        <li>Jenis_Dokumen</li>
        <li>Lokasi_Penyimpanan</li>
        <li>Tanggal_Input</li>
        <li>Status</li>
        <li>Keterangan</li>
    </ul>
    
    <p><strong style="color: #00d4ff;">log_dokumen.csv</strong> berisi kolom:</p>
    <ul style="color: #b8b8d1;">
        <li>Timestamp</li>
        <li>Action (CREATE/UPDATE/DELETE)</li>
        <li>ID_Dokumen</li>
        <li>Details</li>
    </ul>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">📚 Cara Menggunakan</h3>
    <ol style="color: #b8b8d1;">
        <li><strong style="color: #00d4ff;">Tambah Dokumen:</strong> Menu Data Master → Tab "Tambah"</li>
        <li><strong style="color: #00d4ff;">Lihat Data:</strong> Menu Data Master → Tab "Lihat Data"</li>
        <li><strong style="color: #00d4ff;">Edit Dokumen:</strong> Menu Data Master → Tab "Edit"</li>
        <li><strong style="color: #00d4ff;">Hapus Dokumen:</strong> Menu Data Master → Tab "Hapus"</li>
        <li><strong style="color: #00d4ff;">Lihat Log:</strong> Menu Data Master → Tab "Log Aktivitas"</li>
        <li><strong style="color: #00d4ff;">Generate QR:</strong> Menu "Generate QR Code"</li>
        <li><strong style="color: #00d4ff;">Scan QR:</strong> Menu "Scan QR Code"</li>
    </ol>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">👨‍💻 Tim Pengembang</h3>
    <div style="margin-top: 1rem;">
        <div class="dev-card">
            <div class="dev-name">Ahmad Farid Zulkarnain</div>
            <div class="dev-nim">24020063</div>
        </div>
        <div class="dev-card">
            <div class="dev-name">Apriliano Hasta Asfirza</div>
            <div class="dev-nim">24020070</div>
        </div>
        <div class="dev-card">
            <div class="dev-name">Falista Nabila Saputra</div>
            <div class="dev-nim">24020052</div>
        </div>
        <div class="dev-card">
            <div class="dev-name">Iqma Komala Jaya</div>
            <div class="dev-nim">24020056</div>
        </div>
        <div class="dev-card">
            <div class="dev-name">Muhammad Rosyid</div>
            <div class="dev-nim">24020077</div>
        </div>
    </div>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">🎓 Informasi Akademik</h3>
    <ul style="color: #b8b8d1;">
        <li><strong style="color: #00d4ff;">Mata Kuliah:</strong> Pemrograman Terstruktur</li>
        <li><strong style="color: #00d4ff;">Program Studi:</strong> Sistem Informasi</li>
        <li><strong style="color: #00d4ff;">Tahun:</strong> 2025</li>
    </ul>
    
    <h3 style="color: #00d4ff; margin-top: 2rem;">📋 Ketentuan Teknis</h3>
    <ul style="color: #b8b8d1;">
        <li>✅ Menggunakan fungsi (def), tidak menggunakan class</li>
        <li>✅ Data disimpan di CSV (master_dokumen.csv & log_dokumen.csv)</li>
        <li>✅ Logging otomatis setiap aksi CRUD</li>
        <li>✅ Validasi input</li>
        <li>✅ Mode offline</li>
        <li>✅ Delimiter semicolon (;) untuk kompatibilitas Excel</li>
    </ul>
    
    <hr style="border-color: #4a4a6a; margin: 2rem 0;">
    
    <p style="text-align: center; color: #b8b8d1;">
        <strong style="color: #00d4ff;">© 2025 Sistem Manajemen Dokumen Kantor</strong><br>
        Versi 1.0.0 | Dikembangkan dengan ❤️ menggunakan Python & Streamlit
    </p>
    
    </div>
    """, unsafe_allow_html=True)

# ============= MAIN APP =============

def main():
    """Fungsi utama aplikasi"""
    
    # Inisialisasi session state
    if 'page' not in st.session_state:
        st.session_state.page = "lobby"
    
    # Routing halaman
    if st.session_state.page == "lobby":
        show_lobby()
    elif st.session_state.page == "data_master":
        show_data_master()
    elif st.session_state.page == "tentang":
        show_tentang()
    elif st.session_state.page == "dashboard":
        st.info("🚧 Fitur Dashboard sedang dalam pengembangan")
        if st.button("⬅️ Kembali ke Lobby"):
            st.session_state.page = "lobby"
            st.rerun()
    elif st.session_state.page == "generate_qr":
        st.info("🚧 Fitur Generate QR Code sedang dalam pengembangan")
        if st.button("⬅️ Kembali ke Lobby"):
            st.session_state.page = "lobby"
            st.rerun()
    elif st.session_state.page == "scan_qr":
        st.info("🚧 Fitur Scan QR Code sedang dalam pengembangan")
        if st.button("⬅️ Kembali ke Lobby"):
            st.session_state.page = "lobby"
            st.rerun()
    elif st.session_state.page == "laporan":
        st.info("🚧 Fitur Laporan sedang dalam pengembangan")
        if st.button("⬅️ Kembali ke Lobby"):
            st.session_state.page = "lobby"
            st.rerun()
    elif st.session_state.page == "pencarian":
        st.info("🚧 Fitur Pencarian sedang dalam pengembangan")
        if st.button("⬅️ Kembali ke Lobby"):
            st.session_state.page = "lobby"
            st.rerun()
    elif st.session_state.page == "pengaturan":
        st.info("🚧 Fitur Pengaturan sedang dalam pengembangan")
        if st.button("⬅️ Kembali ke Lobby"):
            st.session_state.page = "lobby"
            st.rerun()
    else:
        show_lobby()

# Jalankan aplikasi
if __name__ == "__main__":
    main()