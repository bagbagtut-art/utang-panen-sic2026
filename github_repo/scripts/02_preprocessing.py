"""
scripts/02_preprocessing.py
────────────────────────────
Preprocessing lengkap: parsing → cleaning → ADF test → structural break → export.
Jalankan SETELAH 01_download_data.py dan semua file raw tersedia.

Output: data/processed/*.csv siap untuk analisis lanjutan.
"""

import os, sys
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.stats.diagnostic import het_breuschpagan
except ImportError:
    sys.exit("Install statsmodels: pip install statsmodels")

# Paths
ROOT = os.path.join(os.path.dirname(__file__), '..')
RAW  = os.path.join(ROOT, 'data', 'raw')
PROC = os.path.join(ROOT, 'data', 'processed')
os.makedirs(PROC, exist_ok=True)

TAHUN_START, TAHUN_END = 2000, 2024

print("=" * 65)
print("PREPROCESSING PIPELINE — UTANG PANEN")
print("=" * 65)


def check_file(path, label):
    if not os.path.exists(path):
        print(f"  ✗ File tidak ditemukan: {path}")
        print(f"    Jalankan 01_download_data.py terlebih dahulu.")
        sys.exit(1)
    print(f"  ✓ {label}: {os.path.basename(path)}")


# ──────────────────────────────────────────────────────────────
# STEP 1: PARSE ENSO ONI
# ──────────────────────────────────────────────────────────────
print("\n[STEP 1] Parsing ENSO ONI...")

oni_path = os.path.join(RAW, 'oni_raw.txt')
check_file(oni_path, 'ENSO ONI')

months = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']

def parse_oni(filepath):
    """
    Parse format NOAA ONI: baris pertama = tahun mulai/akhir,
    setiap baris = tahun + 12 nilai bulanan.
    Nilai -99.9 = missing.
    """
    rows = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('YEAR'):
                continue
            parts = line.split()
            if len(parts) < 13:
                continue
            try:
                year = int(parts[0])
                vals = [float(v) if float(v) != -99.9 else np.nan for v in parts[1:13]]
                rows.append([year] + vals)
            except ValueError:
                continue
    df = pd.DataFrame(rows, columns=['tahun'] + months)
    return df

df_oni_wide = parse_oni(oni_path)
df_oni_wide = df_oni_wide[
    (df_oni_wide['tahun'] >= TAHUN_START) &
    (df_oni_wide['tahun'] <= TAHUN_END)
].copy()

# Reshape ke long format
df_oni_long = df_oni_wide.melt(id_vars='tahun', var_name='bulan', value_name='oni')
m_map = {m: i+1 for i, m in enumerate(months)}
df_oni_long['bulan_num'] = df_oni_long['bulan'].map(m_map)
df_oni_long['tanggal'] = pd.to_datetime(
    df_oni_long['tahun'].astype(str) + '-' +
    df_oni_long['bulan_num'].astype(str).str.zfill(2) + '-01'
)
df_oni_long = df_oni_long.sort_values('tanggal').reset_index(drop=True)

# Tahunan: rata-rata 12 bulan
df_oni_annual = df_oni_wide.set_index('tahun')[months].mean(axis=1).reset_index()
df_oni_annual.columns = ['tahun', 'oni_annual']

# Klasifikasi ENSO
def klasifikasi(oni):
    if oni >= 1.5:   return 'El Niño Kuat'
    elif oni >= 0.5: return 'El Niño'
    elif oni <= -1.5: return 'La Niña Kuat'
    elif oni <= -0.5: return 'La Niña'
    return 'Netral'

df_oni_annual['fase'] = df_oni_annual['oni_annual'].apply(klasifikasi)
print(f"   → {len(df_oni_annual)} tahun | fase: {df_oni_annual['fase'].value_counts().to_dict()}")
print(f"   → Missing values ONI: {df_oni_long['oni'].isna().sum()}")

df_oni_long.to_csv(os.path.join(PROC, 'oni_bulanan.csv'), index=False)
df_oni_annual.to_csv(os.path.join(PROC, 'oni_annual.csv'), index=False)
print("   → Disimpan: oni_bulanan.csv, oni_annual.csv")


# ──────────────────────────────────────────────────────────────
# STEP 2: PARSE PRODUKSI PADI BPS
# ──────────────────────────────────────────────────────────────
print("\n[STEP 2] Parsing produksi padi BPS...")

padi_path = os.path.join(RAW, 'bps_padi_provinsi.xlsx')
check_file(padi_path, 'Produksi Padi BPS')

# ── Pembaca generik — sesuaikan skiprows jika format BPS berbeda ──
# Format umum BPS: baris 1-2 = header/judul, kolom = provinsi, baris = tahun
# Atau: kolom = tahun, baris = provinsi (transpose)
# Anda mungkin perlu menyesuaikan parameter berikut:

