import { IDENTITAS } from '../data/proyek'

function Footer() {
  const tahun = new Date().getFullYear()
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div>
          <strong>{IDENTITAS.kompetisi}</strong>
          <p>{IDENTITAS.institusi}</p>
        </div>
        <div className="site-footer-catatan">
          <span>&copy; {tahun} {IDENTITAS.kompetisi}</span>
          <span>Data BPS · Citra Sentinel-2 · Model TabPFN</span>
        </div>
      </div>
    </footer>
  )
}

export default Footer