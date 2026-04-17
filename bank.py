import os
from datetime import datetime, timedelta
from collections import defaultdict

# Nama file teks yang digunakan untuk menyimpan seluruh riwayat transaksi
nama_file = "riwayat_duid.txt"

# Jumlah transaksi yang ditampilkan per halaman saat menggunakan pagination
page = 10

# Daftar jenis transaksi yang diizinkan
# Key = angka pilihan menu, Value = nama jenis transaksi
validitas = {
    "1": "Transfer",
    "2": "Pembayaran"
}

# Semua jenis transaksi di atas dianggap sebagai pengeluaran
output = {"Transfer", "Pembayaran"}


# ══════════════════════════════════════════════════════════════════════════════════════
# bagian read file
# Bertanggung jawab atas semua operasi baca/tulis ke file teks
# ══════════════════════════════════════════════════════════════════════════════════════

def baca_transaksi():
    """
    Membaca semua transaksi dari file teks dan mengembalikannya sebagai list of dict.
    Setiap baris file mewakili satu transaksi dengan format:
        tanggal,nama,rek,nominal,bank,jenis
    Jika file belum ada atau baris tidak lengkap, baris tersebut dilewati.
    """
    transaksi = []

    # Jika file belum pernah dibuat, kembalikan list kosong
    if not os.path.exists(nama_file):
        return transaksi

    with open(nama_file, "r") as f:
        for baris in f:
            baris = baris.strip()

            # Lewati baris kosong
            if not baris:
                continue

            # Pisahkan tiap kolom berdasarkan koma
            bagian = baris.split(",")

            # Pastikan baris memiliki tepat 6 kolom; lewati jika kurang
            if len(bagian) < 6:
                continue

            # Masukkan data ke dalam dict lalu tambahkan ke list
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
    """
    Menambahkan satu transaksi baru ke bagian akhir file (mode append).
    Parameter:
        data (dict): Satu transaksi dengan key tanggal, nama, rek, nominal, bank, jenis.
    """
    with open(nama_file, "a") as f:
        f.write(
            f"{data['tanggal']},{data['nama']},{data['rek']},"
            f"{data['nominal']},{data['bank']},{data['jenis']}\n"
        )


def tulis_ulang_semua(daftar: list):
    """
    Menimpa seluruh isi file dengan daftar transaksi yang diberikan (mode write).
    Digunakan setelah operasi update atau hapus agar file selalu sinkron dengan data di memori.
    Parameter:
        daftar (list): List of dict berisi semua transaksi yang ingin disimpan.
    """
    with open(nama_file, "w") as f:
        for t in daftar:
            f.write(
                f"{t['tanggal']},{t['nama']},{t['rek']},"
                f"{t['nominal']},{t['bank']},{t['jenis']}\n"
            )


# ══════════════════════════════════════════════════════════════════════════════════════
# tampilan user
# Menangani semua output ke layar, termasuk tabel dan pagination
# ══════════════════════════════════════════════════════════════════════════════════════

def cetak_header():
    """Mencetak baris judul kolom tabel beserta garis pemisah."""
    print(f"\n{'No':<4} {'Tanggal':<20} {'Nama':<18} {'No. Rek':<13} "
          f"{'Nominal':>16} {'Bank':<10} {'Jenis'}")
    print("─" * 95)


def cetak_baris(i, t):
    """
    Mencetak satu baris data transaksi dalam format tabel.
    Parameter:
        i (int): Nomor urut transaksi.
        t (dict): Data transaksi yang akan dicetak.
    """
    try:
        # Format nominal menjadi "Rp 1.000.000" dengan pemisah ribuan
        nominal_fmt = f"Rp {int(float(t['nominal'])):>13,}"
    except ValueError:
        # Jika nominal tidak bisa dikonversi ke angka, tampilkan placeholder
        nominal_fmt = f"{'??':>16}"

    print(f"{i:<4} {t['tanggal']:<20} {t['nama']:<18} {t['rek']:<13} "
          f"{nominal_fmt} {t['bank']:<10} {t['jenis']}")


