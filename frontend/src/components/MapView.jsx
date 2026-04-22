import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import axios from 'axios'
import { useEffect, useState } from 'react'

const center = [1.264, 103.819]
const API = "http://127.0.0.1:8001"


// 🎯 DRI color
function getColor(dri) {
  if (dri > 75) return 'red'
  if (dri > 40) return 'orange'
  return 'green'
}

// 🌦 Weather color
function getWeatherColor(risk) {
  if (risk > 60) return 'red'
  if (risk > 30) return 'yellow'
  return 'green'
}


export default function MapView() {
  const [shipments, setShipments] = useState([])
  const [vessels, setVessels] = useState([])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const s = await axios.get(`${API}/shipments`)
      const v = await axios.get(`${API}/vessels`)

      setShipments(s.data)
      setVessels(v.data)
    } catch (err) {
      console.error("API ERROR:", err)
    }
  }

  return (
    <MapContainer center={center} zoom={5} style={{ height: '100vh', width: '100%' }}>
      
      {/* 🌍 DARK MAP */}
      <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />

      {/* 🚢 AIS VESSELS */}
      {vessels.map((v, i) => (
        <CircleMarker
          key={"vessel-" + i}
          center={[v.lat, v.lon]}
          radius={4}
          pathOptions={{ color: '#22c55e' }}
        />
      ))}

      {/* 📦 SHIPMENTS */}
      {shipments.map((s, i) => (
        <CircleMarker
          key={"shipment-" + i}
          center={[s.lat, s.lon]}
          radius={8}
          pathOptions={{
            color: getColor(s.dri),
            fillColor: getColor(s.dri)
          }}
        >
          <Popup>
            <strong>{s.id}</strong><br />
            DRI: {s.dri}<br />
            Weather: {s.weather_risk}<br />
            {s.rerouted ? "⚠️ High Risk" : "✅ Stable"}
          </Popup>
        </CircleMarker>
      ))}

      {/* 🌦 WEATHER ZONES */}
      {shipments.map((s, i) => (
        <CircleMarker
          key={"weather-" + i}
          center={[s.lat, s.lon]}
          radius={25}
          pathOptions={{
            color: getWeatherColor(s.weather_risk),
            fillColor: getWeatherColor(s.weather_risk),
            fillOpacity: 0.15
          }}
        >
          <Popup>
            🌦 Weather Risk: {s.weather_risk}
          </Popup>
        </CircleMarker>
      ))}

    </MapContainer>
  )
}