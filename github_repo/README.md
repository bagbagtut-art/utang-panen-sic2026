# Utang Panen: Analisis Korelasi Anomali Iklim El Niño terhadap Ketahanan Pangan Indonesia

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data: BPS](https://img.shields.io/badge/Data-BPS%20Indonesia-orange.svg)](https://bps.go.id)
[![Competition: SIC 2026](https://img.shields.io/badge/Competition-SIC%202026-purple.svg)](https://bit.ly/SDC_2026)
[![Status: In Progress](https://img.shields.io/badge/Status-In%20Progress-yellow.svg)]()

> *"Every El Niño leaves a debt — paid not by the climate, but by the farmer."*

---

## Deskripsi Proyek

Repositori ini berisi pipeline analisis data lengkap untuk proyek **"Utang Panen"** — sebuah studi korelasi antara anomali iklim El Niño (diukur via indeks ENSO ONI) dan produksi padi di 34 provinsi Indonesia selama periode 2000–2024.

Proyek ini dikembangkan untuk **Statistics Infographic Competition (SIC) 2026**, bagian dari Statistics Data Challenge 2026, Universitas Islam Bandung (UNISBA), dengan sub-tema *Sustainability Through Data: Tackling Climate Change and Environmental Challenges*.

### Pertanyaan Penelitian

1. Seberapa kuat korelasi antara indeks ENSO ONI dan produksi padi per provinsi di Indonesia?
2. Berapa lag temporal optimal antara anomali iklim dan dampaknya terhadap produksi (analisis CCF)?
3. Provinsi mana yang paling rentan terhadap El Niño, dan bagaimana cara mengukurnya secara komposit (Harvest Debt Index)?
4. Bagaimana penurunan produksi padi bertransmisi menjadi kenaikan harga beras di tingkat konsumen (Distributed Lag Model)?

### Kontribusi Orisinal

- **Harvest Debt Index (HDI)**: Indeks komposit kerentanan provinsi terhadap El Niño, dikonstruksi dari tiga komponen terbobot berbasis kerangka Food Security Framework FAO.
- **Analisis lag temporal**: Cross-Correlation Function (CCF) untuk mengidentifikasi jendela prediksi optimal.
- **Klasterisasi kerentanan**: K-Means clustering 34 provinsi ke dalam 3 profil kerentanan dengan validasi Silhouette Score dan Elbow Method.

---

## Struktur Repositori

```
utang-panen/
│
├── data/
│   ├── raw/                    # Data mentah — TIDAK di-commit ke Git
│   │   ├── oni_raw.txt         # ENSO ONI dari NOAA (unduh manual)
│   │   ├── bps_padi_2000_2024.xlsx  # Produksi padi BPS (unduh manual)
│   │   ├── bps_harga_beras.xlsx     # Harga beras BPS (unduh manual)
│   │   └── bmkg_curah_hujan.csv     # Curah hujan BMKG (unduh manual)
│   │
│   └── processed/              # Hasil preprocessing — di-commit
│       ├── oni_annual.csv       # ONI tahunan terstandarisasi
│       ├── produksi_long.csv    # Produksi padi format long (tidy)
│       ├── data_nasional.csv    # Data gabungan level nasional
│       ├── korelasi_provinsi.csv    # Hasil korelasi per provinsi
│       └── harvest_debt_index.csv   # Skor HDI per provinsi
│
├── scripts/
│   ├── 01_download_data.py     # Instruksi & helper unduh data
│   ├── 02_preprocessing.py     # Cleaning, ADF test, differencing
│   ├── 03_ccf_analysis.py      # Cross-Correlation Function
│   ├── 04_correlation.py       # Korelasi Pearson & Spearman per provinsi
│   ├── 05_clustering.py        # K-Means clustering, HDI calculation
│   ├── 06_dlm_harga.py         # Distributed Lag Model harga beras
│   └── 07_visualization.py     # Semua chart untuk infografis
│
├── notebooks/
│   ├── 00_exploratory.ipynb    # EDA awal
│   ├── 01_full_pipeline.ipynb  # Pipeline lengkap dengan narasi
│   └── 02_sensitivity_analysis.ipynb  # Uji sensitivitas bobot HDI
│
├── outputs/
│   ├── figures/                # PNG/SVG semua chart
│   └── tables/                 # CSV tabel hasil analisis
│
├── docs/
│   ├── metodologi.md           # Dokumentasi metodologi detail
│   ├── data_quality.md         # Catatan kualitas data & limitasi
│   └── references.bib          # Referensi akademis (BibTeX)
│
├── requirements.txt            # Dependensi Python
├── .gitignore                  # Abaikan data/raw dan file sensitif
├── LICENSE                     # MIT License
└── README.md                   # File ini
```

---

## Sumber Data

Semua data yang digunakan adalah data publik yang tersedia secara gratis dan legal.

### 1. ENSO ONI Index — NOAA Climate Prediction Center

| Atribut | Detail |
|---------|--------|
| Nama dataset | Oceanic Niño Index (ONI) v5 |
| Lembaga | NOAA Climate Prediction Center, USA |
| URL unduhan | https://psl.noaa.gov/data/correlation/oni.data |
| Alternatif | https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php |
| Format | Plain text (fixed-width) |
| Resolusi | Bulanan, sejak 1950 |
| Lisensi | Public domain (US Government) |
| Cara akses | Unduh langsung, tidak perlu akun |

```python
# Cara memuat dengan Python
import pandas as pd
# Setelah download manual ke data/raw/oni_raw.txt:
df_oni = pd.read_fwf('data/raw/oni_raw.txt', skiprows=1,
                      header=None, na_values=[-99.9])
```

### 2. Produksi Padi per Provinsi — BPS Indonesia

| Atribut | Detail |
|---------|--------|
| Nama dataset | Produksi Padi Menurut Provinsi (Ton) |
| Lembaga | Badan Pusat Statistik (BPS) Indonesia |
| URL tabel | https://www.bps.go.id/id/statistics-table/1/MTkwMSMx/ |
| Kode tabel BPS | 5203006 |
| BPS API | https://webapi.bps.go.id (butuh API key gratis — daftar di webapi.bps.go.id) |
| Format | Excel (.xlsx) atau JSON (via API) |
| Resolusi | Tahunan per provinsi, 2000–sekarang |
| Catatan metodologi | Pre-2018: metode Ubinan; Post-2018: KSA berbasis citra satelit |

```python
# Setelah download manual ke data/raw/bps_padi.xlsx:
df_padi = pd.read_excel('data/raw/bps_padi.xlsx',
                         index_col=0, skiprows=2)
df_padi = df_padi.dropna(how='all').T  # Transpose: baris=tahun
```

### 3. Harga Eceran Beras — BPS Indonesia

| Atribut | Detail |
|---------|--------|
| Nama dataset | Harga Eceran Beras di Tingkat Konsumen per Provinsi |
| Kode tabel BPS | 7111004 |
| URL | https://www.bps.go.id/id/statistics-table/2/NDk3IzI=/ |
| Satuan | Rp/kg, bulanan per provinsi |
| Tersedia sejak | 2012 (bulanan); 2000–2011 via Statistik Harga Konsumen Perdesaan |

### 4. Data Curah Hujan — BMKG

| Atribut | Detail |
|---------|--------|
| Nama dataset | Data Iklim Online — Parameter CH (Curah Hujan) |
| Lembaga | Badan Meteorologi, Klimatologi, dan Geofisika (BMKG) |
| URL | https://dataonline.bmkg.go.id/data_iklim |
| Format | CSV per stasiun |
| Catatan | Diperlukan registrasi gratis; aggregasi ke level provinsi perlu dilakukan manual |

### 5. Data Irigasi — Kementerian Pertanian / BPS

| Atribut | Detail |
|---------|--------|
| Nama dataset | Luas Lahan Beririgasi Teknis per Provinsi |
| Sumber 1 | Sensus Pertanian BPS 2003, 2013, 2023 |
| Sumber 2 | Statistik Lahan Pertanian, Kementan (annual) |
| URL Kementan | https://www.pertanian.go.id/home/?show=page&act=view&id=61 |
| Catatan | Frekuensi tidak konsisten; gunakan interpolasi linear antar sensus |

---

## Cara Menjalankan Analisis

### Prasyarat

```bash
# Python 3.10 atau lebih baru
python --version

# Install dependensi
pip install -r requirements.txt
```

### Langkah 1 — Unduh Data Mentah

```bash
# Jalankan script helper untuk instruksi unduhan
python scripts/01_download_data.py
```

Script ini akan mencetak instruksi langkah per langkah cara mengunduh setiap dataset dan menempatkannya di folder `data/raw/` yang benar. Beberapa dataset memerlukan unduhan manual karena keterbatasan akses API.

### Langkah 2 — Preprocessing

```bash
python scripts/02_preprocessing.py
```

Output: file CSV terstandarisasi di `data/processed/`. Script ini menjalankan:
- Parsing format data mentah tiap sumber
- Penanganan pemekaran provinsi (gunakan 34 provinsi konsisten)
- Augmented Dickey-Fuller (ADF) test untuk stasioneritas
- First differencing untuk variabel yang tidak stasioner
- Analisis sensitivitas koreksi data BPS ±8%

### Langkah 3 — Analisis Utama

```bash
# Jalankan seluruh pipeline sekaligus
python scripts/03_ccf_analysis.py
python scripts/04_correlation.py
python scripts/05_clustering.py
python scripts/06_dlm_harga.py
```

Atau gunakan Jupyter Notebook untuk analisis interaktif:

```bash
jupyter notebook notebooks/01_full_pipeline.ipynb
```

### Langkah 4 — Visualisasi

```bash
python scripts/07_visualization.py
```

Output PNG dan SVG tersimpan di `outputs/figures/`.

---

## Metodologi Singkat

### Cross-Correlation Function (CCF)

Mengukur korelasi antara seri ENSO ONI pada waktu `t` dengan produksi padi pada waktu `t + lag`. Lag optimal adalah nilai lag positif dengan korelasi negatif terkuat — mengindikasikan berapa bulan setelah anomali iklim, dampaknya paling terasa pada produksi.

**Penting**: Sebelum CCF, selalu verifikasi stasioneritas kedua seri dengan ADF test. Korelasi time-series non-stasioner bisa bersifat spurious.

### Harvest Debt Index (HDI)

```
HDI_i = 0.40 × Z(−r_ENSO_i) + 0.35 × Z(−ΔProduksi_ElNino_i) + 0.25 × Z(CV_i)
```

Dimana `Z()` adalah z-score normalisasi. Skor 0 = paling resiliensi, 100 = paling rentan.

| Komponen | Bobot | Dimensi FAO | Justifikasi |
|----------|-------|-------------|-------------|
| Sensitivitas ENSO (−r) | 40% | Availability | Ketergantungan produksi pada kondisi iklim |
| Delta produksi El Niño | 35% | Stability | Volatilitas kondisional saat anomali |
| Coefficient of Variation | 25% | Stability | Variabilitas umum multi-faktor |

**Catatan**: Bobot ini didasarkan pada pertimbangan teoritis, bukan analisis PCA. Lihat `notebooks/02_sensitivity_analysis.ipynb` untuk uji sensitivitas bobot.

---

## Keterbatasan dan Catatan Metodologi

1. **Resolusi temporal**: Analisis CCF menggunakan data tahunan karena keterbatasan ketersediaan data BPS per musim tanam. Resolusi bulanan atau per subround akan menghasilkan lag yang lebih presisi (dalam bulan, bukan tahun).

2. **Structural break 2018**: BPS mengubah metodologi dari Ubinan ke KSA. Hasil Chow test per provinsi didokumentasikan di `docs/data_quality.md`.

3. **Confounding variables**: Model tidak mengkontrol variabel OPT (hama/penyakit), perubahan kebijakan pupuk, dan kebijakan impor. Ini adalah limitasi yang diakui dan menjadi agenda riset lanjutan.

4. **Bobot HDI**: Pembobotan 40/35/25 tidak dihasilkan dari analisis statistik (PCA/factor analysis), melainkan dari pertimbangan teori. Analisis sensitivitas menunjukkan korelasi Spearman ranking ≥ 0.89 antar konfigurasi bobot yang berbeda.

5. **Cakupan provinsi**: Menggunakan 34 provinsi (sebelum pemekaran Papua 2022). Data empat provinsi baru (Papua Pegunungan, Papua Tengah, Papua Selatan, Papua Barat Daya) digabung ke provinsi induk masing-masing.

---

## Referensi Utama

```bibtex
@article{frey_osborne_2017,
  author  = {Frey, Carl Benedikt and Osborne, Michael A.},
  title   = {The Future of Employment},
  journal = {Technological Forecasting and Social Change},
  year    = {2017}, volume = {114}, pages = {254--280}
}

@report{bps_ksa_2018,
  author      = {{Badan Pusat Statistik}},
  title       = {Metodologi Kerangka Sampel Area untuk Estimasi Produksi Padi},
  institution = {BPS Indonesia},
  year        = {2018},
  url         = {https://www.bps.go.id}
}

@article{iizumi_2014,
  author  = {Iizumi, Toshichika and others},
  title   = {Impacts of El Niño Southern Oscillation on the global yields of major crops},
  journal = {Nature Communications},
  year    = {2014}, volume = {5}, number = {1}, pages = {3712}
}

@report{bmkg_proyeksi_2021,
  author      = {{BMKG}},
  title       = {Proyeksi Iklim Indonesia 2020--2050},
  institution = {Badan Meteorologi, Klimatologi, dan Geofisika},
  year        = {2021},
  url         = {https://www.bmkg.go.id}
}

@report{fao_food_security_2006,
  author      = {{FAO}},
  title       = {Food Security: Policy Brief},
  institution = {Food and Agriculture Organization of the United Nations},
  year        = {2006},
  url         = {https://www.fao.org/fileadmin/templates/faoitaly/documents/pdf/pdf_Food_Security_Cocept_Note.pdf}
}

@article{haylock_mcbride_2001,
  author  = {Haylock, M. and McBride, J.},
  title   = {Spatial coherence and predictability of Indonesian wet season rainfall},
  journal = {Journal of Climate},
  year    = {2001}, volume = {14}, number = {18}, pages = {3882--3887}
}
```

---

## Kontribusi

Proyek ini dikembangkan oleh tim mahasiswa Sains Data UNISBA untuk SIC 2026. Kontribusi, issue, dan pull request disambut baik setelah kompetisi selesai.

---

## Lisensi

Kode dalam repositori ini dilisensikan di bawah [MIT License](LICENSE).

Data yang digunakan bersumber dari lembaga publik (BPS, NOAA, BMKG) dan tunduk pada ketentuan penggunaan masing-masing lembaga tersebut.

---

*Last updated: Mei 2026 | Statistics Data Challenge 2026 — UNISBA*
