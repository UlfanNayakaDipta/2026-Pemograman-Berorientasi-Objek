import streamlit as st
import datetime
import pandas as pd

def format_rp(angka):
    return f"Rp {angka or 0:,.0f}".replace(",", ".")

from model import Transaksi
from manajer_anggaran import AnggaranHarian
from konfigurasi import KATEGORI_PENGELUARAN

st.set_page_config(page_title="Catatan Pengeluaran", layout="wide")

@st.cache_resource
def get_anggaran_manager():
    return AnggaranHarian()

anggaran = get_anggaran_manager()

# Halaman Input
def halaman_input():
    st.header("➕ Tambah Pengeluaran Baru")
    with st.form("form_transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            deskripsi = st.text_input("Deskripsi*", placeholder="Contoh: Makan siang")
        with col2:
            kategori = st.selectbox("Kategori*:", KATEGORI_PENGELUARAN, index=0)
        
        col3, col4 = st.columns([1, 1])
        with col3:
            jumlah = st.number_input("Jumlah (Rp)*:", min_value=0.01, step=1000.0, format="%.0f")
        with col4:
            tanggal = st.date_input("Tanggal*:", value=datetime.date.today())
        
        submitted = st.form_submit_button("💾 Simpan Transaksi")
        if submitted:
            if not deskripsi:
                st.warning("Deskripsi wajib!")
            elif jumlah <= 0:
                st.warning("Jumlah wajib!")
            else:
                tx = Transaksi(deskripsi, float(jumlah), kategori, tanggal)
                if anggaran.tambah_transaksi(tx):
                    st.success("Berhasil disimpan!")
                    st.rerun()
                else:
                    st.error("Gagal menyimpan.")

# Halaman Riwayat
def halaman_riwayat():
    st.subheader("📋 Detail Semua Transaksi")
    
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
    
    df_transaksi = anggaran.get_dataframe_transaksi()
    
    if df_transaksi.empty:
        st.info("Belum ada transaksi.")
    else:
        st.dataframe(df_transaksi, use_container_width=True, hide_index=True)
    
    # Fitur Hapus
    st.divider()
    st.subheader("🗑️ Hapus Transaksi")
    id_hapus = st.number_input("ID Transaksi:", min_value=1, step=1)
    if st.button("Hapus"):
        if anggaran.hapus_transaksi(int(id_hapus)):
            st.success(f"ID {id_hapus} berhasil dihapus!")
            st.rerun()
        else:
            st.error("Gagal hapus. Pastikan ID benar.")

# Halaman Ringkasan
def halaman_ringkasan():
    st.subheader("📊 Ringkasan Pengeluaran")
    
    pilihan = st.selectbox("Filter:", ["Semua Waktu", "Hari Ini"])
    tanggal_filter = datetime.date.today() if pilihan == "Hari Ini" else None
    
    total = anggaran.hitung_total_pengeluaran(tanggal_filter)
    st.metric("Total Pengeluaran", format_rp(total))
    
    st.divider()
    st.subheader("Pengeluaran per Kategori")
    
    kategori_data = anggaran.get_pengeluaran_per_kategori(tanggal_filter)
    
    if not kategori_data:
        st.info("Tidak ada data.")
    else:
        df_kat = pd.DataFrame(list(kategori_data.items()), columns=['Kategori', 'Total'])
        st.dataframe(df_kat, use_container_width=True, hide_index=True)
        st.bar_chart(df_kat.set_index('Kategori'))

# Main
def main():
    st.sidebar.title("📓 Catatan Pengeluaran")
    menu = st.sidebar.radio("Menu:", ["Tambah", "Riwayat", "Ringkasan"])
    
    if menu == "Tambah":
        halaman_input()
    elif menu == "Riwayat":
        halaman_riwayat()
    else:
        halaman_ringkasan()

if __name__ == "__main__":
    main()