const TAB = [
  { id: 'prediksi', label: 'Prediksi' },
  { id: 'performa', label: 'Performa Model' },
  { id: 'tentang', label: 'Tentang Proyek' },
]

function NavTabs({ aktif, onGanti }) {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <div className="site-brand">
          <span className="site-brand-judul">Prediksi Produksi Padi</span>
          <span className="site-brand-sub">Jawa Timur · Citra Sentinel-2</span>
        </div>
        <nav className="nav-tabs" role="tablist">
          {TAB.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={aktif === t.id}
              className={`nav-tab ${aktif === t.id ? 'aktif' : ''}`}
              onClick={() => onGanti(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}

export default NavTabs