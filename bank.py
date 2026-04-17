import os
from datetime import datetime, timedelta
from collections import defaultdict

# nama file pnyimpanan data transaksi
nama_file    = "riwayat_duid.txt"
page  = 10   # jumlah baris per halaman pagination

# pilihan jenis transaksi yang tersedia
validitas = {
    "1": "Transfer",
    "2": "Pembayaran"
}

# semua nya dihitung sebagai pengeluaran
output = {"Transfer", "Pembayaran"}

# ══════════════════════════════════════════════════════════════════════════════════════
# fungsi untuk membaca dan menyimpan data transaksi ke file
# ══════════════════════════════════════════════════════════════════════════════════════

def baca_transaksi():
    """
    baca semua transaksi dari file. return list of dict.
    """
    # jika file belum ada, kembalikan list kosong
    transaksi = []
    if not os.path.exists(nama_file):
        return transaksi
    with open(nama_file, "r") as f:
        for baris in f:
            baris = baris.strip()
            if not baris:
                continue # lewati baris kosong
            bagian = baris.split(",")
            if len(bagian) < 6:
                continue # lewati baris yang tidak lengkap
            transaksi.append({
                "tanggal": bagian[0],
                "nama"   : bagian[1],
                "rek"    : bagian[2],
                "nominal": bagian[3],
                "bank"   : bagian[4],
                "jenis"  : bagian[5]
            })
    return transaksi


def simpan_transaksi(data: dict):
    """Tambah satu baris transaksi ke file."""
    with open(nama_file, "a") as f:
        f.write(
            f"{data['tanggal']},{data['nama']},{data['rek']},"
            f"{data['nominal']},{data['bank']},{data['jenis']}\n"
        )


def tulis_ulang_semua(daftar: list):
    """Timpa seluruh isi file dengan daftar transaksi yang diberikan."""
    with open(nama_file, "w") as f:
        for t in daftar:
            f.write(
                f"{t['tanggal']},{t['nama']},{t['rek']},"
                f"{t['nominal']},{t['bank']},{t['jenis']}\n"
            )


# ═══════════════════════════════════════════
# tampilan data
# ═══════════════════════════════════════════

def cetak_header():
    print(f"\n{'No':<4} {'Tanggal':<20} {'Nama':<18} {'No. Rek':<13} "
        f"{'Nominal':>16} {'Bank':<10} {'Jenis'}")
    print("─" * 95)


def cetak_baris(i, t):
    try:
        nominal_fmt = f"Rp {int(float(t['nominal'])):>13,}"
    except ValueError:
        nominal_fmt = f"{'??':>16}" # jika nominal tidak bisa diubah ke angka, tampilkan '??'
    print(f"{i:<4} {t['tanggal']:<20} {t['nama']:<18} {t['rek']:<13} "
        f"{nominal_fmt} {t['bank']:<10} {t['jenis']}")


def cetak_pagination(data, judul=""):
    """Tampilkan data dengan pagination 10 baris per halaman."""
    if not data:
        print("  (Tidak ada data.)")
        return

    total       = len(data)
    total_hal   = (total + page - 1) // page # hitung jumlah halaman
    halaman     = 1

    while True:
        # hitung indeks untuk potongan data yang akan ditampilkan
        mulai    = (halaman - 1) * page
        akhir    = mulai + page
        potongan = data[mulai:akhir]

        if judul:
            print(f"\n─── {judul} ───")
        print(f"  Halaman {halaman}/{total_hal}  |  Total: {total} transaksi")
        cetak_header()
        for i, t in enumerate(potongan, mulai + 1):
            cetak_baris(i, t)

        # jika hanya ada 1 halaman, tidak perlu menampilkan navigasi
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


# ═══════════════════════════════════════════
# validasi input
# ═══════════════════════════════════════════

