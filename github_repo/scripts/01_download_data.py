"""
scripts/01_download_data.py
───────────────────────────
Instruksi dan helper untuk mengunduh semua dataset yang dibutuhkan.
Beberapa dataset memerlukan unduhan manual karena ketentuan akses API.
Jalankan: python scripts/01_download_data.py
"""

import os, sys, time, textwrap
import urllib.request, urllib.error, ssl

DATA_RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(DATA_RAW, exist_ok=True)


def print_header(text):
    print("\n" + "═" * 65)
    print(f"  {text}")
    print("═" * 65)


def print_manual(title, url, filename, instructions):
    print(f"\n  [{title}]")
    print(f"  URL    : {url}")
    print(f"  Simpan : data/raw/{filename}")
    print("  Langkah:")
    for i, step in enumerate(instructions, 1):
        wrapped = textwrap.fill(step, width=60, subsequent_indent="          ")
        print(f"    {i}. {wrapped}")


def try_download(url, dest, label):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            content = r.read()
        with open(dest, 'wb') as f:
            f.write(content)
        size_kb = len(content) / 1024
        print(f"  ✓ Berhasil diunduh: {label} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        print(f"  ✗ Gagal otomatis ({type(e).__name__}) → unduh manual")
        return False


# ──────────────────────────────────────────────────────────────
# DATASET 1: ENSO ONI — NOAA
# ──────────────────────────────────────────────────────────────
print_header("DATASET 1/4 — ENSO ONI (NOAA Climate Prediction Center)")

oni_dest = os.path.join(DATA_RAW, 'oni_raw.txt')
if os.path.exists(oni_dest):
    print(f"  ✓ Sudah ada: data/raw/oni_raw.txt")
else:
    success = try_download(
        'https://psl.noaa.gov/data/correlation/oni.data',
        oni_dest,
        'ENSO ONI'
    )
    if not success:
        print_manual(
            "Unduhan Manual — ENSO ONI",
            "https://psl.noaa.gov/data/correlation/oni.data",
            "oni_raw.txt",
            [
                "Buka URL di browser.",
                "Klik kanan pada halaman → Save As → simpan sebagai 'oni_raw.txt'.",
                "Pindahkan file ke folder data/raw/.",
                "Alternatif: https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php"
                " → copy tabel → paste ke Excel → save as CSV.",
            ]
        )

# ──────────────────────────────────────────────────────────────
# DATASET 2: PRODUKSI PADI — BPS
# ──────────────────────────────────────────────────────────────
print_header("DATASET 2/4 — Produksi Padi per Provinsi (BPS Indonesia)")

padi_dest = os.path.join(DATA_RAW, 'bps_padi_provinsi.xlsx')
if os.path.exists(padi_dest):
    print(f"  ✓ Sudah ada: data/raw/bps_padi_provinsi.xlsx")
else:
    print_manual(
        "Unduhan Manual — Produksi Padi BPS",
        "https://www.bps.go.id/id/statistics-table/1/MTkwMSMx/",
        "bps_padi_provinsi.xlsx",
        [
            "Buka URL di browser.",
            "Klik tabel 'Produksi Padi Menurut Provinsi (Ton)'.",
            "Klik ikon unduhan (Excel) di kanan atas tabel.",
            "Ulangi untuk tahun 2000 hingga 2024 (atau gunakan fitur multi-year).",
            "Gabungkan semua data ke satu file dengan sheet per tahun atau format long.",
            "ALTERNATIF VIA API (lebih efisien):",
            "  Daftar API key gratis di https://webapi.bps.go.id",
            "  Endpoint: GET /v1/api/list/model/data/lang/ind/domain/0000/var/1067/key/{API_KEY}",
            "  Variable ID 1067 = Produksi Padi",
        ]
    )

# ──────────────────────────────────────────────────────────────
# DATASET 3: HARGA BERAS — BPS
# ──────────────────────────────────────────────────────────────
print_header("DATASET 3/4 — Harga Eceran Beras (BPS Indonesia)")

harga_dest = os.path.join(DATA_RAW, 'bps_harga_beras.xlsx')
if os.path.exists(harga_dest):
    print(f"  ✓ Sudah ada: data/raw/bps_harga_beras.xlsx")
else:
    print_manual(
        "Unduhan Manual — Harga Beras BPS",
        "https://www.bps.go.id/id/statistics-table/2/NDk3IzI=/",
        "bps_harga_beras.xlsx",
        [
            "Buka URL di browser.",
            "Pilih tabel 'Harga Eceran Beras di Tingkat Konsumen Menurut Provinsi'.",
            "Unduh Excel untuk periode 2000–2024.",
            "Untuk 2000–2011, cari publikasi 'Statistik Harga Konsumen Perdesaan' di bps.go.id/publication.",
        ]
    )

# ──────────────────────────────────────────────────────────────
# DATASET 4: CURAH HUJAN — BMKG
# ──────────────────────────────────────────────────────────────
print_header("DATASET 4/4 — Curah Hujan per Stasiun (BMKG)")

bmkg_dest = os.path.join(DATA_RAW, 'bmkg_curah_hujan.csv')
if os.path.exists(bmkg_dest):
    print(f"  ✓ Sudah ada: data/raw/bmkg_curah_hujan.csv")
else:
    print_manual(
        "Unduhan Manual — Curah Hujan BMKG",
        "https://dataonline.bmkg.go.id/data_iklim",
        "bmkg_curah_hujan.csv",
        [
            "Daftar akun gratis di dataonline.bmkg.go.id.",
            "Login → Pilih 'Data Iklim' → Parameter: RR (Curah Hujan).",
            "Pilih semua stasiun → periode 2000–2024 → format CSV.",
            "Simpan sebagai bmkg_curah_hujan.csv di data/raw/.",
            "CATATAN: Agregasi ke level provinsi menggunakan rata-rata",
            "  aritmatik stasiun dalam provinsi (lihat scripts/02_preprocessing.py).",
        ]
    )

# ──────────────────────────────────────────────────────────────
# RINGKASAN STATUS
# ──────────────────────────────────────────────────────────────
print_header("RINGKASAN STATUS DATA")

files_needed = {
    'oni_raw.txt': 'ENSO ONI (NOAA)',
    'bps_padi_provinsi.xlsx': 'Produksi Padi (BPS)',
    'bps_harga_beras.xlsx': 'Harga Beras (BPS)',
    'bmkg_curah_hujan.csv': 'Curah Hujan (BMKG)',
}

all_ready = True
for fname, label in files_needed.items():
    path = os.path.join(DATA_RAW, fname)
    status = "✓ Ada" if os.path.exists(path) else "✗ Belum ada"
    if not os.path.exists(path):
        all_ready = False
    print(f"  {status}  {label:<35} ({fname})")

if all_ready:
    print("\n  Semua data siap. Jalankan: python scripts/02_preprocessing.py")
else:
    print("\n  Lengkapi unduhan manual di atas, lalu jalankan:")
    print("  python scripts/02_preprocessing.py")
