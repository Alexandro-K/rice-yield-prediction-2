import {
  IDENTITAS, ANGGOTA, RINGKASAN, ALUR, CARA_KERJA, SUMBER_DATA, KETERBATASAN,
} from '../data/proyek'

function TentangProyek() {
  return (
    <>
      <div className="blok">
        <h2>Ringkasan</h2>
        <p className="blok-teks">{RINGKASAN}</p>
      </div>

      <div className="blok">
        <h2>Alur Sistem</h2>
        <ol className="alur">
          {ALUR.map((langkah, i) => (
            <li key={langkah.judul} className="alur-langkah">
              <div className="alur-nomor">{i + 1}</div>
              <div className="alur-isi">
                <h3>{langkah.judul}</h3>
                <p>{langkah.isi}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>

      <div className="blok">
        <h2>Cara Kerja Saat Tombol Prediksi Ditekan</h2>
        <ol className="daftar">
          {CARA_KERJA.map((teks) => (
            <li key={teks}>{teks}</li>
          ))}
        </ol>
      </div>

      <div className="blok">
        <h2>Sumber Data dan Model</h2>
        <table className="insight-tabel">
          <thead>
            <tr>
              <th style={{ width: '22%' }}>Komponen</th>
              <th>Keterangan</th>
            </tr>
          </thead>
          <tbody>
            {SUMBER_DATA.map((baris) => (
              <tr key={baris.komponen}>
                <td>{baris.komponen}</td>
                <td>{baris.keterangan}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="blok">
        <h2>Keterbatasan</h2>
        <ul className="daftar">
          {KETERBATASAN.map((teks) => (
            <li key={teks}>{teks}</li>
          ))}
        </ul>
      </div>

      <div className="blok">
        <h2>Tim Pengembang</h2>
        <p className="blok-teks">
          {IDENTITAS.kompetisi}. {IDENTITAS.institusi}.
        </p>
        <div className="tim-grid">
          {ANGGOTA.map((a, i) => (
            <div key={`anggota-${i}`} className="tim-kartu">
              <strong>{a.nama}</strong>
              <span>NPM: {a.npm}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

export default TentangProyek