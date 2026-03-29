import React, { useState, useEffect } from 'react';
import { useLoadScript, GoogleMap, HeatmapLayer, DirectionsRenderer, Marker } from '@react-google-maps/api';
import axios from 'axios';
import './index.css';

const libraries = ['visualization'];

const mapContainerStyle = {
  width: '100%',
  height: '100%',
  borderRadius: '12px',
};

const center = { lat: 14.68, lng: 77.60 };

export default function App() {
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: "YOUR_API_KEY", // Replace with real key
    libraries,
  });

  const [heatData, setHeatData] = useState([]);
  const [directions, setDirections] = useState(null);
  const [vehiclePos, setVehiclePos] = useState({ lat: 14.68, lng: 77.60 });
  const [riskLevel, setRiskLevel] = useState("High");
  const [carActive, setCarActive] = useState(true);

  // STEP 7 / 12: Fetch Heatmap Data and Automatic Updates
  const fetchHeatMap = () => {
    if (!window.google) return;
    axios.get("http://127.0.0.1:8000/heatmap")
      .then(res => {
        const pts = res.data.map(pt => ({
          location: new window.google.maps.LatLng(pt.Lat, pt.Lng),
          weight: pt.weight || pt.risk || 1
        }));
        setHeatData(pts);
      })
      .catch(err => console.error("Could not fetch heatmap:", err));
  };

  // Run heatmap poll
  useEffect(() => {
    if (isLoaded) {
      fetchHeatMap();
      const intervalId = setInterval(fetchHeatMap, 5000);
      return () => clearInterval(intervalId);
    }
  }, [isLoaded]);

  // STEP 8: Directions Route
  useEffect(() => {
    if (isLoaded) {
      const directionsService = new window.google.maps.DirectionsService();
      directionsService.route({
        origin: { lat: 14.68, lng: 77.60 },
        destination: { lat: 14.72, lng: 77.62 },
        travelMode: 'DRIVING'
      }, (result, status) => {
        if (status === 'OK') {
          setDirections(result);
        }
      });
    }
  }, [isLoaded]);

  // STEP 9: Moving Vehicle
  useEffect(() => {
    if (!carActive) return;
    const i = setInterval(() => {
      setVehiclePos(prev => ({
        lat: prev.lat + (Math.random() * 0.001 - 0.0002),
        lng: prev.lng + (Math.random() * 0.001 - 0.0002)
      }));
    }, 2000);
    return () => clearInterval(i);
  }, [carActive]);

  if (loadError) return <div className="loading">Error loading Google Maps. Set a valid API Key.</div>;
  if (!isLoaded) return <div className="loading">Loading AI Patrol Map...</div>;

  return (
    <div className="dashboard-container">
      <header className="header">
        <h2>🚓 Smart Patrol Dashboard <span className="badge">AI Powered</span></h2>
      </header>
      
      <div className="content">
        <div className="map-wrapper">
          <GoogleMap
            mapContainerStyle={mapContainerStyle}
            zoom={13}
            center={center}
            options={{ streetViewControl: false, mapTypeControl: false, styles: darkMapStyles }}
          >
            {heatData.length > 0 && <HeatmapLayer data={heatData} options={{radius: 30}} />}
            {directions && <DirectionsRenderer directions={directions} options={{
                polylineOptions: { strokeColor: "#0ea5e9", strokeWeight: 5 }
            }} />}
            <Marker position={vehiclePos} label="🚨" />
          </GoogleMap>
        </div>
        
        <aside className="sidebar">
          <h3>📊 System Info</h3>
          
          <div className="stat-card risk-card">
            <h4>Risk Level</h4>
            <div className="status-indicator">
              <span className="dot red"></span>
              <p className="risk-status">{riskLevel}</p>
            </div>
          </div>
          
          <div className="stat-card">
            <h4>Vehicle Status</h4>
            <div className="status-indicator">
              <span className={`dot ${carActive ? "green" : "yellow"}`}></span>
              <p>{carActive ? "Active on Route" : "Standby"}</p>
            </div>
            <p className="coords-small">Lat: {vehiclePos.lat.toFixed(4)} <br/>Lng: {vehiclePos.lng.toFixed(4)}</p>
          </div>

          <div className="app-buttons">
            <button onClick={fetchHeatMap} className="btn primary">Update Data (Sync)</button>
            <button onClick={() => setCarActive(!carActive)} className="btn toggle">
              {carActive ? "Pause Vehicle" : "Start Vehicle"}
            </button>
            <button onClick={() => alert("Route re-generated via AI Engine")} className="btn secondary">Generate Route</button>
          </div>
        </aside>
      </div>
    </div>
  );
}

// Optional Dark Mode for Map
const darkMapStyles = [
  { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#38414e" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212a37" }] },
  { featureType: "road", elementType: "labels.text.fill", stylers: [{ color: "#9ca5b3" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#17263c" }] },
];
