# Dokumentasi Metodologi — Utang Panen

## 1. Kerangka Analisis

Analisis ini mengadopsi kerangka **iklim → produksi → harga → kerentanan** yang terdiri dari empat lapisan:

1. **Layer temporal**: Cross-Correlation Function (CCF) untuk mengidentifikasi lag antara anomali iklim dan dampak produksi.
2. **Layer spasial**: Korelasi Pearson & Spearman per provinsi untuk memetakan heterogenitas kerentanan.
3. **Layer komposit**: Harvest Debt Index (HDI) untuk merangkum multi-dimensi kerentanan ke satu angka.
4. **Layer transmisi**: Distributed Lag Model (DLM) untuk menghitung kaskade dari produksi ke harga beras.

---

## 2. Sumber Data dan Keterbatasannya

### ENSO ONI (NOAA)

ONI dihitung sebagai rata-rata bergerak 3-bulan anomali SST di wilayah Niño 3.4 (5°N–5°S, 120°–170°W). Kekuatan: data publik, resolusi bulanan sejak 1950, metodologi konsisten. Keterbatasan: indeks tunggal global yang tidak membedakan respons regional Indonesia — Sumatera dan Kalimantan lebih dipengaruhi Dipole Mode Index (DMI) Samudra Hindia.

### Produksi Padi BPS

Kekuatan: data resmi pemerintah, tersedia per provinsi tahunan. Keterbatasan: **perubahan metodologi 2018** dari Ubinan (ground-truth sample) ke KSA (area sampling berbasis citra satelit) menciptakan potensi structural break. Studi BPS 2018 menunjukkan KSA menghasilkan estimasi lebih rendah 8–12% dibanding Ubinan untuk beberapa provinsi. Semua analisis menjalankan sensitivity analysis dengan koreksi –8%.

---

## 3. Preprocessing

### Penanganan Pemekaran Provinsi

Indonesia mengalami pemekaran provinsi signifikan: 26 (1999) → 33 (2004) → 34 (2012) → 38 (2022). Untuk konsistensi time-series 2000–2024, proyek ini menggunakan **34 provinsi** (pre-2022), dengan empat provinsi hasil pemekaran 2022 digabung ke provinsi induknya.

| Provinsi Baru (2022) | Digabung ke |
|----------------------|-------------|
| Papua Pegunungan | Papua |
| Papua Tengah | Papua |
| Papua Selatan | Papua |
| Papua Barat Daya | Papua Barat |

### Uji Stasioneritas

Augmented Dickey-Fuller (ADF) test dengan lag dipilih berdasarkan kriteria AIC. Hipotesis null: ada unit root (tidak stasioner). Keputusan: jika p < 0.05, tolak H0, series dianggap stasioner → gunakan level. Jika p ≥ 0.05, series tidak stasioner → terapkan first differencing.

### Uji Structural Break

Chow test pada 2018 sebagai titik perubahan metodologi BPS. Jika F-statistic tidak signifikan (p ≥ 0.05), sambungan data Ubinan–KSA dianggap valid untuk analisis jangka panjang.

---

## 4. Cross-Correlation Function (CCF)

**Formula**:

```
CCF(lag) = Corr(ENSO_t, Produksi_{t+lag})
```

Lag optimal = nilai lag positif dengan korelasi Pearson negatif terkuat, menunjukkan berapa tahun setelah El Niño terjadi sebelum dampak produksi paling terasa.

**Multiple comparisons correction**: Pengujian 34 provinsi × beberapa lag = banyak pengujian simultan. Diterapkan Benjamini-Hochberg FDR correction dengan q = 0.10 untuk mengontrol false discovery rate.

**Catatan resolusi**: Data tahunan membatasi presisi lag ke resolusi satu tahun. Untuk mengetahui lag dalam satuan bulan, dibutuhkan data produksi per subround/musim tanam BPS.

---

## 5. Harvest Debt Index (HDI)

### Formulasi

```
HDI_i = 0.40 × Z(−r_ENSO_i) + 0.35 × Z(−ΔProd_ElNino_i) + 0.25 × Z(CV_i)
```

Dimana `Z(x) = (x − min(x)) / (max(x) − min(x)) × 100` (min-max normalisasi ke skala 0–100).

### Komponen dan Justifikasi

| Komponen | Bobot | Variabel | Justifikasi Teori |
|----------|-------|----------|-------------------|
| Sensitivitas ENSO | 40% | `−r_Pearson(ONI, produksi)` | Dimensi *availability* (FAO): ketergantungan produksi pada iklim |
| Delta El Niño | 35% | `−ΔProduksi rata-rata saat El Niño vs normal (%)` | Dimensi *stability*: volatilitas kondisional saat El Niño |
| Variabilitas umum | 25% | `CV = σ/μ × 100` (produksi 2000–2024) | Dimensi *stability*: variabilitas multi-faktor jangka panjang |

### Keterbatasan dan Analisis Sensitivitas

Bobot 40/35/25 didasarkan pada pertimbangan teoritis (FAO Food Security Framework), bukan analisis PCA atau expert elicitation formal. Untuk memvalidasi robustness:

```python
# Lihat notebooks/02_sensitivity_analysis.ipynb
# Uji dengan 4 konfigurasi bobot:
configs = [(40,35,25), (33,33,33), (50,30,20), (35,40,25)]
```

Hasil: korelasi Spearman ranking HDI antar konfigurasi bobot ≥ 0.89, menunjukkan pesan utama robust terhadap pilihan bobot yang wajar.

---

## 6. Confounding Variables yang Tidak Dikontrol

Ini adalah limitasi yang diakui secara eksplisit:

1. **OPT (Organisme Pengganggu Tanaman)**: Serangan wereng, blast, tikus berkorelasi dengan musim hujan tetapi juga merupakan variabel independen. Data SIMOPT Kementan bisa diintegrasikan di versi lanjutan.

2. **Kebijakan pupuk**: Perubahan HPP (Harga Pembelian Pemerintah) dan subsidi pupuk pada 2015 dan 2023 bersamaan dengan El Niño kuat. Dummy variabel kebijakan sebaiknya dimasukkan dalam analisis lanjutan.

3. **Intensitas pertanian (IP)**: Jawa dengan IP 2.8x/tahun vs luar Jawa 1.2x menghasilkan variance absolut berbeda. Normalisasi dengan CV per unit luas tanam lebih tepat untuk perbandingan lintas provinsi.

4. **Adaptasi petani**: Pergeseran varietas (padi tahan kering), pergeseran musim tanam, dan perluasan areal irigasi dapat mereduksi kerentanan secara bertahap — efek yang tidak tertangkap model statis ini.

---

*Dokumentasi ini diperbarui seiring perkembangan analisis. Versi terakhir: Mei 2026.*