def cetak_pagination(data, judul=""):
    """
    Menampilkan list transaksi dengan sistem pagination (10 baris per halaman).
    User dapat berpindah halaman menggunakan tombol N (next), P (previous), Q (quit).
    Parameter:
        data  (list): List transaksi yang akan ditampilkan.
        judul (str) : Judul opsional yang ditampilkan di atas tabel.
    """
    # Jika tidak ada data sama sekali, tampilkan pesan kosong
    if not data:
        print("  (Tidak ada data.)")
        return

    total     = len(data)
    total_hal = (total + page - 1) // page  # Rumus: ceil(total / page)
    halaman   = 1                            # Mulai dari halaman pertama

    while True:
        # Hitung indeks awal dan akhir data untuk halaman saat ini
        mulai    = (halaman - 1) * page
        akhir    = mulai + page
        potongan = data[mulai:akhir]

        # Tampilkan judul jika ada
        if judul:
            print(f"\n─── {judul} ───")

        print(f"  Halaman {halaman}/{total_hal}  |  Total: {total} transaksi")
        cetak_header()

        # Cetak tiap baris pada halaman ini; nomor urut dimulai dari indeks global
        for i, t in enumerate(potongan, mulai + 1):
            cetak_baris(i, t)

        # Jika hanya ada 1 halaman, tidak perlu menampilkan menu navigasi
        if total_hal == 1:
            break

        # Tampilkan pilihan navigasi antar halaman
        print(f"\n  [N] Halaman Berikutnya  [P] Halaman Sebelumnya  [Q] Kembali")
        nav = input("  Navigasi: ").strip().upper()

        if nav == "N":
            # Maju ke halaman berikutnya jika belum di halaman terakhir
            if halaman < total_hal:
                halaman += 1
            else:
                print("  Sudah di halaman terakhir.")
        elif nav == "P":
            # Mundur ke halaman sebelumnya jika belum di halaman pertama
            if halaman > 1:
                halaman -= 1
            else:
                print("  Sudah di halaman pertama.")
        elif nav == "Q":
            break  # Keluar dari loop pagination
        else:
            print("  Pilihan tidak valid.")
            break


# ══════════════════════════════════════════════════════════════════════════════════════
# bagian validasi
# Memastikan setiap input dari user sesuai dengan aturan yang berlaku
# ══════════════════════════════════════════════════════════════════════════════════════

def input_nama(label):
    """
    Meminta input nama dari user.
    Aturan: tidak boleh kosong dan tidak boleh mengandung karakter angka.
    Parameter:
        label (str): Teks prompt yang ditampilkan ke user.
    Returns:
        str: Nama yang sudah divalidasi.
    """
    while True:
        nilai = input(label).strip()
        if not nilai:
            print("  Tidak boleh kosong.")
        elif any(c.isdigit() for c in nilai):
            # Cek apakah ada karakter angka di dalam nama
            print("  Nama tidak boleh mengandung angka.")
        else:
            return nilai


def input_nominal():
    """
    Meminta input nominal transaksi dari user.
    Aturan: harus berupa angka dan nilainya harus lebih dari 0.
    Koma dan titik sebagai pemisah ribuan akan diabaikan secara otomatis.
    Returns:
        float: Nominal yang sudah divalidasi.
    """
    while True:
        # Hapus koma dan titik agar input seperti "1.000.000" tetap bisa diproses
        raw = input("Nominal (Rp)          : ").strip().replace(",", "").replace(".", "")
        try:
            nilai = float(raw)
            if nilai <= 0:
                print("  Nominal harus lebih dari 0.")
            else:
                return nilai
        except ValueError:
            # Input bukan angka sama sekali
            print("  Input tidak valid, masukkan angka saja.")


def input_rek():
    """
    Meminta input nomor rekening dari user.
    Aturan: harus tepat 10 digit dan hanya boleh berisi angka.
    Returns:
        str: Nomor rekening yang sudah divalidasi.
    """
    while True:
        rek = input("Nomor rekening        : ").strip()
        if rek.isdigit() and len(rek) == 10:
            return rek
        print("  Nomor rekening harus tepat 10 digit angka.")