def input_nama(label):
    """Input nama — tidak boleh kosong dan tidak boleh berisi angka."""
    while True:
        nilai = input(label).strip()
        if not nilai:
            print("  Tidak boleh kosong.")
        elif any(c.isdigit() for c in nilai): # cek jika ada karakter angka
            print("  Nama tidak boleh mengandung angka.")
        else:
            return nilai


def input_nominal():
    """Input nominal — harus angka positif."""
    while True:
        # menghapus tanda koma dan titik agar bisa dikonversi ke float
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
    """Input nomor rekening — harus tepat 10 digit angka."""
    while True:
        rek = input("Nomor rekening        : ").strip()
        if rek.isdigit() and len(rek) == 10:
            return rek
        print("  Nomor rekening harus tepat 10 digit angka.")


def konfirmasi(pesan="Simpan transaksi ini? (y/n): "):
    """Minta konfirmasi y/n dari user."""
    while True:
        jwb = input(pesan).strip().lower()
        if jwb in ("y", "n"):
            return jwb == "y"
        print("  Masukkan 'y' untuk Ya atau 'n' untuk Tidak.")


# ═══════════════════════════════════════════
# fungsi utama 
# ═══════════════════════════════════════════

def tambah_transaksi():
    print("\n=== INPUT TRANSAKSI BARU ===")

    # mengumpulkan semua input terlebih dahulu, baru tampilkan ringkasan untuk konfirmasi
    nama    = input_nama("Nama pemilik rekening : ")
    rek     = input_rek()
    bank    = input_nama("Nama bank             : ")
    nominal = input_nominal()

    # pilih jenis transaksi
    print("\nJenis Transaksi:")
    for k, v in validitas.items():
        print(f"  {k}. {v}")
    while True:
        pilih_jenis = input("Pilih jenis (1-2): ").strip()
        if pilih_jenis in validitas:
            jenis = validitas[pilih_jenis]
            break
        print("  Pilihan tidak valid.")

    # tampilkan ringkasan sebelum konfirmasi
    print("\n┌─── Ringkasan Transaksi ────────────────────┐")
    print(f"│  Nama    : {nama}")
    print(f"│  Rek     : {rek}")
    print(f"│  Bank    : {bank}")
    print(f"│  Nominal : Rp {int(nominal):,}")
    print(f"│  Jenis   : {jenis}")
    print("└────────────────────────────────────────────┘")

    # batalkan jika user tidak konfirmasi
    if not konfirmasi("Simpan transaksi ini? (y/n): "):
        print("  Transaksi dibatalkan.")
        return

    # ambil waktu sekarang untuk tanggal transaksi
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "tanggal": tanggal,
        "nama"   : nama,
        "rek"    : rek,
        "nominal": str(int(nominal)),
        "bank"   : bank,
        "jenis"  : jenis
    }
    simpan_transaksi(data)
    print(f"\n✓ Transaksi '{jenis}' sebesar Rp {int(nominal):,} berhasil disimpan.")


def cek_saldo():
    print("\n=== CEK TOTAL PENGELUARAN ===")
    data = baca_transaksi()
    if not data:
        print("Belum ada transaksi.")
        return

    # hitung total per jenis transaksi
    per_jenis = defaultdict(float)
    for t in data:
        per_jenis[t['jenis']] += float(t['nominal'])

    total = sum(per_jenis.values())
    for jenis, jumlah in per_jenis.items():
        print(f"  {jenis:<15}: Rp {jumlah:>15,.0f}")
    print(f"  {'─' * 37}")
    print(f"  {'Total Keluar':<15}: Rp {total:>15,.0f}")


# ═══════════════════════════════════════════
# UPDATE TRANSAKSI
# ═══════════════════════════════════════════

