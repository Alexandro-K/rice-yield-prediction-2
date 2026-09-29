import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { getModelInfo } from '../api/client'
import { formatAngka } from '../utils/format'

function PerformaModel() {
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    let batal = false
    getModelInfo()
      .then((data) => { if (!batal) setInfo(data) })
      .catch(() => { if (!batal) setError(true) })
      .finally(() => { if (!batal) setLoading(false) })
    return () => { batal = true }
  }, [])

  if (loading) return <div className="blok blok-info">Memuat informasi model...</div>
  if (error || !info) {
    return (
      <div className="blok blok-info">
        Informasi model tidak dapat dimuat. Server mungkin sedang aktif kembali; coba beberapa saat lagi.
      </div>
    )
  }

  const m = info.metrik
  const kartu = [
    {
      label: 'MAE',
      nilai: `${formatAngka(m.mae_ton, 0)} Ton`,
      arti: 'Rata-rata selisih absolut antara prediksi dan produksi aktual per bulan.',
    },
    {
      label: 'RMSE',
      nilai: `${formatAngka(m.rmse_ton, 0)} Ton`,
      arti: 'Seperti MAE, tetapi memberi bobot lebih pada kesalahan yang besar.',
    },
    {
      label: 'R2',
      nilai: formatAngka(m.r2, 3),
      arti: 'Proporsi variasi produksi yang dijelaskan model. Nilai 1 berarti sempurna.',
    },
    {
      label: 'MAE relatif',
      nilai: `${formatAngka(m.mae_relatif_persen, 1)}%`,
      arti: 'MAE dibagi rata-rata produksi aktual pada data uji.',
    },
  ]

  const dataKelompok = (info.kepentingan_kelompok_fitur || []).map((k) => ({
    kelompok: k.kelompok,
    persen: Number(k.persen.toFixed(1)),
  }))

  const perbandingan = info.perbandingan_model || []

  return (
    <>
      <div className="blok">
        <h2>Performa Model pada Data Uji</h2>
        <p className="blok-teks">
          Model: {info.model}. Dilatih dengan data {info.data_latih_evaluasi.toLowerCase()} dan diuji pada
          data {info.data_uji.toLowerCase()} ({info.jumlah_data_uji} observasi), menggunakan {info.jumlah_fitur} fitur.
        </p>

        <div className="metrik-grid">
          {kartu.map((k) => (
            <div key={k.label} className="metrik-kartu">
              <span className="insight-label">{k.label}</span>
              <span className="insight-nilai">{k.nilai}</span>
              <small>{k.arti}</small>
            </div>
          ))}
        </div>
      </div>

      {perbandingan.length > 0 && (
        <div className="blok">
          <h2>Perbandingan Model</h2>
          <table className="insight-tabel">
            <thead>
              <tr>
                <th>Model</th>
                <th>MAE (Ton)</th>
                <th>RMSE (Ton)</th>
                <th>R2</th>
              </tr>
            </thead>
            <tbody>
              {perbandingan.map((p) => (
                <tr key={p.model}>
                  <td>{p.model}</td>
                  <td>{formatAngka(p.mae_ton, 0)}</td>
                  <td>{formatAngka(p.rmse_ton, 0)}</td>
                  <td>{formatAngka(p.r2, 3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="blok">
        <h2>Faktor yang Paling Memengaruhi Prediksi</h2>
        <p className="blok-teks">
          Setiap kelompok fitur diacak secara bergantian pada data uji, lalu diukur seberapa besar kesalahan
          prediksi meningkat. Semakin besar persentasenya, semakin besar peran kelompok tersebut.
        </p>
        <div style={{ width: '100%', height: dataKelompok.length * 44 + 60 }}>
          <ResponsiveContainer>
            <BarChart
              data={dataKelompok}
              layout="vertical"
              margin={{ top: 8, right: 32, left: 8, bottom: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e3e9e5" horizontal={false} />
              <XAxis type="number" tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="kelompok" width={250} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v) => `${formatAngka(v, 1)}%`} />
              <Bar dataKey="persen" name="Kontribusi" fill="#2f7d46" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="blok">
        <h2>Catatan Metodologi</h2>
        <p className="blok-teks">{info.catatan}</p>
      </div>
    </>
  )
}

export default PerformaModel