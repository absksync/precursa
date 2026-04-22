# 🚢 Precursa — AI-Powered Logistics Monitoring System

---

## 📌 What is Precursa?

Precursa is a real-time logistics monitoring platform that tracks ship movements, analyzes disruption risks, and explains those risks using AI.

It combines live vessel data, weather conditions, and intelligent scoring to help understand:

> **Which shipments are at risk — and why**

---

## ⚙️ How It Works

1. **AIS Data (Ships)**
   - Live vessel positions are streamed using AIS API
   - Used to estimate port congestion

2. **Weather Data**
   - Weather API provides wind, rain, and cloud data
   - Converted into a risk score

3. **Risk Calculation (DRI)**
   - Combines multiple factors:
     - Congestion
     - Weather
     - Tariff (simulated)
     - Carrier reliability (simulated)

4. **AI Copilot (Gemini)**
   - Explains why a shipment is risky
   - Converts data into simple insights

5. **Frontend Dashboard**
   - Shows everything on a live map
   - Updates every few seconds

---

## 📊 Key Features

- 🌍 Live ship tracking (AIS)
- 🌦 Weather-based risk analysis
- 📈 Disruption Risk Index (DRI)
- 🧠 AI-powered explanations (Gemini)
- 🖥 Interactive map dashboard

---

## 🧱 Tech Stack

### Backend
- FastAPI
- AIS Stream API
- OpenWeather API
- Google Gemini API

### Frontend
- React (Vite)
- Leaflet (maps)
- Axios

---

## 🌐 API Endpoints

- `GET /shipments` → Shipment data with risk scores  
- `GET /vessels` → Live ship locations  
- `POST /explain` → AI explanation for a shipment  

---

## 🚀 How to Run

### 1. Clone the repo

```bash
git clone https://github.com/absksync/precursa.git
cd precursa