def konfirmasi(pesan="Simpan transaksi ini? (y/n): "):
    """
    Menampilkan prompt konfirmasi dan menunggu jawaban y (ya) atau n (tidak).
    Parameter:
        pesan (str): Teks pertanyaan konfirmasi yang ditampilkan.
    Returns:
        bool: True jika user menjawab 'y', False jika 'n'.
    """
    while True:
        jwb = input(pesan).strip().lower()
        if jwb in ("y", "n"):
            return jwb == "y"
        print("  Masukkan 'y' untuk Ya atau 'n' untuk Tidak.")


# ══════════════════════════════════════════════════════════════════════════════════════
# fitur utama
# ══════════════════════════════════════════════════════════════════════════════════════

def tambah_transaksi():
    """
    Menjalankan alur input transaksi baru:
    1. Kumpulkan semua data dari user (nama, rek, bank, nominal, jenis).
    2. Tampilkan ringkasan untuk dikonfirmasi.
    3. Jika dikonfirmasi, simpan ke file dengan timestamp saat ini.
    """
    print("\n=== INPUT TRANSAKSI BARU ===")

    # Kumpulkan semua input terlebih dahulu sebelum menampilkan ringkasan
    nama    = input_nama("Nama pemilik rekening : ")
    rek     = input_rek()
    bank    = input_nama("Nama bank             : ")
    nominal = input_nominal()

    # Tampilkan pilihan jenis transaksi dan minta user memilih
    print("\nJenis Transaksi:")
    for k, v in validitas.items():
        print(f"  {k}. {v}")
    while True:
        pilih_jenis = input("Pilih jenis (1-2): ").strip()
        if pilih_jenis in validitas:
            jenis = validitas[pilih_jenis]
            break
        print("  Pilihan tidak valid.")

    # Tampilkan ringkasan lengkap sebelum user mengonfirmasi
    print("\n┌─── Ringkasan Transaksi ────────────────────┐")
    print(f"│  Nama    : {nama}")
    print(f"│  Rek     : {rek}")
    print(f"│  Bank    : {bank}")
    print(f"│  Nominal : Rp {int(nominal):,}")
    print(f"│  Jenis   : {jenis}")
    print("└────────────────────────────────────────────┘")

    # Batalkan proses jika user tidak mengonfirmasi
    if not konfirmasi("Simpan transaksi ini? (y/n): "):
        print("  Transaksi dibatalkan.")
        return

    # Gunakan waktu sekarang sebagai timestamp transaksi
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
    """
    Menghitung dan menampilkan total pengeluaran yang dikelompokkan per jenis transaksi,
    beserta grand total seluruhnya.
    """
    print("\n=== CEK TOTAL PENGELUARAN ===")
    data = baca_transaksi()

    if not data:
        print("Belum ada transaksi.")
        return

    # Akumulasi nominal per jenis transaksi menggunakan defaultdict
    per_jenis = defaultdict(float)
    for t in data:
        per_jenis[t['jenis']] += float(t['nominal'])

    # Tampilkan breakdown per jenis lalu grand total
    total = sum(per_jenis.values())
    for jenis, jumlah in per_jenis.items():
        print(f"  {jenis:<15}: Rp {jumlah:>15,.0f}")
    print(f"  {'─' * 37}")
    print(f"  {'Total Keluar':<15}: Rp {total:>15,.0f}")


# ══════════════════════════════════════════════════════════════════════════════════════
# bagian update transaksi
# ══════════════════════════════════════════════════════════════════════════════════════

