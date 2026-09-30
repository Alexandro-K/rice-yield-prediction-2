import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // proses GEE dan TabPFN bisa memakan waktu lama, beri ruang hingga 3 menit
})

export async function predictProduksi(kabupaten, tahun, bulan) {
  const response = await apiClient.post('/predict', { kabupaten, tahun, bulan })
  return response.data
}

export async function getMapLayer(kabupaten, tahun, bulan, layer = 'NDVI') {
  const response = await apiClient.post('/map-layer', { kabupaten, tahun, bulan, layer })
  return response.data
}

export async function interpretHasil(hasilPrediksi) {
  const response = await apiClient.post('/interpret', {
    kabupaten: hasilPrediksi.kabupaten,
    tahun: hasilPrediksi.tahun,
    bulan: hasilPrediksi.bulan,
    prediksi_produksi_ton: hasilPrediksi.prediksi_produksi_ton,
    ndvi_mean: hasilPrediksi.ndvi_mean,
    evi_mean: hasilPrediksi.evi_mean,
    savi_mean: hasilPrediksi.savi_mean,
  })
  return response.data
}

export async function getModelInfo() {
  const response = await apiClient.get('/model-info')
  return response.data
}

export async function predictTrajectory(kabupaten, tahun, bulan) {
  const response = await apiClient.post('/predict-trajectory', { kabupaten, tahun, bulan })
  return response.data
}

export const STATUS_MEMERIKSA = 'memeriksa'
export const STATUS_SIAP = 'siap'
export const STATUS_GAGAL = 'gagal'

const WAKTU_MAKSIMAL_MS = 5 * 60 * 1000 // 5 menit
const JEDA_ANTAR_PERCOBAAN_MS = 6000
const TOTAL_PERCOBAAN = Math.ceil(WAKTU_MAKSIMAL_MS / JEDA_ANTAR_PERCOBAAN_MS)

let janjiSiapServer = null

async function periksaSekali(urlHealth) {
  const response = await axios.get(urlHealth, { timeout: 15000, validateStatus: () => true })
  return response.status >= 200 && response.status < 300
}

export function ensureServerAwake(onStatus) {
  const urlHealth = API_BASE_URL.replace(/\/api\/?$/, '/')

  if (!janjiSiapServer) {
    janjiSiapServer = (async () => {
      for (let i = 0; i < TOTAL_PERCOBAAN; i++) {
        onStatus?.(STATUS_MEMERIKSA, i + 1, TOTAL_PERCOBAAN)
        try {
          const berhasil = await periksaSekali(urlHealth)
          if (berhasil) {
            onStatus?.(STATUS_SIAP)
            return true
          }
        } catch {
          // 
        }
        if (i < TOTAL_PERCOBAAN - 1) {
          await new Promise((resolve) => setTimeout(resolve, JEDA_ANTAR_PERCOBAAN_MS))
        }
      }
      onStatus?.(STATUS_GAGAL)
      janjiSiapServer = null 
      return false
    })()
  }

  return janjiSiapServer
}