def update_transaksi():
    """Edit data transaksi yang sudah ada berdasarkan nomor urut."""
    print("\n=== UPDATE TRANSAKSI ===")
    data = baca_transaksi()
    if not data:
        print("Belum ada transaksi.")
        return

    # tampilkan semua transaksi terlebih dahulu
    cetak_pagination(data, "Pilih Transaksi yang Akan Diupdate")

    # minta user memilih nomor transaksi
    while True:
        try:
            pilih = input(f"\nMasukkan nomor transaksi yang ingin diupdate (1-{len(data)}, 0=Batal): ").strip()
            idx = int(pilih)
            if idx == 0:
                print("  Update dibatalkan.")
                return
            if 1 <= idx <= len(data):
                break
            print(f"  Nomor harus antara 1 sampai {len(data)}.")
        except ValueError:
            print("  Masukkan angka yang valid.")

    target = data[idx - 1]

    # tampilkan data lama sebagai referensi
    print("\n┌─── Data Lama ──────────────────────────────┐")
    print(f"│  Nama    : {target['nama']}")
    print(f"│  Rek     : {target['rek']}")
    print(f"│  Bank    : {target['bank']}")
    print(f"│  Nominal : Rp {int(float(target['nominal'])):,}")
    print(f"│  Jenis   : {target['jenis']}")
    print("└────────────────────────────────────────────┘")
    print("  (Tekan Enter untuk mempertahankan nilai lama)\n")

    # input data baru — tekan Enter untuk skip / pertahankan nilai lama
    raw_nama = input(f"Nama pemilik rekening [{target['nama']}]: ").strip()
    if raw_nama:
        # validasi: tidak boleh ada angka
        while any(c.isdigit() for c in raw_nama):
            print("  Nama tidak boleh mengandung angka.")
            raw_nama = input(f"Nama pemilik rekening [{target['nama']}]: ").strip()
            if not raw_nama:
                break
        nama_baru = raw_nama if raw_nama else target['nama']
    else:
        nama_baru = target['nama']

    raw_rek = input(f"Nomor rekening        [{target['rek']}]: ").strip()
    if raw_rek:
        while not (raw_rek.isdigit() and len(raw_rek) == 10):
            print("  Nomor rekening harus tepat 10 digit angka.")
            raw_rek = input(f"Nomor rekening        [{target['rek']}]: ").strip()
            if not raw_rek:
                break
        rek_baru = raw_rek if raw_rek else target['rek']
    else:
        rek_baru = target['rek']

    raw_bank = input(f"Nama bank             [{target['bank']}]: ").strip()
    if raw_bank:
        while any(c.isdigit() for c in raw_bank):
            print("  Nama bank tidak boleh mengandung angka.")
            raw_bank = input(f"Nama bank             [{target['bank']}]: ").strip()
            if not raw_bank:
                break
        bank_baru = raw_bank if raw_bank else target['bank']
    else:
        bank_baru = target['bank']

    raw_nominal = input(f"Nominal (Rp)          [{int(float(target['nominal'])):,}]: ").strip().replace(",", "").replace(".", "")
    if raw_nominal:
        while True:
            try:
                val = float(raw_nominal)
                if val <= 0:
                    print("  Nominal harus lebih dari 0.")
                    raw_nominal = input(f"Nominal (Rp)          [{int(float(target['nominal'])):,}]: ").strip().replace(",", "").replace(".", "")
                else:
                    nominal_baru = str(int(val))
                    break
            except ValueError:
                print("  Input tidak valid, masukkan angka saja.")
                raw_nominal = input(f"Nominal (Rp)          [{int(float(target['nominal'])):,}]: ").strip().replace(",", "").replace(".", "")
    else:
        nominal_baru = target['nominal']

    print(f"\nJenis Transaksi saat ini: {target['jenis']}")
    print("  1. Transfer")
    print("  2. Pembayaran")
    raw_jenis = input("Pilih jenis baru (1-2, Enter=pertahankan): ").strip()
    if raw_jenis in validitas:
        jenis_baru = validitas[raw_jenis]
    else:
        jenis_baru = target['jenis']

    # tampilkan ringkasan perubahan sebelum disimpan
    print("\n┌─── Ringkasan Perubahan ────────────────────┐")
    print(f"│  Nama    : {target['nama']:<18} → {nama_baru}")
    print(f"│  Rek     : {target['rek']:<18} → {rek_baru}")
    print(f"│  Bank    : {target['bank']:<18} → {bank_baru}")
    print(f"│  Nominal : Rp {int(float(target['nominal'])):>10,}    → Rp {int(float(nominal_baru)):,}")
    print(f"│  Jenis   : {target['jenis']:<18} → {jenis_baru}")
    print("└────────────────────────────────────────────┘")

    if not konfirmasi("Simpan perubahan ini? (y/n): "):
        print("  Update dibatalkan.")
        return

    # terapkan perubahan — tanggal transaksi asli dipertahankan
    data[idx - 1] = {
        "tanggal": target['tanggal'],
        "nama"   : nama_baru,
        "rek"    : rek_baru,
        "nominal": nominal_baru,
        "bank"   : bank_baru,
        "jenis"  : jenis_baru
    }
    tulis_ulang_semua(data)
    print(f"\n✓ Transaksi nomor {idx} berhasil diupdate.")


