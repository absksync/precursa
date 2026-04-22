import { useEffect, useState } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8001"

export default function SidePanel() {
  const [shipments, setShipments] = useState([])
  const [selected, setSelected] = useState(null)
  const [explanation, setExplanation] = useState("")

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const res = await axios.get(`${API}/shipments`)
      setShipments(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  const handleExplain = async (shipment) => {
    setSelected(shipment)
    setExplanation("Analyzing...")

    try {
      const res = await axios.post(`${API}/explain`, shipment)
      setExplanation(res.data.explanation)
    } catch (e) {
      setExplanation("Failed to fetch explanation.")
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: "20px" }}>🧠 AI Copilot</h2>

      {shipments.map((s, i) => (
        <div key={i} style={{
          padding: "10px",
          marginBottom: "10px",
          borderRadius: "8px",
          background: "rgba(255,255,255,0.05)"
        }}>
          <strong>{s.id}</strong><br />
          DRI: {s.dri}<br />

          <button
            onClick={() => handleExplain(s)}
            style={{
              marginTop: "5px",
              padding: "5px 10px",
              background: "#2563eb",
              border: "none",
              borderRadius: "5px",
              color: "white",
              cursor: "pointer"
            }}
          >
            Explain Risk
          </button>
        </div>
      ))}

      {selected && (
        <div style={{
          marginTop: "20px",
          padding: "15px",
          background: "rgba(37, 99, 235, 0.1)",
          borderRadius: "10px"
        }}>
          <h3>📊 AI Insight</h3>
          <p>{explanation}</p>
        </div>
      )}
    </div>
  )
}