def update_transaksi():
    """
    Mengizinkan user mengedit data transaksi yang sudah tersimpan.
    Alur:
    1. Tampilkan semua transaksi.
    2. User memilih nomor transaksi yang ingin diubah.
    3. Untuk tiap field, user bisa memasukkan nilai baru atau tekan Enter untuk skip.
    4. Tampilkan ringkasan perubahan, minta konfirmasi, lalu timpa file.
    Catatan: Tanggal transaksi asli tidak dapat diubah.
    """
    print("\n=== UPDATE TRANSAKSI ===")
    data = baca_transaksi()

    if not data:
        print("Belum ada transaksi.")
        return

    # Tampilkan semua transaksi agar user bisa memilih nomor yang benar
    cetak_pagination(data, "Pilih Transaksi yang Akan Diupdate")

    # Minta user memilih nomor transaksi yang valid (1 s/d total data)
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

    # Ambil data transaksi yang dipilih sebagai referensi nilai lama
    target = data[idx - 1]

    # Tampilkan data lama agar user tahu nilai saat ini sebelum mengubahnya
    print("\n┌─── Data Lama ──────────────────────────────┐")
    print(f"│  Nama    : {target['nama']}")
    print(f"│  Rek     : {target['rek']}")
    print(f"│  Bank    : {target['bank']}")
    print(f"│  Nominal : Rp {int(float(target['nominal'])):,}")
    print(f"│  Jenis   : {target['jenis']}")
    print("└────────────────────────────────────────────┘")
    print("  (Tekan Enter untuk mempertahankan nilai lama)\n")

    # ── Update Nama ──────────────────────────────────────────────────
    raw_nama = input(f"Nama pemilik rekening [{target['nama']}]: ").strip()
    if raw_nama:
        # Validasi ulang: nama baru tidak boleh mengandung angka
        while any(c.isdigit() for c in raw_nama):
            print("  Nama tidak boleh mengandung angka.")
            raw_nama = input(f"Nama pemilik rekening [{target['nama']}]: ").strip()
            if not raw_nama:
                break  # User menekan Enter, gunakan nilai lama
        nama_baru = raw_nama if raw_nama else target['nama']
    else:
        nama_baru = target['nama']  # Pertahankan nilai lama

    # ── Update Nomor Rekening ─────────────────────────────────────────
    raw_rek = input(f"Nomor rekening        [{target['rek']}]: ").strip()
    if raw_rek:
        # Validasi ulang: harus tepat 10 digit angka
        while not (raw_rek.isdigit() and len(raw_rek) == 10):
            print("  Nomor rekening harus tepat 10 digit angka.")
            raw_rek = input(f"Nomor rekening        [{target['rek']}]: ").strip()
            if not raw_rek:
                break  # User menekan Enter, gunakan nilai lama
        rek_baru = raw_rek if raw_rek else target['rek']
    else:
        rek_baru = target['rek']  # Pertahankan nilai lama

    # ── Update Nama Bank ──────────────────────────────────────────────
    raw_bank = input(f"Nama bank             [{target['bank']}]: ").strip()
    if raw_bank:
        # Validasi ulang: nama bank tidak boleh mengandung angka
        while any(c.isdigit() for c in raw_bank):
            print("  Nama bank tidak boleh mengandung angka.")
            raw_bank = input(f"Nama bank             [{target['bank']}]: ").strip()
            if not raw_bank:
                break  # User menekan Enter, gunakan nilai lama
        bank_baru = raw_bank if raw_bank else target['bank']
    else:
        bank_baru = target['bank']  # Pertahankan nilai lama

    # ── Update Nominal ────────────────────────────────────────────────
    raw_nominal = input(f"Nominal (Rp)          [{int(float(target['nominal'])):,}]: ").strip().replace(",", "").replace(".", "")
    if raw_nominal:
        # Validasi ulang: harus angka positif
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
        nominal_baru = target['nominal']  # Pertahankan nilai lama

    # ── Update Jenis Transaksi ────────────────────────────────────────
    print(f"\nJenis Transaksi saat ini: {target['jenis']}")
    print("  1. Transfer")
    print("  2. Pembayaran")
    raw_jenis = input("Pilih jenis baru (1-2, Enter=pertahankan): ").strip()

    # Jika user memilih jenis baru yang valid, gunakan; selain itu pertahankan lama
    if raw_jenis in validitas:
        jenis_baru = validitas[raw_jenis]
    else:
        jenis_baru = target['jenis']

    # Tampilkan ringkasan perubahan (lama → baru) sebelum konfirmasi akhir
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

    # Terapkan perubahan pada data di memori; tanggal asli tetap dipertahankan
    data[idx - 1] = {
        "tanggal": target['tanggal'],
        "nama"   : nama_baru,
        "rek"    : rek_baru,
        "nominal": nominal_baru,
        "bank"   : bank_baru,
        "jenis"  : jenis_baru
    }

    # Timpa file dengan data yang sudah diperbarui
    tulis_ulang_semua(data)
    print(f"\n✓ Transaksi nomor {idx} berhasil diupdate.")


