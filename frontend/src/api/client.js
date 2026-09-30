import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, 
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

async function bangunkanServer(maksimalPercobaan = 5, jedaMs = 4000) {
  const urlHealth = API_BASE_URL.replace(/\/api\/?$/, '/')
  for (let i = 0; i < maksimalPercobaan; i++) {
    try {
      await axios.get(urlHealth, { timeout: 10000 })
      return true
    } catch {
      if (i < maksimalPercobaan - 1) {
        await new Promise((resolve) => setTimeout(resolve, jedaMs))
      }
    }
  }
  return false
}

export { bangunkanServer }