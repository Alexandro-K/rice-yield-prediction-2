import { formatAngka, formatPersenBertanda } from '../utils/format'

const KELAS_KATEGORI = {
  Rendah: 'badge-rendah',
  Sedang: 'badge-sedang',
  Tinggi: 'badge-tinggi',
}

function KartuVegetasi({ label, nilai, data }) {
  return (
    <div className="insight-card">
      <span className="insight-label">{label}</span>
      <span className={`badge ${KELAS_KATEGORI[data.kategori]}`}>{data.kategori}</span>
      <small>Nilai: {nilai.toFixed(4)} · kuartil riwayat kabupaten ini</small>
    </div>
  )
}

function TabelKategori({ judul, satuan, rendahMax, sedangMin, sedangMax, tinggiMin, desimal }) {
  const fmt = (v) => (desimal ? v.toFixed(desimal) : formatAngka(v, 0))
  return (
    <table className="insight-tabel">
      <thead>
        <tr><th>{judul}</th><th>Rentang{satuan ? ` (${satuan})` : ''}</th></tr>
      </thead>
      <tbody>
        <tr><td>Rendah</td><td>Kurang dari {fmt(rendahMax)}</td></tr>
        <tr><td>Sedang</td><td>{fmt(sedangMin)} sampai {fmt(sedangMax)}</td></tr>
        <tr><td>Tinggi</td><td>Lebih dari {fmt(tinggiMin)}</td></tr>
      </tbody>
    </table>
  )
}

function PanelPenjelasan({ insight, loading, error, hasil }) {
  if (loading) {
    return <div className="insight-panel blok-info">Menyusun penjelasan hasil...</div>
  }
  if (error) {
    return (
      <div className="insight-panel blok-info">
        Penjelasan hasil tidak dapat dimuat. Angka prediksi di atas tetap valid.
      </div>
    )
  }
  if (!insight) return null

  const bp = insight.batas_produksi

  return (
    <div className="insight-panel">
      <h2>Penjelasan Hasil</h2>

      <div className="insight-grid insight-grid-2">
        <div className="insight-card">
          <span className="insight-label">Kategori produksi</span>
          <span className={`badge ${KELAS_KATEGORI[insight.kategori_produksi]}`}>
            {insight.kategori_produksi}
          </span>
          <small>{insight.sumber_batas_produksi}</small>
        </div>

        <div className="insight-card">
          <span className="insight-label">Dibanding rata-rata bulan yang sama</span>
          <span className="insight-nilai">
            {insight.selisih_persen_vs_musiman !== null
              ? formatPersenBertanda(insight.selisih_persen_vs_musiman)
              : '-'}
          </span>
          <small>
            {insight.rata_rata_bulan_sama_ton !== null
              ? `Rata-rata historis: ${formatAngka(insight.rata_rata_bulan_sama_ton)} Ton`
              : 'Data pembanding belum cukup untuk bulan ini'}
          </small>
        </div>
      </div>

      <div className="insight-grid insight-grid-3">
        <KartuVegetasi label="Kondisi vegetasi (NDVI)" nilai={hasil.ndvi_mean} data={insight.ndvi} />
        <KartuVegetasi label="Kondisi vegetasi (EVI)" nilai={hasil.evi_mean} data={insight.evi} />
        <KartuVegetasi label="Kondisi vegetasi (SAVI)" nilai={hasil.savi_mean} data={insight.savi} />
      </div>

      <p className="insight-narasi">{insight.narasi_produksi}</p>
      <ul className="insight-bullet">
        {insight.narasi_indeks.map((teks, i) => (
          <li key={i}>{teks}</li>
        ))}
      </ul>

      <div className="insight-tabel-wrap">
        <TabelKategori
          judul="Kategori produksi (bulan ini)" satuan="Ton" desimal={0}
          rendahMax={bp.q25} sedangMin={bp.q25} sedangMax={bp.q75} tinggiMin={bp.q75}
        />
        <TabelKategori
          judul="Kategori vegetasi (NDVI)" desimal={3}
          rendahMax={insight.ndvi.batas.q25} sedangMin={insight.ndvi.batas.q25}
          sedangMax={insight.ndvi.batas.q75} tinggiMin={insight.ndvi.batas.q75}
        />
        <TabelKategori
          judul="Kategori vegetasi (EVI)" desimal={3}
          rendahMax={insight.evi.batas.q25} sedangMin={insight.evi.batas.q25}
          sedangMax={insight.evi.batas.q75} tinggiMin={insight.evi.batas.q75}
        />
        <TabelKategori
          judul="Kategori vegetasi (SAVI)" desimal={3}
          rendahMax={insight.savi.batas.q25} sedangMin={insight.savi.batas.q25}
          sedangMax={insight.savi.batas.q75} tinggiMin={insight.savi.batas.q75}
        />
      </div>

      <small className="insight-catatan">
        Seluruh batas kategori dihitung dari kuartil pertama dan ketiga riwayat data kabupaten yang bersangkutan,
        bukan ambang tetap yang sama untuk semua wilayah.
      </small>
    </div>
  )
}

export default PanelPenjelasan