# ══════════════════════════════════════════════════════════════════════════════════════
# FITUR HAPUS TRANSAKSI LAMA (> 2 BULAN)
# ══════════════════════════════════════════════════════════════════════════════════════

def hapus_transaksi_lama():
    """
    Menghapus semua transaksi yang berusia lebih dari 60 hari (≈ 2 bulan) dari hari ini.
    Alur:
    1. Pisahkan transaksi menjadi dua kelompok: akan dihapus vs. akan disimpan.
    2. Tampilkan pratinjau transaksi yang akan dihapus.
    3. Minta konfirmasi, lalu timpa file hanya dengan transaksi yang disimpan.
    """
    print("\n=== HAPUS TRANSAKSI LEBIH DARI 2 BULAN ===")
    data = baca_transaksi()

    if not data:
        print("Belum ada transaksi.")
        return

    # Hitung tanggal batas: transaksi sebelum tanggal ini akan dihapus
    batas = datetime.now() - timedelta(days=60)

    akan_dihapus  = []  # Transaksi yang lebih tua dari batas
    akan_disimpan = []  # Transaksi yang masih dalam rentang 2 bulan terakhir

    for t in data:
        try:
            tgl = datetime.strptime(t['tanggal'], "%Y-%m-%d %H:%M:%S")
            if tgl < batas:
                akan_dihapus.append(t)
            else:
                akan_disimpan.append(t)
        except ValueError:
            # Jika format tanggal tidak dikenali, amankan transaksi dengan tetap menyimpannya
            akan_disimpan.append(t)

    # Jika tidak ada transaksi yang memenuhi kriteria penghapusan
    if not akan_dihapus:
        print(f"  Tidak ada transaksi yang lebih dari 2 bulan (sebelum {batas.strftime('%Y-%m-%d')}).")
        return

    # Tampilkan pratinjau transaksi yang akan dihapus beserta total nominalnya
    print(f"\n  Ditemukan {len(akan_dihapus)} transaksi sebelum {batas.strftime('%Y-%m-%d')} yang akan dihapus:\n")
    cetak_header()
    for i, t in enumerate(akan_dihapus, 1):
        cetak_baris(i, t)

    total_nominal = sum(float(t['nominal']) for t in akan_dihapus)
    print(f"\n  Total nominal yang akan dihapus : Rp {total_nominal:,.0f}")
    print(f"  Sisa transaksi setelah hapus    : {len(akan_disimpan)} transaksi\n")

    # Minta konfirmasi akhir sebelum menghapus secara permanen
    if not konfirmasi(f"Hapus {len(akan_dihapus)} transaksi lama ini? (y/n): "):
        print("  Penghapusan dibatalkan.")
        return

    # Timpa file hanya dengan transaksi yang masih dalam rentang 2 bulan
    tulis_ulang_semua(akan_disimpan)
    print(f"\n✓ {len(akan_dihapus)} transaksi lama berhasil dihapus.")
    print(f"  {len(akan_disimpan)} transaksi tersisa dalam riwayat.")


# ══════════════════════════════════════════════════════════════════════════════════════
# bagian laporan transaksi
# ══════════════════════════════════════════════════════════════════════════════════════

def menu_laporan():
    """
    Menampilkan submenu laporan dengan dua pilihan:
    1. Ringkasan per Bulan  — total pengeluaran dikelompokkan per bulan (YYYY-MM).
    2. Ringkasan per Bank   — total pengeluaran dikelompokkan per nama bank dan jenis.
    """
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

            # Kelompokkan total nominal berdasarkan bulan (format YYYY-MM)
            per_bulan = defaultdict(float)
            for t in data:
                bulan = t['tanggal'][:7]  # Ambil 7 karakter pertama: "YYYY-MM"
                per_bulan[bulan] += float(t['nominal'])

            # Tampilkan dalam urutan bulan dari yang paling lama
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

            # Kelompokkan nominal dua tingkat: per bank → per jenis transaksi
            per_bank = defaultdict(lambda: defaultdict(float))
            for t in data:
                per_bank[t['bank']][t['jenis']] += float(t['nominal'])

            # Tampilkan tiap bank beserta breakdown jenis dan subtotalnya
            print()
            for bank in sorted(per_bank):
                subtotal = sum(per_bank[bank].values())
                print(f"  [ {bank} ]")
                for jenis, jumlah in per_bank[bank].items():
                    print(f"    {jenis:<15}: Rp {jumlah:>13,.0f}")
                print(f"    {'Subtotal':<15}: Rp {subtotal:>13,.0f}")
                print()

        elif pilih == '3':
            break  # Kembali ke menu utama
        else:
            print("Opsi tidak valid.")


