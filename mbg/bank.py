import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Nama file JSON untuk menyimpan seluruh data aplikasi
nama_file = "riwayat_duid.json"

# Jumlah transaksi yang ditampilkan per halaman
page = 10

# Daftar jenis transaksi untuk filter mutasi
validitas = {
    "1": "Transfer Bank",
    "2": "Virtual Account",
    "3": "Top Up",
    "4": "Setor Tunai"
}

# ══════════════════════════════════════════════════════════════════════════════════════
# BAGIAN BANTUAN DETEKSI PEMASUKAN
# ══════════════════════════════════════════════════════════════════════════════════════

def is_pemasukan(t: dict) -> bool:
    """
    Fungsi pintar untuk mendeteksi apakah transaksi adalah Pemasukan.
    Jika ada kata 'setor', 'tunai', 'cash', atau 'top up' pada jenis atau bank, 
    maka dianggap Pemasukan.
    """
    teks_pencarian = (str(t.get('jenis', '')) + " " + str(t.get('bank', ''))).lower()
    kata_kunci = ['top up', 'setor', 'tunai', 'cash', 'pemasukan', 'terima']
    
    return any(kata in teks_pencarian for kata in kata_kunci)

# ══════════════════════════════════════════════════════════════════════════════════════
# rid n writ
# ══════════════════════════════════════════════════════════════════════════════════════

def baca_data() -> dict:
    default = {"saldo": 0.0, "transaksi": []}
    if not os.path.exists(nama_file):
        return default
    with open(nama_file, "r") as f:
        try:
            data = json.load(f)
            if "saldo" not in data:
                data["saldo"] = 0.0
            if "transaksi" not in data:
                data["transaksi"] = []
            return data
        except json.JSONDecodeError:
            print("  ⚠ File data rusak, membuat ulang data kosong.")
            return default

