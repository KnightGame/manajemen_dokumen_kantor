import streamlit as st
from utils import scan_qr_code_from_camera, read_dokumen

def show_scan_qr(data_file):
    """
    Menampilkan halaman scan QR Code
    Parameter: data_file (string)
    """
    st.markdown('<div class="main-header">📷 Scan QR Code</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Panduan
    st.markdown("""
    <div style="background: #2d2d44; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #00d4ff; margin-bottom: 2rem;">
        <h4 style="color: #00d4ff; margin-bottom: 1rem;">ℹ️ Cara Scan QR Code</h4>
        <ol style="color: #b8b8d1;">
            <li>Klik tombol "Mulai Scan QR Code"</li>
            <li>Izinkan akses kamera jika diminta</li>
            <li>Arahkan QR Code ke kamera</li>
            <li>Data dokumen akan muncul otomatis</li>
            <li>Tekan 'Q' pada keyboard untuk berhenti</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📷 Scanner")
        
        # Tombol scan
        if st.button("📷 Mulai Scan QR Code", type="primary", use_container_width=True):
            with st.spinner("Membuka kamera..."):
                scanned_id, msg = scan_qr_code_from_camera()
                
                if scanned_id:
                    st.success(msg)
                    st.session_state['scanned_id'] = scanned_id
                    st.rerun()
                else:
                    st.warning(msg)
        
        st.markdown("---")
        
        # Input manual (alternatif)
        st.markdown("### ⌨️ Input Manual (Alternatif)")
        st.caption("Jika kamera tidak tersedia, masukkan ID dokumen secara manual")
        
        manual_id = st.text_input("ID Dokumen", placeholder="Contoh: DOC001")
        if st.button("🔍 Cari", use_container_width=True):
            if manual_id:
                st.session_state['scanned_id'] = manual_id
                st.rerun()
            else:
                st.warning("Masukkan ID Dokumen terlebih dahulu")
    
    with col2:
        st.markdown("### 📄 Hasil Scan")
        
        # Tampilkan hasil scan
        if 'scanned_id' in st.session_state and st.session_state['scanned_id']:
            scanned_id = st.session_state['scanned_id']
            doc_data = read_dokumen(data_file, scanned_id)
            
            if doc_data is not None:
                # Tampilan hasil dengan styling
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%); 
                            padding: 25px; 
                            border-radius: 15px; 
                            border: 3px solid #00d4ff;
                            box-shadow: 0 8px 16px rgba(0,212,255,0.3);
                            margin: 20px 0;'>
                    <h2 style='color: #00d4ff; margin-bottom: 20px; font-size: 24px; text-align: center;'>
                        ✅ Dokumen Ditemukan!
                    </h2>
                    
                    <div style='background: #3d3d54; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00d4ff;'>
                        <p style='color: #00d4ff; margin: 0; font-size: 14px; font-weight: bold;'>ID Dokumen</p>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 18px;'>{doc_data['ID_Dokumen']}</p>
                    </div>
                    
                    <div style='background: #3d3d54; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00d4ff;'>
                        <p style='color: #00d4ff; margin: 0; font-size: 14px; font-weight: bold;'>Judul Dokumen</p>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 18px;'>{doc_data['Judul_Dokumen']}</p>
                    </div>
                    
                    <div style='background: #3d3d54; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #7b2ff7;'>
                        <p style='color: #7b2ff7; margin: 0; font-size: 14px; font-weight: bold;'>Jenis Dokumen</p>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 16px;'>{doc_data['Jenis_Dokumen']}</p>
                    </div>
                    
                    <div style='background: #3d3d54; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #7b2ff7;'>
                        <p style='color: #7b2ff7; margin: 0; font-size: 14px; font-weight: bold;'>Lokasi Penyimpanan</p>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 16px;'>{doc_data['Lokasi_Penyimpanan']}</p>
                    </div>
                    
                    <div style='background: #3d3d54; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00d4ff;'>
                        <p style='color: #00d4ff; margin: 0; font-size: 14px; font-weight: bold;'>Status</p>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 16px;'>{doc_data['Status']}</p>
                    </div>
                    
                    <div style='background: #3d3d54; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00d4ff;'>
                        <p style='color: #00d4ff; margin: 0; font-size: 14px; font-weight: bold;'>Tanggal Input</p>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 16px;'>{doc_data['Tanggal_Input']}</p>
                    </div>
                    
                    <div style='background: #3d3d54; padding: 15px; border-radius: 8px; border-left: 4px solid #7b2ff7;'>
                        <p style='color: #7b2ff7; margin: 0; font-size: 14px; font-weight: bold;'>Keterangan</p>
                        <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 16px;'>{doc_data['Keterangan']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Tombol aksi
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🔄 Scan Lagi", use_container_width=True):
                        del st.session_state['scanned_id']
                        st.rerun()
                
                with col_b:
                    if st.button("🗑️ Clear", use_container_width=True):
                        del st.session_state['scanned_id']
                        st.rerun()
                
            else:
                st.error(f"❌ Dokumen dengan ID '{scanned_id}' tidak ditemukan dalam database!")
                
                if st.button("🔄 Coba Lagi", use_container_width=True):
                    del st.session_state['scanned_id']
                    st.rerun()
        else:
            st.info("📷 Belum ada QR Code yang di-scan. Klik tombol 'Mulai Scan' untuk memulai.")
    
    st.markdown("---")
    
    # Tips
    st.markdown("""
    <div style="background: #2d2d44; padding: 1rem; border-radius: 10px; border-left: 5px solid #7b2ff7;">
        <h4 style="color: #7b2ff7; margin-bottom: 0.5rem;">💡 Tips</h4>
        <ul style="color: #b8b8d1; font-size: 0.9rem;">
            <li>Pastikan pencahayaan cukup untuk scan yang optimal</li>
            <li>Posisikan QR Code tegak lurus dengan kamera</li>
            <li>Jaga jarak 10-20 cm dari kamera</li>
            <li>QR Code harus dalam kondisi baik (tidak rusak/buram)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
