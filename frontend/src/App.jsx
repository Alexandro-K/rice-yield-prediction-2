import { useState } from 'react'
import { predictProduksi, getMapLayer, interpretHasil, predictTrajectory } from './api/client'
import PetaSawah from './components/PetaSawah'
import PanelPenjelasan from './components/PanelPenjelasan'
import GrafikRiwayat from './components/GrafikRiwayat'
import NavTabs from './components/NavTabs'
import PerformaModel from './components/PerformaModel'
import TentangProyek from './components/TentangProyek'
import Footer from './components/Footer'
import { formatAngka } from './utils/format'

const KABUPATEN_LIST = ['Bojonegoro', 'Jember', 'Ngawi', 'Tuban', 'Lamongan']
const BULAN_LIST = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
]

function App() {
  const [tab, setTab] = useState('prediksi')
  const [kabupaten, setKabupaten] = useState('Ngawi')
  const [tahun, setTahun] = useState(2024)
  const [bulan, setBulan] = useState(6)
  const [hasil, setHasil] = useState(null)
  const [mapData, setMapData] = useState(null)
  const [insight, setInsight] = useState(null)
  const [trajectory, setTrajectory] = useState(null)
  const [insightLoading, setInsightLoading] = useState(false)
  const [insightError, setInsightError] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [statusServer, setStatusServer] = useState(null)

  const handlePrediksi = async () => {
    setLoading(true)
    setError(null)
    setHasil(null)
    setMapData(null)
    setInsight(null)
    setTrajectory(null)
    setInsightError(false)

    setStatusServer('memeriksa')
    const serverSiap = await bangunkanServer()
    if (!serverSiap) {
      setError('Server sedang tidak dapat dijangkau. Silakan coba lagi dalam beberapa saat.')
      setLoading(false)
      setStatusServer(null)
      return
    }
    setStatusServer(null)

    const janjiPeta = getMapLayer(kabupaten, tahun, bulan, 'NDVI').then(
      (data) => ({ ok: true, data }),
      () => ({ ok: false }),
    )

    try {
      const dataPrediksi = await predictProduksi(kabupaten, tahun, bulan)
      setHasil(dataPrediksi)

      setInsightLoading(true)
      try {
        const dataInsight = await interpretHasil(dataPrediksi)
        setInsight(dataInsight)
      } catch {
        setInsightError(true)
      } finally {
        setInsightLoading(false)
      }

      try {
        const dataTrajectory = await predictTrajectory(kabupaten, tahun, bulan)
        setTrajectory(dataTrajectory)
      } catch {
        setTrajectory(null)
      }

      const hasilPeta = await janjiPeta
      if (hasilPeta.ok) setMapData(hasilPeta.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Terjadi kesalahan saat memproses prediksi.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <NavTabs aktif={tab} onGanti={setTab} />

      <div className="app-container">
        {tab === 'prediksi' && (
          <>
            <div className="form-panel">
              <label>
                Kabupaten
                <select value={kabupaten} onChange={(e) => setKabupaten(e.target.value)}>
                  {KABUPATEN_LIST.map((kab) => (
                    <option key={kab} value={kab}>{kab}</option>
                  ))}
                </select>
              </label>

              <label>
                Tahun
                <input
                  type="number"
                  value={tahun}
                  min={2019}
                  max={2026}
                  onChange={(e) => setTahun(Number(e.target.value))}
                />
              </label>

              <label>
                Bulan
                <select value={bulan} onChange={(e) => setBulan(Number(e.target.value))}>
                  {BULAN_LIST.map((nama, idx) => (
                    <option key={nama} value={idx + 1}>{nama}</option>
                  ))}
                </select>
              </label>

              <button onClick={handlePrediksi} disabled={loading}>
                {statusServer === 'memeriksa'
                  ? 'Membangunkan server, mohon tunggu...'
                  : loading
                    ? 'Memproses (bisa memakan waktu sekitar 1 menit)...'
                    : 'Prediksi'}
              </button>
            </div>

            {error && <div className="error-panel">{error}</div>}

            {hasil && (
              <div className="result-panel">
                <h2>Hasil Prediksi - {hasil.kabupaten}, {BULAN_LIST[hasil.bulan - 1]} {hasil.tahun}</h2>
                <p className="prediksi-utama">
                  {formatAngka(hasil.prediksi_produksi_ton)} Ton
                </p>
                <div className="index-grid">
                  <div><span>NDVI</span>{hasil.ndvi_mean.toFixed(4)}</div>
                  <div><span>EVI</span>{hasil.evi_mean.toFixed(4)}</div>
                  <div><span>SAVI</span>{hasil.savi_mean.toFixed(4)}</div>
                  <div><span>Jumlah Citra Terpakai</span>{hasil.jumlah_citra}</div>
                </div>
              </div>
            )}

            {hasil && (
              <PanelPenjelasan insight={insight} loading={insightLoading} error={insightError} hasil={hasil} />
            )}

            {hasil && insight && (
              <GrafikRiwayat insight={insight} hasil={hasil} trajectory={trajectory} />
            )}

            <div className="map-panel">
              <PetaSawah mapData={mapData} />
            </div>
          </>
        )}

        {tab === 'performa' && <PerformaModel />}
        {tab === 'tentang' && <TentangProyek />}
      </div>

      <Footer />
    </>
  )
}

export default App