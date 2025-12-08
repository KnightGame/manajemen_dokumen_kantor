import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data_dokumen, get_statistics

def create_pie_chart_jenis(data_file):
    """
    Membuat pie chart distribusi jenis dokumen
    Parameter: data_file (string)
    Return: figure plotly
    """
    try:
        df = load_data_dokumen(data_file)
        
        if df.empty:
            return None
        
        # Hitung distribusi jenis
        jenis_count = df['Jenis_Dokumen'].value_counts()
        
        # Buat pie chart
        fig = px.pie(
            values=jenis_count.values,
            names=jenis_count.index,
            title='Distribusi Jenis Dokumen',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

def create_bar_chart_status(data_file):
    """
    Membuat bar chart status dokumen
    Parameter: data_file (string)
    Return: figure plotly
    """
    try:
        df = load_data_dokumen(data_file)
        
        if df.empty:
            return None
        
        # Hitung status
        status_count = df['Status'].value_counts()
        
        # Buat bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=status_count.index,
                y=status_count.values,
                marker_color=['#00d4ff', '#7b2ff7']
            )
        ])
        
        fig.update_layout(
            title='Status Dokumen',
            xaxis_title='Status',
            yaxis_title='Jumlah',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

def create_bar_chart_lokasi(data_file):
    """
    Membuat bar chart distribusi lokasi
    Parameter: data_file (string)
    Return: figure plotly
    """
    try:
        df = load_data_dokumen(data_file)
        
        if df.empty:
            return None
        
        # Hitung lokasi (top 10)
        lokasi_count = df['Lokasi_Penyimpanan'].value_counts().head(10)
        
        # Buat horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=lokasi_count.index,
                x=lokasi_count.values,
                orientation='h',
                marker_color='#00d4ff'
            )
        ])
        
        fig.update_layout(
            title='Top 10 Lokasi Penyimpanan',
            xaxis_title='Jumlah Dokumen',
            yaxis_title='Lokasi',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

def create_line_chart_timeline(data_file):
    """
    Membuat line chart timeline penambahan dokumen
    Parameter: data_file (string)
    Return: figure plotly
    """
    try:
        df = load_data_dokumen(data_file)
        
        if df.empty:
            return None
        
        # Convert tanggal ke datetime
        df['Tanggal_Input'] = pd.to_datetime(df['Tanggal_Input'])
        
        # Group by tanggal
        timeline = df.groupby(df['Tanggal_Input'].dt.date).size().reset_index(name='Jumlah')
        
        # Buat line chart
        fig = px.line(
            timeline,
            x='Tanggal_Input',
            y='Jumlah',
            title='Timeline Penambahan Dokumen',
            markers=True
        )
        
        fig.update_layout(
            xaxis_title='Tanggal',
            yaxis_title='Jumlah Dokumen',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0')
        )
        
        fig.update_traces(line_color='#00d4ff', marker_color='#7b2ff7')
        
        return fig
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

def show_dashboard(data_file):
    """
    Menampilkan halaman dashboard
    Parameter: data_file (string)
    """
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Load statistik
    stats = get_statistics(data_file)
    
    # Statistik Cards
    st.markdown("### 📈 Statistik Umum")
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
    
    # Grafik Row 1
    st.markdown("### 📊 Visualisasi Data")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_jenis = create_pie_chart_jenis(data_file)
        if fig_jenis:
            st.plotly_chart(fig_jenis, use_container_width=True)
        else:
            st.info("Belum ada data untuk ditampilkan")
    
    with col2:
        fig_status = create_bar_chart_status(data_file)
        if fig_status:
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Belum ada data untuk ditampilkan")
    
    # Grafik Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        fig_lokasi = create_bar_chart_lokasi(data_file)
        if fig_lokasi:
            st.plotly_chart(fig_lokasi, use_container_width=True)
        else:
            st.info("Belum ada data untuk ditampilkan")
    
    with col2:
        fig_timeline = create_line_chart_timeline(data_file)
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Belum ada data untuk ditampilkan")
    
    st.markdown("---")
    
    # Tabel Data Terbaru
    st.markdown("### 📋 10 Dokumen Terbaru")
    df = load_data_dokumen(data_file)
    if not df.empty:
        st.dataframe(df.tail(10).sort_values('Tanggal_Input', ascending=False), 
                    use_container_width=True, 
                    hide_index=True)
    else:
        st.info("Belum ada dokumen yang terdaftar")
