import datetime
import pandas as pd
from model import Transaksi
import database

class AnggaranHarian:
    _db_setup_done = False
    
    def __init__(self):
        if not AnggaranHarian._db_setup_done:
            print("[AnggaranHarian] Setup database...")
            if database.setup_database_initial():
                AnggaranHarian._db_setup_done = True
                print("[AnggaranHarian] Database siap.")
    
    def tambah_transaksi(self, transaksi: Transaksi) -> bool:
        if not isinstance(transaksi, Transaksi) or transaksi.jumlah <= 0:
            return False
        sql = "INSERT INTO transaksi (deskripsi, jumlah, kategori, tanggal) VALUES (?, ?, ?, ?)"
        params = (transaksi.deskripsi, transaksi.jumlah, transaksi.kategori, 
                  transaksi.tanggal.strftime("%Y-%m-%d"))
        last_id = database.execute_query(sql, params)
        if last_id is not None:
            transaksi.id = last_id
            return True
        return False
    
    def get_dataframe_transaksi(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = "SELECT tanggal, kategori, deskripsi, jumlah FROM transaksi"
        params = None
        if filter_tanggal:
            query += " WHERE tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)
        query += " ORDER BY tanggal DESC, id DESC"
        df = database.get_dataframe(query, params=params)
        if not df.empty:
            df['Jumlah (Rp)'] = df['jumlah'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            df = df[['tanggal', 'kategori', 'deskripsi', 'Jumlah (Rp)']]
        return df
    
    def hitung_total_pengeluaran(self, tanggal: datetime.date | None = None) -> float:
        sql = "SELECT SUM(jumlah) FROM transaksi"
        params = None
        if tanggal:
            sql += " WHERE tanggal = ?"
            params = (tanggal.strftime("%Y-%m-%d"),)
        result = database.fetch_query(sql, params=params, fetch_all=False)
        if result and result[0] is not None:
            return float(result[0])
        return 0.0
    
    def get_pengeluaran_per_kategori(self, tanggal: datetime.date | None = None) -> dict:
        hasil = {}
        sql = "SELECT kategori, SUM(jumlah) FROM transaksi"
        params = []
        if tanggal:
            sql += " WHERE tanggal = ?"
            params.append(tanggal.strftime("%Y-%m-%d"))
        sql += " GROUP BY kategori HAVING SUM(jumlah) > 0 ORDER BY SUM(jumlah) DESC"
        rows = database.fetch_query(sql, params=tuple(params) if params else None, fetch_all=True)
        if rows:
            for row in rows:
                kategori = row['kategori'] if row['kategori'] else "Lainnya"
                jumlah = float(row[1]) if row[1] is not None else 0.0
                hasil[kategori] = jumlah
        return hasil
    
    # TAMBAHKAN INI UNTUK PENUGASAN HAPUS
    def hapus_transaksi(self, id_transaksi: int) -> bool:
        if not isinstance(id_transaksi, int) or id_transaksi <= 0:
            return False
        sql = "DELETE FROM transaksi WHERE id = ?"
        result = database.execute_query(sql, (id_transaksi,))
        return result is not None
    
    