# ══════════════════════════════════════════════════════════════════════════════════════
# bagian mutasi
# ══════════════════════════════════════════════════════════════════════════════════════

def menu_tampilan():
    """
    Menampilkan submenu untuk melihat riwayat transaksi dengan berbagai filter dan urutan:
    1. Semua Transaksi            — tampilkan semua data tanpa filter.
    2. Berdasarkan Jenis          — filter hanya Transfer atau Pembayaran.
    3. Urutan Berdasarkan Tanggal — dari yang paling lama ke paling baru.
    4. Urutan Berdasarkan Nominal — dari yang terbesar ke terkecil.
    """
    while True:
        print("\n=== Mutasi Rekening ===")
        print("1. Tampilkan Semua Riwayat")
        print("2. Tampilkan Riwayat Berdasarkan Jenis")
        print("3. Tampilkan Riwayat Berdasarkan Tanggal")
        print("4. Tampilkan Riwayat Berdasarkan Nominal")
        print("5. Kembali ke Menu Utama")
        pilih = input("Pilih opsi (1-5): ").strip()
        data  = baca_transaksi()

        if pilih == '1':
            # Tampilkan seluruh data tanpa penyaringan
            cetak_pagination(data, "Semua Transaksi")

        elif pilih == '2':
            # Filter data berdasarkan jenis transaksi yang dipilih user
            print("\n  1. Transfer")
            print("  2. Pembayaran")
            pilih_jenis = input("Pilih jenis (1-2): ").strip()
            if pilih_jenis not in validitas:
                print("  Pilihan tidak valid.")
                continue
            jenis = validitas[pilih_jenis]
            # Ambil hanya transaksi dengan jenis yang sesuai
            hasil = [t for t in data if t['jenis'] == jenis]
            cetak_pagination(hasil, f"Transaksi Jenis '{jenis}'")

        elif pilih == '3':
            # Urutkan dari tanggal paling lama ke paling baru (ascending)
            urutan = sorted(data, key=lambda x: x['tanggal'])
            cetak_pagination(urutan, "Urutan Berdasarkan Tanggal (Terlama → Terbaru)")

        elif pilih == '4':
            # Urutkan dari nominal terbesar ke terkecil (descending)
            try:
                urutan = sorted(data, key=lambda x: float(x['nominal']), reverse=True)
            except ValueError:
                # Jika ada nominal yang tidak bisa dikonversi, gunakan data asli tanpa urutan
                urutan = data
            cetak_pagination(urutan, "Urutan Berdasarkan Nominal (Terbesar → Terkecil)")

        elif pilih == '5':
            break  # Kembali ke menu utama
        else:
            print("Opsi tidak valid. Silakan pilih antara 1-5.")


# ══════════════════════════════════════════════════════════════════════════════════════
# menu utama user
# ══════════════════════════════════════════════════════════════════════════════════════

def main():
    """
    Titik masuk program. Menampilkan menu utama dan mengarahkan user
    ke fitur yang dipilih dalam loop hingga user memilih keluar.
    """
    while True:
        print("\n=== APLIKASI RIWAYAT KEUANGAN ===")
        print("1. Input Transaksi Baru")
        print("2. Mutasi Rekening")
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
            # Beritahu user bahwa data telah tersimpan sebelum program ditutup
            print("Sistem Berhenti. Data Anda aman di 'riwayat_transaksi.txt'")
            break
        else:
            print("Pilihan tidak valid. Masukkan angka 1-7.")


# Titik awal eksekusi: pastikan main() hanya dipanggil saat file dijalankan langsung,
# bukan saat diimpor sebagai modul oleh file lain
if __name__ == "__main__":
    main()