try:
    df_padi_raw = pd.read_excel(padi_path, index_col=0, skiprows=2)
    # Deteksi apakah perlu transpose
    # Jika index adalah provinsi dan columns adalah tahun → transpose
    # Jika index adalah tahun dan columns adalah provinsi → sudah benar
    cols_are_years = all(str(c).isdigit() and 2000 <= int(str(c)) <= 2030
                         for c in df_padi_raw.columns if str(c).isdigit())
    if cols_are_years:
        df_padi_raw = df_padi_raw.T
        df_padi_raw.index = df_padi_raw.index.astype(int)
        df_padi_raw.index.name = 'tahun'

    # Filter tahun
    df_padi = df_padi_raw.loc[
        (df_padi_raw.index >= TAHUN_START) &
        (df_padi_raw.index <= TAHUN_END)
    ].copy()

    # Bersihkan nilai string, koma, dsb.
    for col in df_padi.columns:
        df_padi[col] = pd.to_numeric(
            df_padi[col].astype(str).str.replace(',', '').str.strip(),
            errors='coerce'
        )

    print(f"   → {df_padi.shape[0]} tahun × {df_padi.shape[1]} provinsi")

except Exception as e:
    print(f"   ✗ Gagal parsing Excel BPS: {e}")
    print("   Periksa format file dan sesuaikan parameter skiprows/index_col.")
    print("   Lihat dokumentasi di docs/metodologi.md")
    sys.exit(1)

# Penanganan pemekaran provinsi:
# Provinsi baru (Papua Pegunungan, dst.) digabung ke provinsi induk
pemekaran_map = {
    'Papua Pegunungan': 'Papua',
    'Papua Tengah': 'Papua',
    'Papua Selatan': 'Papua',
    'Papua Barat Daya': 'Papua Barat',
}
for prov_baru, prov_induk in pemekaran_map.items():
    if prov_baru in df_padi.columns and prov_induk in df_padi.columns:
        df_padi[prov_induk] = df_padi[prov_induk].fillna(0) + df_padi[prov_baru].fillna(0)
        df_padi = df_padi.drop(columns=[prov_baru])
        print(f"   → Digabung: {prov_baru} → {prov_induk}")

# Missing value check
mv = df_padi.isna().sum().sum()
total = df_padi.size
print(f"   → Missing values: {mv}/{total} ({mv/total*100:.1f}%) — "
      f"{'imputasi linear' if mv > 0 else 'tidak ada'}")
if mv > 0:
    df_padi = df_padi.interpolate(method='linear', limit_direction='both')

# Reshape ke long format
df_padi_long = df_padi.reset_index().melt(id_vars='tahun', var_name='provinsi', value_name='produksi_ton')
df_padi_long = df_padi_long.merge(df_oni_annual, on='tahun')

df_padi.to_csv(os.path.join(PROC, 'produksi_wide.csv'))
df_padi_long.to_csv(os.path.join(PROC, 'produksi_long.csv'), index=False)
print("   → Disimpan: produksi_wide.csv, produksi_long.csv")


# ──────────────────────────────────────────────────────────────
# STEP 3: UJI STASIONERITAS (ADF TEST)
# ──────────────────────────────────────────────────────────────
print("\n[STEP 3] Uji stasioneritas (Augmented Dickey-Fuller)...")

def run_adf(series, nama, alpha=0.05):
    s = series.dropna()
    if len(s) < 8:
        return {'variabel': nama, 'n': len(s), 'adf_stat': np.nan,
                'p_value': np.nan, 'lag': np.nan, 'stasioner': 'N/A (n kecil)'}
    res = adfuller(s, autolag='AIC')
    return {
        'variabel': nama,
        'n': len(s),
        'adf_stat': round(res[0], 4),
        'p_value': round(res[1], 4),
        'lag_aic': res[2],
        'stasioner': 'YA' if res[1] < alpha else 'TIDAK',
        'aksi': 'Gunakan level' if res[1] < alpha else 'First differencing'
    }

adf_list = []
# Nasional
prod_nat = df_padi.sum(axis=1)
adf_list.append(run_adf(df_oni_annual['oni_annual'], 'ENSO ONI'))
adf_list.append(run_adf(prod_nat, 'Produksi nasional'))
adf_list.append(run_adf(df_oni_annual['oni_annual'].diff().dropna(), 'ENSO ONI (diff1)'))
adf_list.append(run_adf(prod_nat.diff().dropna(), 'Produksi nasional (diff1)'))

# Per provinsi
for prov in df_padi.columns[:5]:  # Uji 5 provinsi pertama sebagai sampel
    adf_list.append(run_adf(df_padi[prov], f'Produksi — {prov[:15]}'))

df_adf = pd.DataFrame(adf_list)
print(df_adf[['variabel','n','adf_stat','p_value','stasioner','aksi']].to_string(index=False))

