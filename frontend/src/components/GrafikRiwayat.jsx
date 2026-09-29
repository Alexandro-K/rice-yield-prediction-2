import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { formatAngka } from '../utils/format'

const BULAN_SINGKAT = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
const buatLabel = (tahun, bulan) => `${BULAN_SINGKAT[bulan - 1]} ${tahun}`

function susunData(riwayat, tahun, bulan, prediksi, titikAntara) {
  const peta = new Map()

  riwayat.forEach((t) => {
    const kunci = t.tahun * 12 + (t.bulan - 1)
    peta.set(kunci, { kunci, label: buatLabel(t.tahun, t.bulan), aktual: t.produksi_ton })
  })

  const ambil = (kunci, t, b) => peta.get(kunci) || { kunci, label: buatLabel(t, b) }

  titikAntara.forEach((p) => {
    const kunci = p.tahun * 12 + (p.bulan - 1)
    peta.set(kunci, {
      ...ambil(kunci, p.tahun, p.bulan),
      antara: p.prediksi_produksi_ton,
      jembatan: p.prediksi_produksi_ton,
    })
  })

  const kunciTarget = tahun * 12 + (bulan - 1)
  const titikTarget = ambil(kunciTarget, tahun, bulan)
  peta.set(kunciTarget, {
    ...titikTarget,
    prediksi,
    jembatan: prediksi,
    aktualPeriode: titikTarget.aktual,
  })

  const kunciAwal = titikAntara.length > 0
    ? Math.min(...titikAntara.map((p) => p.tahun * 12 + (p.bulan - 1)))
    : kunciTarget
  const jangkar = peta.get(kunciAwal - 1)
  if (jangkar && jangkar.aktual !== undefined) {
    peta.set(kunciAwal - 1, { ...jangkar, jembatan: jangkar.aktual })
  }

  const semuaKunci = Array.from(peta.keys())
  const kunciMin = Math.min(...semuaKunci)
  const kunciMaks = Math.max(...semuaKunci)
  const hasil = []
  for (let k = kunciMin; k <= kunciMaks; k++) {
    hasil.push(peta.get(k) || { kunci: k, label: buatLabel(Math.floor(k / 12), (k % 12) + 1) })
  }
  return hasil
}

function GrafikRiwayat({ insight, hasil, trajectory }) {
  if (!insight || !hasil) return null

  const titikAntara = trajectory?.titik || []
  const dilewati = trajectory?.bulan_dilewati || []

  const data = susunData(
    insight.riwayat_produksi,
    hasil.tahun,
    hasil.bulan,
    hasil.prediksi_produksi_ton,
    titikAntara,
  )
  const labelPrediksi = buatLabel(hasil.tahun, hasil.bulan)
  const adaAktual = data.some((d) => d.aktualPeriode !== undefined)

  const riwayat = insight.riwayat_produksi
  const terakhir = riwayat[riwayat.length - 1]
  const melampauiData =
    hasil.tahun * 12 + hasil.bulan > terakhir.tahun * 12 + terakhir.bulan

  return (
    <div className="grafik-panel">
      <h2>Riwayat Produksi {hasil.kabupaten}</h2>
      <p className="grafik-keterangan">
        Garis putus-putus oranye menunjukkan prediksi dari bulan setelah data terakhir hingga bulan target.
        Titik oranye besar adalah hasil prediksi periode yang dipilih
        {adaAktual ? ', titik hijau tua adalah data aktual pada periode yang sama.' : '.'}
      </p>

      {melampauiData && (
        <p className="grafik-keterangan">
          Data produksi aktual dalam dataset berakhir pada {buatLabel(terakhir.tahun, terakhir.bulan)}.
          Prediksi setelah bulan tersebut tidak dapat dibandingkan dengan data aktual.
        </p>
      )}

      {dilewati.length > 0 && (
        <p className="grafik-keterangan">
          Bulan berikut tidak diprediksi karena data indeks vegetasinya belum lengkap: {dilewati.join(', ')}.
        </p>
      )}

      <div style={{ width: '100%', height: 340 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e3e9e5" />
            <XAxis dataKey="label" interval="preserveStartEnd" minTickGap={32} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => formatAngka(v, 0)} width={70} />
            <Tooltip formatter={(nilai) => `${formatAngka(nilai)} Ton`} />
            <Legend />
            <ReferenceLine x={labelPrediksi} stroke="#d97706" strokeOpacity={0.5} strokeDasharray="3 3" />

            <Line
              type="monotone"
              dataKey="aktual"
              name="Produksi historis"
              stroke="#3b6e50"
              strokeWidth={2}
              dot={false}
              connectNulls
            />
            <Line
              type="linear"
              dataKey="jembatan"
              stroke="#d97706"
              strokeWidth={2}
              strokeDasharray="5 4"
              dot={false}
              connectNulls
              legendType="none"
              tooltipType="none"
              isAnimationActive={false}
            />
            {titikAntara.length > 0 && (
              <Line
                type="linear"
                dataKey="antara"
                name="Prediksi bulan sebelum target"
                stroke="#f59e0b"
                strokeWidth={0}
                legendType="circle"
                dot={{ r: 3.5, fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 1 }}
                isAnimationActive={false}
              />
            )}
            {adaAktual && (
              <Line
                type="linear"
                dataKey="aktualPeriode"
                name="Aktual periode ini"
                stroke="#1f4d2c"
                strokeWidth={0}
                legendType="circle"
                dot={{ r: 6, fill: '#1f4d2c', stroke: '#ffffff', strokeWidth: 2 }}
                isAnimationActive={false}
              />
            )}
            <Line
              type="linear"
              dataKey="prediksi"
              name="Prediksi periode terpilih"
              stroke="#d97706"
              strokeWidth={0}
              legendType="circle"
              dot={{ r: 7, fill: '#d97706', stroke: '#ffffff', strokeWidth: 2 }}
              activeDot={{ r: 9 }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default GrafikRiwayat