export const IDENTITAS = {
  kompetisi: 'KOMPRES 16 (2026)',
  namaTim: 'Nama Tim',                 // ISI
  institusi: 'Universitas Gunadarma',
}

export const ANGGOTA = [
  { nama: 'Nama Anggota 1', npm: 'NPM' },   // ISI
  { nama: 'Nama Anggota 2', npm: 'NPM' },   // ISI
  { nama: 'Nama Anggota 3', npm: 'NPM' },   // ISI
  { nama: 'Nama Anggota 4', npm: 'NPM' },   // ISI
]

export const RINGKASAN =
  'Aplikasi ini memperkirakan produksi padi bulanan tingkat kabupaten di Jawa Timur ' +
  '(Bojonegoro, Jember, Ngawi, Tuban, dan Lamongan) dari indeks vegetasi yang dihitung ' +
  'dari citra satelit Sentinel-2. Pengguna cukup memilih kabupaten, tahun, dan bulan; ' +
  'seluruh pengolahan citra dan prediksi dijalankan otomatis oleh server.'

export const ALUR = [
  {
    judul: 'Citra satelit Sentinel-2',
    isi: 'Citra permukaan bumi dari Sentinel-2 Level-2A diakses melalui Google Earth Engine pada resolusi 10 meter.',
  },
  {
    judul: 'Pra-pemrosesan citra',
    isi: 'Piksel berawan disaring dengan s2cloudless, lalu citra dalam satu bulan digabung menjadi satu komposit median.',
  },
  {
    judul: 'Indeks vegetasi pada lahan sawah',
    isi: 'NDVI, EVI, dan SAVI dihitung, kemudian dirata-ratakan hanya pada area sawah tiap kabupaten.',
  },
  {
    judul: 'Rekayasa fitur',
    isi: 'Indeks bulan berjalan digabung dengan nilai bulan sebelumnya (lag), perubahan antarbulan, rata-rata bergulir, tren, pola musiman, dan identitas wilayah menjadi 18 fitur.',
  },
  {
    judul: 'Model prediksi TabPFN',
    isi: 'Fitur diproses oleh model TabPFN yang hiperparameternya dituning, dan menghasilkan estimasi produksi dalam Ton.',
  },
  {
    judul: 'Prediksi dan penjelasan hasil',
    isi: 'Hasil dibandingkan dengan statistik historis kabupaten untuk menyusun kategori, penjelasan, grafik riwayat, dan peta.',
  },
]

export const CARA_KERJA = [
  'Pengguna memilih kabupaten, tahun, dan bulan, lalu menekan tombol Prediksi.',
  'Server mengambil citra Sentinel-2 bulan tersebut dari Google Earth Engine, menyaring awan, membentuk komposit median, dan menghitung rata-rata NDVI, EVI, dan SAVI pada area sawah kabupaten.',
  'Indeks dua bulan sebelumnya diambil dari basis data historis untuk membentuk fitur lag, delta, tren, dan rata-rata bergulir. Jika data dua bulan sebelumnya belum lengkap, prediksi ditolak agar tidak menghasilkan angka yang keliru.',
  'Ke-18 fitur dikirim ke model TabPFN yang mengembalikan estimasi produksi dalam Ton.',
  'Hasil dibandingkan dengan statistik historis untuk menyusun penjelasan dan grafik riwayat. Server juga menghitung prediksi bulan-bulan antara data terakhir dan bulan target, sementara peta menampilkan komposit NDVI dan batas area sawah.',
]

export const SUMBER_DATA = [
  { komponen: 'Citra satelit', keterangan: 'Sentinel-2 Level-2A (COPERNICUS/S2_SR_HARMONIZED) melalui Google Earth Engine, resolusi 10 meter.' },
  { komponen: 'Penyaringan awan', keterangan: 'Sentinel-2 Cloud Probability (s2cloudless) dengan ambang probabilitas awan 40%.' },
  { komponen: 'Area analisis', keterangan: 'Batas administrasi dan lahan sawah kabupaten dari data Rupabumi Indonesia (RBI) skala 1:25.000.' },   // ISI: pastikan sesuai
  { komponen: 'Data produksi', keterangan: 'Data produksi padi bulanan per kabupaten dari Badan Pusat Statistik (BPS), periode 2019 sampai 2024.' },   // ISI: pastikan sesuai
  { komponen: 'Model', keterangan: 'TabPFN (regresi) dengan hiperparameter dituning menggunakan Optuna. Pada tahap eksperimen dibandingkan dengan TimesFM dan TimeGPT.' },
  { komponen: 'Skema evaluasi', keterangan: 'Model dilatih dengan data sampai 2023 dan diuji pada data 2024. Model pada aplikasi dilatih ulang dengan seluruh data yang tersedia.' },
  { komponen: 'Teknologi aplikasi', keterangan: 'Backend FastAPI, frontend React dengan Leaflet dan Recharts, dijalankan di SnapDeploy dan Vercel.' },
]

export const KETERBATASAN = [
  'Model dilatih dari data lima kabupaten periode 2019 sampai 2024. Prediksi di luar rentang tersebut merupakan ekstrapolasi sehingga tingkat kepastiannya lebih rendah.',
  'Data produksi aktual dalam dataset berakhir pada Desember 2024, sehingga prediksi setelah bulan tersebut tidak dapat dibandingkan dengan data aktual.',
  'Evaluasi memakai satu tahun data uji (2024), sehingga metrik bersifat indikatif dan belum mencerminkan seluruh kondisi.',
  'Kualitas indeks vegetasi bergantung pada ketersediaan citra bebas awan. Pada bulan dengan tutupan awan tebal, jumlah citra dapat sedikit atau tidak tersedia.',
  'Indeks dirata-ratakan per kabupaten sehingga tidak menggambarkan variasi antar kecamatan atau antar lahan.',
  'Ambang kategori vegetasi (NDVI) merupakan pendekatan umum dan belum dikalibrasi khusus untuk lahan sawah di wilayah studi.',
  'Kategori dan penjelasan hasil bersifat indikatif berdasarkan pola historis, dan bukan pengganti data produksi resmi.',
]

export const PENGANTAR = {
  paragraf:
    'Aplikasi ini memperkirakan produksi padi bulanan tingkat kabupaten di Jawa Timur menggunakan indeks ' +
    'vegetasi (NDVI, EVI, SAVI) yang dihitung dari citra satelit Sentinel-2, dikombinasikan dengan model ' +
    'machine learning TabPFN. Prediksi ini membantu memberi gambaran awal kondisi produksi padi tanpa ' +
    'menunggu laporan resmi, misalnya untuk pemantauan dini atau perencanaan yang bersifat indikatif.',
  poin: [
    { label: 'Kabupaten tersedia', isi: 'Bojonegoro, Jember, Ngawi, Tuban, dan Lamongan' },
    { label: 'Rentang periode', isi: 'Tahun 2019 sampai 2026' },
    { label: 'Indeks yang digunakan', isi: 'NDVI, EVI, dan SAVI dari citra Sentinel-2' },
  ],
}