# ═══════════════════════════════════════════
# HAPUS TRANSAKSI LAMA (> 2 BULAN)
# ═══════════════════════════════════════════

def hapus_transaksi_lama():
    """
    Hapus otomatis semua transaksi yang tanggalnya sudah lebih dari 2 bulan
    (60 hari) dari hari ini. User akan melihat pratinjau sebelum konfirmasi.
    """
    print("\n=== HAPUS TRANSAKSI LEBIH DARI 2 BULAN ===")
    data = baca_transaksi()
    if not data:
        print("Belum ada transaksi.")
        return

    batas = datetime.now() - timedelta(days=60)  # 60 hari ≈ 2 bulan

    akan_dihapus = []
    akan_disimpan = []

    for t in data:
        try:
            tgl = datetime.strptime(t['tanggal'], "%Y-%m-%d %H:%M:%S")
            if tgl < batas:
                akan_dihapus.append(t)
            else:
                akan_disimpan.append(t)
        except ValueError:
            # jika format tanggal tidak dikenali, amankan dengan tetap simpan
            akan_disimpan.append(t)

    if not akan_dihapus:
        print(f"  Tidak ada transaksi yang lebih dari 2 bulan (sebelum {batas.strftime('%Y-%m-%d')}).")
        return

    # tampilkan pratinjau transaksi yang akan dihapus
    print(f"\n  Ditemukan {len(akan_dihapus)} transaksi sebelum {batas.strftime('%Y-%m-%d')} yang akan dihapus:\n")
    cetak_header()
    for i, t in enumerate(akan_dihapus, 1):
        cetak_baris(i, t)

    total_nominal = sum(float(t['nominal']) for t in akan_dihapus)
    print(f"\n  Total nominal yang akan dihapus : Rp {total_nominal:,.0f}")
    print(f"  Sisa transaksi setelah hapus    : {len(akan_disimpan)} transaksi\n")

    if not konfirmasi(f"Hapus {len(akan_dihapus)} transaksi lama ini? (y/n): "):
        print("  Penghapusan dibatalkan.")
        return

    tulis_ulang_semua(akan_disimpan)
    print(f"\n✓ {len(akan_dihapus)} transaksi lama berhasil dihapus.")
    print(f"  {len(akan_disimpan)} transaksi tersisa dalam riwayat.")


# ═══════════════════════════════════════════
# laporan
# ═══════════════════════════════════════════

