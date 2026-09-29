import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import { useEffect } from 'react'

function FlyToCenter({ lat, lon }) {
  const map = useMap()
  useEffect(() => {
    if (lat && lon) {
      map.flyTo([lat, lon], 11)
    }
  }, [lat, lon, map])
  return null
}

function PetaSawah({ mapData }) {
  if (!mapData) {
    return (
      <div className="peta-placeholder">
        Peta akan muncul di sini setelah prediksi dijalankan.
      </div>
    )
  }

  const { tile_url, batas_geojson, sawah_geojson, center_lat, center_lon } = mapData

  return (
    <MapContainer
      center={[center_lat, center_lon]}
      zoom={11}
      style={{ height: '450px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      <TileLayer url={tile_url} opacity={0.75} />
      <GeoJSON
        data={batas_geojson}
        style={{ color: '#2c3e50', weight: 2, fillOpacity: 0 }}
      />
      <GeoJSON
        data={sawah_geojson}
        style={{ color: '#e74c3c', weight: 1, fillOpacity: 0.15 }}
      />
      <FlyToCenter lat={center_lat} lon={center_lon} />
    </MapContainer>
  )
}

export default PetaSawah