import { MapContainer, TileLayer, FeatureGroup, GeoJSON } from "react-leaflet";
import { EditControl } from "react-leaflet-draw";
import axios from "axios";
import { useState } from "react";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";

const sendToBackend = async (boundary, setEncroachment, setScore, setIntelligence) => {
  try {
    const builtRes = await axios.post("http://localhost:5000/detect-builtup", {
      boundary
    });

    const encRes = await axios.post("http://localhost:5000/detect-encroachment", {
      boundary
    });

    const scoreRes = await axios.post("http://localhost:5000/compliance-score", {
      total_area_m2: builtRes.data.total_area_m2,
      built_up_area_m2: builtRes.data.built_up_area_m2,
      encroachment: encRes.data.encroachment_detected
    });

    setEncroachment(encRes.data.encroachment_geojson);
    setScore(scoreRes.data.compliance_score);
    setIntelligence({
      severity: scoreRes.data.severity,
      risk_score: scoreRes.data.risk_score,
      action: scoreRes.data.recommended_action,
      urgency: scoreRes.data.urgency,
      built_percentage: scoreRes.data.built_percentage
    });
    console.log(scoreRes.data);
  } catch (error) {
    console.error("Backend error:", error);
  }
};

export default function MapView({ onBoundaryCreated }) {
  const [encroachment, setEncroachment] = useState(null);
  const [score, setScore] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  return (
    <MapContainer center={[21.2514, 81.6296]} zoom={13} style={{ height: "100vh" }}>
      <TileLayer
        attribution="OpenStreetMap"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <FeatureGroup>
        <EditControl
          position="topright"
          draw={{
            rectangle: true,
            polygon: true,
            circle: false,
            marker: false,
          }}
          onCreated={(e) => {
            const geojson = e.layer.toGeoJSON();
            onBoundaryCreated(geojson);
            sendToBackend(geojson.geometry, setEncroachment, setScore, setIntelligence);
          }}
        />
      </FeatureGroup>

      {encroachment && (
        <GeoJSON
          data={encroachment}
          style={{ color: "red", weight: 3 }}
        />
      )}

      {score !== null && (
        <div className="score-box" style={{
          position: "absolute",
          bottom: "20px",
          right: "20px",
          backgroundColor: "white",
          padding: "20px",
          borderRadius: "8px",
          boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
          zIndex: 1000,
          minWidth: "320px",
          maxHeight: "500px",
          overflowY: "auto"
        }}>
          <h2 style={{margin: "0 0 15px 0"}}>📊 Compliance Analysis</h2>
          
          <div style={{marginBottom: "15px", paddingBottom: "15px", borderBottom: "1px solid #eee"}}>
            <h3 style={{margin: "0 0 8px 0", fontSize: "24px"}}>{score}</h3>
            {score > 80 && <p style={{color:"green", margin: 0, fontSize: "16px", fontWeight: "bold"}}>✓ Green Compliant</p>}
            {score <= 80 && score > 50 && <p style={{color:"orange", margin: 0, fontSize: "16px", fontWeight: "bold"}}>⚠ Moderate Risk</p>}
            {score <= 50 && <p style={{color:"red", margin: 0, fontSize: "16px", fontWeight: "bold"}}>✗ Violation</p>}
          </div>

          {intelligence && (
            <>
              <div style={{marginBottom: "15px", paddingBottom: "15px", borderBottom: "1px solid #eee"}}>
                <p style={{margin: "0 0 5px 0", fontSize: "12px", color: "#666"}}>BUILT-UP %</p>
                <p style={{margin: 0, fontSize: "18px", fontWeight: "bold"}}>{intelligence.built_percentage}%</p>
              </div>

              <div style={{marginBottom: "15px", paddingBottom: "15px", borderBottom: "1px solid #eee"}}>
                <p style={{margin: "0 0 5px 0", fontSize: "12px", color: "#666"}}>⚖ SEVERITY LEVEL</p>
                <p style={{margin: 0, fontSize: "14px", fontWeight: "bold"}}>{intelligence.severity}</p>
                <p style={{margin: "5px 0 0 0", fontSize: "12px", color: "#666"}}>Risk Score: {intelligence.risk_score}/4</p>
              </div>

              <div style={{marginBottom: "15px", paddingBottom: "15px", borderBottom: "1px solid #eee"}}>
                <p style={{margin: "0 0 5px 0", fontSize: "12px", color: "#666"}}>🧾 RECOMMENDED ACTION</p>
                <p style={{margin: "0 0 5px 0", fontSize: "14px"}}>{intelligence.action}</p>
                <p style={{margin: 0, fontSize: "12px", color: "red", fontWeight: "bold"}}>⏰ {intelligence.urgency}</p>
              </div>
            </>
          )}
        </div>
      )}
    </MapContainer>
  );
}