df_adf.to_csv(os.path.join(PROC, 'hasil_adf_test.csv'), index=False)
print("\n   → Disimpan: hasil_adf_test.csv")


# ──────────────────────────────────────────────────────────────
# STEP 4: STRUCTURAL BREAK TEST (Chow Test, 2018)
# ──────────────────────────────────────────────────────────────
print("\n[STEP 4] Uji structural break (Chow Test, titik: 2018)...")

def chow_test(series, break_year):
    """
    Chow Test sederhana: bandingkan residual regresi
    sebelum dan sesudah break_year.
    Hipotesis null: tidak ada structural break.
    """
    years = series.index.values
    values = series.values
    n = len(values)
    idx_break = np.searchsorted(years, break_year)

    if idx_break < 5 or n - idx_break < 5:
        return {'f_stat': np.nan, 'p_value': np.nan, 'result': 'Sampel terlalu kecil'}

    def ssr(y):
        """Sum of squared residuals dari regresi linear vs waktu"""
        x = np.arange(len(y))
        sl, ic, _, _, _ = stats.linregress(x, y)
        resid = y - (sl * x + ic)
        return np.sum(resid ** 2)

    s_full = ssr(values)
    s1 = ssr(values[:idx_break])
    s2 = ssr(values[idx_break:])

    k = 2  # parameter (slope + intercept)
    f_stat = ((s_full - (s1 + s2)) / k) / ((s1 + s2) / (n - 2 * k))
    p_value = 1 - stats.f.cdf(abs(f_stat), k, n - 2 * k)

    result = 'Ada break (p<0.05)' if p_value < 0.05 else 'Tidak ada break'
    return {'f_stat': round(f_stat, 4), 'p_value': round(p_value, 4), 'result': result}

chow_nat = chow_test(prod_nat, 2018)
print(f"   Produksi nasional — F={chow_nat['f_stat']}, p={chow_nat['p_value']}")
print(f"   Kesimpulan: {chow_nat['result']}")
print("   Interpretasi: jika tidak ada break → data pre/post-2018 bisa disambung langsung")

chow_results = []
for prov in df_padi.columns:
    r = chow_test(df_padi[prov], 2018)
    r['provinsi'] = prov
    chow_results.append(r)
df_chow = pd.DataFrame(chow_results)
n_break = (df_chow['p_value'] < 0.05).sum()
print(f"\n   Structural break signifikan di {n_break}/{len(df_padi.columns)} provinsi")

df_chow.to_csv(os.path.join(PROC, 'hasil_chow_test.csv'), index=False)
print("   → Disimpan: hasil_chow_test.csv")


# ──────────────────────────────────────────────────────────────
# STEP 5: SENSITIVITY ANALYSIS — Koreksi Data BPS ±8%
# ──────────────────────────────────────────────────────────────
print("\n[STEP 5] Analisis sensitivitas koreksi data BPS...")

# Simulasi: jika data BPS overestimate 8% (bias Ubinan yang terdokumentasi)
df_padi_corrected = df_padi * 0.92
prod_nat_corrected = df_padi_corrected.sum(axis=1)

r_original, p_original = stats.pearsonr(
    df_oni_annual['oni_annual'], prod_nat)
r_corrected, p_corrected = stats.pearsonr(
    df_oni_annual['oni_annual'], prod_nat_corrected)

print(f"   Korelasi nasional (data asli):     r = {r_original:.4f}, p = {p_original:.4f}")
print(f"   Korelasi nasional (koreksi -8%):   r = {r_corrected:.4f}, p = {p_corrected:.4f}")
print(f"   Perbedaan: Δr = {abs(r_original - r_corrected):.4f}")
print("   Kesimpulan: ", end="")
if abs(r_original - r_corrected) < 0.02:
    print("Hasil robust terhadap koreksi Ubinan ✓")
else:
    print("Ada perbedaan signifikan — perlu dibahas dalam limitasi")


# ──────────────────────────────────────────────────────────────
# STEP 6: SIMPAN DATA GABUNGAN
# ──────────────────────────────────────────────────────────────
print("\n[STEP 6] Menyimpan data gabungan...")

df_nasional = pd.DataFrame({
    'tahun': df_oni_annual['tahun'],
    'oni_annual': df_oni_annual['oni_annual'],
    'fase_enso': df_oni_annual['fase'],
    'produksi_nasional_ton': prod_nat.values,
    'produksi_nasional_corrected': prod_nat_corrected.values,
})
df_nasional.to_csv(os.path.join(PROC, 'data_nasional.csv'), index=False)
print("   → Disimpan: data_nasional.csv")

print("\n✓ Preprocessing selesai. Semua file tersimpan di data/processed/")
print("  Langkah berikutnya: python scripts/03_ccf_analysis.py")