def menu_laporan():
    while True:
        print("\n=== LAPORAN ===")
        print("1. Ringkasan per Bulan")
        print("2. Ringkasan per Bank")
        print("3. Kembali")
        pilih = input("Pilih opsi (1-3): ").strip()
        data  = baca_transaksi()

        if pilih == '1':
            if not data:
                print("Belum ada transaksi.")
                continue
            per_bulan = defaultdict(float)
            for t in data:
                bulan = t['tanggal'][:7]   # ambil "YYYY-MM"
                per_bulan[bulan] += float(t['nominal'])

            print(f"\n  {'Bulan':<12} {'Total Pengeluaran':>22}")
            print("  " + "─" * 36)
            for bulan in sorted(per_bulan):
                print(f"  {bulan:<12} Rp {per_bulan[bulan]:>15,.0f}")
            total = sum(per_bulan.values())
            print("  " + "─" * 36)
            print(f"  {'TOTAL':<12} Rp {total:>15,.0f}")

        elif pilih == '2':
            if not data:
                print("Belum ada transaksi.")
                continue
            per_bank = defaultdict(lambda: defaultdict(float))
            for t in data:
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


# ═══════════════════════════════════════════
# menu
# ═══════════════════════════════════════════

def menu_tampilan():
    while True:
        print("\n=== TAMPILKAN RIWAYAT TRANSAKSI ===")
        print("1. Tampilkan Semua Transaksi")
        print("2. Tampilkan Transaksi Berdasarkan Jenis")
        print("3. Tampilkan Urutan Berdasarkan Tanggal")
        print("4. Tampilkan Urutan Berdasarkan Nominal")
        print("5. Kembali ke Menu Utama")
        pilih = input("Pilih opsi (1-5): ").strip()
        data  = baca_transaksi()

        if pilih == '1':
            # tampilkan semua transaksi dengan pagination
            cetak_pagination(data, "Semua Transaksi")

        elif pilih == '2':
            # pilih jenis transaksi yang ingin ditampilkan
            print("\n  1. Transfer")
            print("  2. Pembayaran")
            pilih_jenis = input("Pilih jenis (1-2): ").strip()
            if pilih_jenis not in validitas:
                print("  Pilihan tidak valid.")
                continue
            jenis = validitas[pilih_jenis]
            hasil = [t for t in data if t['jenis'] == jenis]
            cetak_pagination(hasil, f"Transaksi Jenis '{jenis}'")

        elif pilih == '3':
            # urutkan data berdasarkan tanggal (dari yang paling lama ke yang paling baru)
            urutan = sorted(data, key=lambda x: x['tanggal'])
            cetak_pagination(urutan, "Urutan Berdasarkan Tanggal (Terlama → Terbaru)")

        elif pilih == '4':
            # urutkan data berdasarkan nominal (dari yang terbesar ke yang terkecil)
            try:
                urutan = sorted(data, key=lambda x: float(x['nominal']), reverse=True)
            except ValueError:
                urutan = data
            cetak_pagination(urutan, "Urutan Berdasarkan Nominal (Terbesar → Terkecil)")

        elif pilih == '5':
            break
        else:
            print("Opsi tidak valid. Silakan pilih antara 1-5.")


# ═══════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════

def main():
    while True:
        print("\n=== APLIKASI RIWAYAT KEUANGAN ===")
        print("1. Input Transaksi Baru")
        print("2. Tampilkan Riwayat")
        print("3. Cek Total Pengeluaran")
        print("4. Laporan")
        print("5. Update Transaksi")
        print("6. Hapus Transaksi Lama (>2 Bulan)")
        print("7. Keluar")

        pilihan = input("Pilih Menu: ").strip()
        if pilihan == '1':
            tambah_transaksi()
        elif pilihan == '2':
            menu_tampilan()
        elif pilihan == '3':
            cek_saldo()
        elif pilihan == '4':
            menu_laporan()
        elif pilihan == '5':
            update_transaksi()
        elif pilihan == '6':
            hapus_transaksi_lama()
        elif pilihan == '7':
            print("Sistem Berhenti. Data Anda aman di 'riwayat_transaksi.txt'")
            break
        else:
            print("Pilihan tidak valid. Masukkan angka 1-7.")


if __name__ == "__main__":
    main()