def simpan_data(data: dict):
    with open(nama_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def baca_saldo() -> float:
    return baca_data()["saldo"]

def baca_transaksi() -> list:
    return baca_data()["transaksi"]

# ══════════════════════════════════════════════════════════════════════════════════════
# client
# ══════════════════════════════════════════════════════════════════════════════════════

def cetak_header():
    print(f"\n{'No':<4} {'Tanggal':<20} {'Nama':<18} {'No. Rek/VA':<15} "
          f"{'Nominal':>18} {'Bank':<10} {'Jenis'}")
    print("─" * 105)

def cetak_baris(i, t):
    try:
        nominal_val = int(float(t['nominal']))
        if is_pemasukan(t):
            nominal_fmt = f"+ Rp {nominal_val:>11,}"  # Tanda + untuk uang masuk
        else:
            nominal_fmt = f"- Rp {nominal_val:>11,}"  # Tanda - untuk uang keluar
    except (ValueError, KeyError):
        nominal_fmt = f"{'??':>18}"

    print(f"{i:<4} {t['tanggal']:<20} {t['nama']:<18} {t['rek']:<15} "
          f"{nominal_fmt}  {t['bank']:<10} {t['jenis']}")

def cetak_pagination(data, judul=""):
    if not data:
        print("  (Tidak ada data.)")
        return

    total     = len(data)
    total_hal = (total + page - 1) // page
    halaman   = 1

    while True:
        mulai    = (halaman - 1) * page
        akhir    = mulai + page
        potongan = data[mulai:akhir]

        if judul:
            print(f"\n─── {judul} ───")

        print(f"  Halaman {halaman}/{total_hal}  |  Total: {total} transaksi")
        cetak_header()

        for i, t in enumerate(potongan, mulai + 1):
            cetak_baris(i, t)

        if total_hal == 1:
            break

        print(f"\n  [N] Halaman Berikutnya  [P] Halaman Sebelumnya  [Q] Kembali")
        nav = input("  Navigasi: ").strip().upper()

        if nav == "N":
            if halaman < total_hal:
                halaman += 1
            else:
                print("  Sudah di halaman terakhir.")
        elif nav == "P":
            if halaman > 1:
                halaman -= 1
            else:
                print("  Sudah di halaman pertama.")
        elif nav == "Q":
            break
        else:
            print("  Pilihan tidak valid.")
            break

# ══════════════════════════════════════════════════════════════════════════════════════
# palisade
# ══════════════════════════════════════════════════════════════════════════════════════

def input_nama(label):
    while True:
        nilai = input(label).strip()
        if not nilai:
            print("  Tidak boleh kosong.")
        elif any(c.isdigit() for c in nilai):
            print("  Nama tidak boleh mengandung angka.")
        else:
            return nilai

def input_nominal():
    while True:
        raw = input("Nominal (Rp)          : ").strip().replace(",", "").replace(".", "")
        try:
            nilai = float(raw)
            if nilai <= 0:
                print("  Nominal harus lebih dari 0.")
            else:
                return nilai
        except ValueError:
            print("  Input tidak valid, masukkan angka saja.")

def input_rek():
    while True:
        rek = input("Nomor rekening        : ").strip()
        if rek.isdigit() and len(rek) == 10:
            return rek
        print("  Nomor rekening harus tepat 10 digit angka.")

def input_va():
    while True:
        va = input("Nomor Virtual Account : ").strip()
        if va.isdigit() and len(va) >= 8:
            return va
        print("  Nomor VA tidak valid (harus angka, minimal 8 digit).")

def konfirmasi(pesan="Simpan transaksi ini? (y/n): "):
    while True:
        jwb = input(pesan).strip().lower()
        if jwb in ("y", "n"):
            return jwb == "y"
        print("  Masukkan 'y' untuk Ya atau 'n' untuk Tidak.")

# ══════════════════════════════════════════════════════════════════════════════════════
# te ep dan top up
# ══════════════════════════════════════════════════════════════════════════════════════

def transfer_bank():
    print("\n=== TRANSFER BANK ===")
    data  = baca_data()
    saldo = data["saldo"]
    
    print(f"\n  Saldo tersedia : Rp {saldo:,.0f}")
    if saldo <= 0:
        print("  Saldo Anda tidak mencukupi.")
        return

    jenis   = "Transfer Bank"
    nama    = input_nama("Nama pemilik rekening : ")
    rek     = input_rek()
    bank    = input_nama("Nama bank             : ")
    nominal = input_nominal()

    if nominal > saldo:
        print(f"\n  ✗ Saldo tidak mencukupi. Maksimum: Rp {saldo:,.0f}")
        return

    print("\n┌─── Ringkasan Transaksi ────────────────────┐")
    print(f"│  Jenis   : {jenis}")
    print(f"│  Nama    : {nama}")
    print(f"│  Rek     : {rek}")
    print(f"│  Bank    : {bank}")
    print(f"│  Nominal : Rp {int(nominal):,}")
    print(f"│  Sisa Saldo: Rp {saldo - nominal:,.0f}")
    print("└────────────────────────────────────────────┘")

    if not konfirmasi("Lanjutkan transfer? (y/n): "):
        print("  Transaksi dibatalkan.")
        return

    transaksi_baru = {
        "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nama"   : nama,
        "rek"    : rek,
        "nominal": int(nominal),
        "bank"   : bank,
        "jenis"  : jenis
    }

    data["transaksi"].append(transaksi_baru)
    data["saldo"] = saldo - nominal
    simpan_data(data)

    print(f"\n✓ Transfer sebesar Rp {int(nominal):,} berhasil dikirim.")
    print(f"  Saldo tersisa : Rp {data['saldo']:,.0f}")


def virtual_account():
    print("\n=== VIRTUAL ACCOUNT ===")
    data  = baca_data()
    saldo = data["saldo"]
    
    print(f"\n  Saldo tersedia : Rp {saldo:,.0f}")
    if saldo <= 0:
        print("  Saldo Anda tidak mencukupi.")
        return

    jenis    = "Virtual Account"
    provider = input_nama("E-Wallet : ")
    no_va    = input_va()
    nominal  = input_nominal()

    if nominal > saldo:
        print(f"\n  ✗ Saldo tidak mencukupi. Maksimum: Rp {saldo:,.0f}")
        return

    print("\n┌─── Ringkasan Pembayaran VA ────────────────┐")
    print(f"│  Layanan : {provider}")
    print(f"│  No. VA  : {no_va}")
    print(f"│  Nominal : Rp {int(nominal):,}")
    print(f"│  Sisa Saldo: Rp {saldo - nominal:,.0f}")
    print("└────────────────────────────────────────────┘")

    if not konfirmasi("Lanjutkan pembayaran VA? (y/n): "):
        print("  Pembayaran dibatalkan.")
        return

    transaksi_baru = {
        "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nama"   : provider,
        "rek"    : no_va,
        "nominal": int(nominal),
        "bank"   : "VA",
        "jenis"  : jenis
    }

    data["transaksi"].append(transaksi_baru)
    data["saldo"] = saldo - nominal
    simpan_data(data)

    print(f"\n✓ Pembayaran VA ke {provider} sebesar Rp {int(nominal):,} berhasil.")
    print(f"  Saldo tersisa : Rp {data['saldo']:,.0f}")

# ══════════════════════════════════════════════════════════════════════════════════════
# riwayat
# ══════════════════════════════════════════════════════════════════════════════════════

def cek_rekap_keuangan():
    print("\n=== CEK PEMASUKAN & PENGELUARAN ===")
    transaksi = baca_transaksi()

    if not transaksi:
        print("Belum ada transaksi.")
        return

    total_masuk = 0.0
    per_jenis_keluar = defaultdict(float)

    for t in transaksi:
        if is_pemasukan(t):
            total_masuk += float(t['nominal'])
        else:
            per_jenis_keluar[t['jenis']] += float(t['nominal'])

    total_keluar = sum(per_jenis_keluar.values())

    print("\n  [ TOTAL PEMASUKAN (+)]")
    print(f"  Setor Tunai : Rp {total_masuk:>15,.0f}")
    
    print("\n  [ TOTAL PENGELUARAN (-)]")
    if not per_jenis_keluar:
        print("  (Belum ada pengeluaran)")
    else:
        for jenis, jumlah in per_jenis_keluar.items():
            print(f"  {jenis:<20} : Rp {jumlah:>15,.0f}")
    
    print(f"  {'─' * 42}")
    print(f"  {'TOTAL PENGELUARAN':<20} : Rp {total_keluar:>15,.0f}")


def menu_laporan():
    while True:
        print("\n=== LAPORAN KEUANGAN ===")
        print("1. Ringkasan per Bulan (Pemasukan dan Pengeluaran)")
        print("2. Ringkasan per Bank/Layanan (hanya Pengeluaran)")
        print("3. Kembali")
        pilih     = input("Pilih opsi (1-3): ").strip()
        transaksi = baca_transaksi()

        if pilih == '1':
            if not transaksi:
                print("Belum ada transaksi.")
                continue

            per_bulan = defaultdict(lambda: {"masuk": 0.0, "keluar": 0.0})
            
            for t in transaksi:
                bulan = t['tanggal'][:7]
                if is_pemasukan(t):
                    per_bulan[bulan]["masuk"] += float(t['nominal'])
                else:
                    per_bulan[bulan]["keluar"] += float(t['nominal'])

            print(f"\n  {'Bulan':<10} | {'Pemasukan (+)':>18} | {'Pengeluaran (-)':>18}")
            print("  " + "─" * 54)
            for bulan in sorted(per_bulan):
                masuk = per_bulan[bulan]["masuk"]
                keluar = per_bulan[bulan]["keluar"]
                print(f"  {bulan:<10} | Rp {masuk:>15,.0f} | Rp {keluar:>15,.0f}")

        elif pilih == '2':
            if not transaksi:
                print("Belum ada transaksi.")
                continue

            per_bank = defaultdict(lambda: defaultdict(float))
            for t in transaksi:
                if not is_pemasukan(t):
                    per_bank[t['bank']][t['jenis']] += float(t['nominal'])

            print()
            for bank in sorted(per_bank):
                subtotal = sum(per_bank[bank].values())
                print(f"  [ {bank} ]")
                for jenis, jumlah in per_bank[bank].items():
                    print(f"    {jenis:<15}: Rp {jumlah:>13,.0f}")
                print(f"    {'Subtotal':<15}: Rp {subtotal:>13,.0f}")
                print()

        elif pilih == '3':
            break
        else:
            print("Opsi tidak valid.")


def menu_tampilan():
    while True:
        print("\n=== Mutasi Rekening ===")
        print("1. Tampilkan Semua Riwayat")
        print("2. Tampilkan Berdasarkan Jenis Transaksi")
        print("3. Tampilkan Berdasarkan Tanggal")
        print("4. Tampilkan Berdasarkan Nominal")
        print("5. Kembali ke Menu Utama")
        pilih     = input("Pilih opsi (1-5): ").strip()
        transaksi = baca_transaksi()

        if pilih == '1':
            cetak_pagination(transaksi, "Semua Transaksi")

        elif pilih == '2':
            print("\n  Pilih Filter:")
            for k, v in validitas.items():
                print(f"  {k}. {v}")
            pilih_jenis = input("Pilih jenis (1-4): ").strip()
            
            if pilih_jenis not in validitas:
                print("  Pilihan tidak valid.")
                continue
                
            jenis = validitas[pilih_jenis]
            hasil = [t for t in transaksi if t['jenis'] == jenis or (jenis == "Setor Tunai" and is_pemasukan(t))]
            cetak_pagination(hasil, f"Mutasi: {jenis}")

        elif pilih == '3':
            urutan = sorted(transaksi, key=lambda x: x['tanggal'], reverse=True)
            cetak_pagination(urutan, "Urutan Berdasarkan Tanggal (Terbaru → Terlama)")

        elif pilih == '4':
            try:
                urutan = sorted(transaksi, key=lambda x: float(x['nominal']), reverse=True)
            except ValueError:
                urutan = transaksi
            cetak_pagination(urutan, "Urutan Berdasarkan Nominal (Terbesar → Terkecil)")

        elif pilih == '5':
            break
        else:
            print("Opsi tidak valid. Silakan pilih antara 1-5.")


def hapus_transaksi_lama():
    print("\n=== HAPUS TRANSAKSI LEBIH DARI 2 BULAN ===")
    data      = baca_data()
    transaksi = data["transaksi"]

    if not transaksi:
        print("Belum ada transaksi.")
        return

    batas         = datetime.now() - timedelta(days=60)
    akan_dihapus  = []
    akan_disimpan = []

    for t in transaksi:
        try:
            tgl = datetime.strptime(t['tanggal'], "%Y-%m-%d %H:%M:%S")
            if tgl < batas:
                akan_dihapus.append(t)
            else:
                akan_disimpan.append(t)
        except ValueError:
            akan_disimpan.append(t)

    if not akan_dihapus:
        print(f"  Tidak ada transaksi yang lebih dari 2 bulan (sebelum {batas.strftime('%Y-%m-%d')}).")
        return

    print(f"\n  Ditemukan {len(akan_dihapus)} transaksi sebelum {batas.strftime('%Y-%m-%d')} yang akan dihapus:\n")
    cetak_header()
    for i, t in enumerate(akan_dihapus, 1):
        cetak_baris(i, t)

    if not konfirmasi(f"Hapus {len(akan_dihapus)} transaksi lama ini? (y/n): "):
        print("  Penghapusan dibatalkan.")
        return

    data["transaksi"] = akan_disimpan
    simpan_data(data)
    print(f"\n✓ {len(akan_dihapus)} transaksi lama berhasil dihapus.")
    print(f"  {len(akan_disimpan)} transaksi tersisa dalam riwayat.")


# ══════════════════════════════════════════════════════════════════════════════════════
# utama
# ══════════════════════════════════════════════════════════════════════════════════════

def main():
    while True:
        saldo = baca_saldo()

        print("\n╔══════════════════════════════════════╗")
        print(f"║     RIWAYAT TRANSAKSI REKENING       ║")
        print(f"║  Saldo Anda : Rp {saldo:>17,.0f}   ║")
        print("╚══════════════════════════════════════╝")
        print("1. Transfer Bank")
        print("2. Virtual Account")
        print("3. Mutasi Rekening")
        print("4. Cek Pemasukan & Pengeluaran")
        print("5. Laporan Keuangan (Bulanan)")
        print("6. Hapus Transaksi Lama (>2 Bulan)")
        print("7. Keluar")

        pilihan = input("Pilih Menu: ").strip()

        if pilihan == '1':
            transfer_bank()
        elif pilihan == '2':
            virtual_account()
        elif pilihan == '3':
            menu_tampilan()
        elif pilihan == '4':
            cek_rekap_keuangan()
        elif pilihan == '5':
            menu_laporan()
        elif pilihan == '6':
            hapus_transaksi_lama()
        elif pilihan == '7':
            print("Sistem Berhenti. Data Anda aman di 'riwayat_duid.json'")
            break
        else:
            print("Pilihan tidak valid. Masukkan angka 1-7.")

if __name__ == "__main__":
    main()