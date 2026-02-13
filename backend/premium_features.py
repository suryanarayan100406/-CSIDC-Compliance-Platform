"""
Premium Features Module — National-Level Hackathon Enhancements
3D Map, Heatmap, Predictive Analytics, District Analytics, Data Query, Premium Theme
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta


# ==============================
# Control Room Dark Theme CSS
# ==============================
PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ===== GLOBAL APP ===== */
.stApp {
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: #0a0e1a !important;
    color: #f1f5f9;
}
.stApp > header { background: transparent !important; }
.main .block-container { padding: 1.5rem 2rem 3rem 2rem; max-width: 1400px; }

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080c18 0%, #0d1225 40%, #111827 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stRadio > div > label {
    background: #1a1f35;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 14px !important;
    margin-bottom: 4px;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: #222841;
    border-color: #3b82f6;
}

/* ===== METRIC CARDS ===== */
div[data-testid="stMetric"] {
    background: #1a1f35;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 0 20px rgba(59,130,246,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(59,130,246,0.18);
    border-color: rgba(59,130,246,0.3);
}
div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-size: 28px !important;
    font-weight: 800 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(59,130,246,0.5) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: #1a1f35 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 20px rgba(59,130,246,0.15) !important;
}

/* ===== INPUTS ===== */
.stTextArea textarea, .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    background: #1a1f35 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}
.stTextArea textarea:focus, .stTextInput input:focus, .stNumberInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 20px rgba(59,130,246,0.15) !important;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1f35;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 8px 16px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(59,130,246,0.15) !important;
    color: #3b82f6 !important;
}

/* ===== DATAFRAMES ===== */
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

/* ===== DOWNLOAD BUTTON ===== */
.stDownloadButton > button {
    background: #1a1f35 !important;
    border: 1px solid #8b5cf6 !important;
    color: #8b5cf6 !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: rgba(139,92,246,0.1) !important;
}

/* ===== DIVIDERS ===== */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 24px 0 !important; }

/* ===== CONTROL ROOM HEADER ===== */
.cr-header {
    background: linear-gradient(135deg, #0a0e1a, #111827, #1a1f35);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
}
.cr-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #06b6d4, #8b5cf6, #3b82f6);
    background-size: 300% 100%;
    animation: scanline 4s linear infinite;
}
@keyframes scanline {
    0% { background-position: 0% 0%; }
    100% { background-position: 300% 0%; }
}
.cr-header h1 {
    font-size: 26px;
    font-weight: 800;
    margin: 0;
    color: #f1f5f9;
    letter-spacing: -0.5px;
}
.cr-header .subtitle {
    color: #64748b;
    margin: 6px 0 0 0;
    font-size: 13px;
}
.cr-header .badge {
    display: inline-block;
    background: rgba(34,197,94,0.15);
    color: #22c55e;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 8px;
    letter-spacing: 0.5px;
}

/* ===== GLASS CARD ===== */
.glass-card {
    background: #1a1f35;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 22px;
    margin: 10px 0;
    transition: transform 0.2s, box-shadow 0.2s;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0,0,0,0.3);
}

/* ===== PULSE ===== */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
.pulse { animation: pulse 2s ease-in-out infinite; }

/* ===== LIVE DOT ===== */
.live-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s ease-in-out infinite;
    box-shadow: 0 0 8px #22c55e;
}

</style>
"""


def inject_premium_theme():
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


def render_premium_header(title, subtitle="", live=True):
    live_html = '<span class="live-dot"></span>LIVE' if live else ''
    st.markdown(f"""
    <div class="cr-header">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
        <span class="badge">{live_html}</span>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# Plotly Risk Gauge
# ==============================
def render_plotly_gauge(score, title="Compliance Risk Score"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": title, "font": {"size": 16, "color": "white"}},
        number={"font": {"size": 48, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white", "tickfont": {"color": "white"}},
            "bar": {"color": "#3b82f6"},
            "bgcolor": "#1a1a2e",
            "steps": [
                {"range": [0, 50], "color": "#7f1d1d"},
                {"range": [50, 80], "color": "#713f12"},
                {"range": [80, 100], "color": "#14532d"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        height=280,
        margin=dict(t=40, b=20, l=30, r=30),
    )
    st.plotly_chart(fig, use_container_width=True)


# ==============================
# 3D Map with PyDeck (Full Satellite + Multi-Layer)
# ==============================
def render_3d_map(plots_data):
    if len(plots_data) == 0:
        st.info("No plot data available. Generate demo data first.")
        return

    df = pd.DataFrame(plots_data)
    if "Lat" not in df.columns or "Lon" not in df.columns:
        st.warning("Plot data missing coordinates.")
        return

    # Compute visualization columns
    df["elevation"] = df.get("Risk Score", pd.Series([50]*len(df))).apply(lambda x: (100 - x) * 30)
    df["scatter_radius"] = df.get("Encroached Area", pd.Series([0]*len(df))).apply(lambda x: max(80, min(x * 2, 600)))
    df["color_r"] = df.get("Risk Score", pd.Series([50]*len(df))).apply(lambda x: 239 if x < 50 else (245 if x < 80 else 34))
    df["color_g"] = df.get("Risk Score", pd.Series([50]*len(df))).apply(lambda x: 68 if x < 50 else (158 if x < 80 else 197))
    df["color_b"] = df.get("Risk Score", pd.Series([50]*len(df))).apply(lambda x: 68 if x < 50 else (11 if x < 80 else 94))
    df["label"] = df.apply(lambda r: f"{r.get('Plot ID','')} [{r.get('Risk Score','?')}]", axis=1)

    # Satellite tile provider (open — no API key needed)
    SATELLITE_STYLE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

    # --- LAYERS ---
    # 3D Column Layer
    column_layer = pdk.Layer(
        "ColumnLayer", data=df,
        get_position=["Lon", "Lat"], get_elevation="elevation",
        elevation_scale=1, radius=200,
        get_fill_color=["color_r", "color_g", "color_b", 200],
        pickable=True, auto_highlight=True,
    )

    # Scatter Plot Layer (sized by encroachment)
    scatter_layer = pdk.Layer(
        "ScatterplotLayer", data=df,
        get_position=["Lon", "Lat"],
        get_radius="scatter_radius",
        get_fill_color=["color_r", "color_g", "color_b", 180],
        pickable=True, stroked=True,
        get_line_color=[255, 255, 255, 100],
        line_width_min_pixels=1,
    )

    # Heatmap Layer (only encroached/risky plots)
    heat_data = df[df["Encroached Area"] > 0] if "Encroached Area" in df.columns and len(df[df["Encroached Area"] > 0]) > 0 else df
    heatmap_layer = pdk.Layer(
        "HeatmapLayer", data=heat_data,
        get_position=["Lon", "Lat"], get_weight="elevation",
        radiusPixels=60, intensity=1, threshold=0.3, opacity=0.6,
    )

    # Text Label Layer
    text_layer = pdk.Layer(
        "TextLayer", data=df,
        get_position=["Lon", "Lat"],
        get_text="label", get_size=14,
        get_color=[255, 255, 255, 220],
        get_angle=0, get_text_anchor="'middle'",
        get_alignment_baseline="'top'",
        pickable=False,
    )

    # Arc Layer — connect high-risk plots to each other
    risky = df[df.get("Risk Score", pd.Series([100]*len(df))) < 60]
    arc_data = []
    risky_list = risky.to_dict("records")
    for i in range(len(risky_list)):
        for j in range(i + 1, min(i + 3, len(risky_list))):
            arc_data.append({
                "sourceLat": risky_list[i]["Lat"],
                "sourceLon": risky_list[i]["Lon"],
                "targetLat": risky_list[j]["Lat"],
                "targetLon": risky_list[j]["Lon"],
            })
    arc_df = pd.DataFrame(arc_data) if arc_data else pd.DataFrame(columns=["sourceLat","sourceLon","targetLat","targetLon"])

    arc_layer = pdk.Layer(
        "ArcLayer", data=arc_df,
        get_source_position=["sourceLon", "sourceLat"],
        get_target_position=["targetLon", "targetLat"],
        get_source_color=[239, 68, 68, 160],
        get_target_color=[245, 158, 11, 160],
        get_width=2,
    )

    # --- VIEW STATES ---
    view_3d = pdk.ViewState(
        latitude=df["Lat"].mean(), longitude=df["Lon"].mean(),
        zoom=12, pitch=60, bearing=-30,
    )
    view_top = pdk.ViewState(
        latitude=df["Lat"].mean(), longitude=df["Lon"].mean(),
        zoom=12, pitch=0, bearing=0,
    )

    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛰 3D Satellite View", "🏗 3D Risk Columns", "🔥 Violation Heatmap",
        "📍 Scatter Plot", "🌐 Combined Intelligence"
    ])

    # Custom MapLibre style with ESRI satellite raster tiles (same as Folium map)
    # Encoded as data URI to bypass pydeck's mapbox provider requirement for dict styles
    import json, base64
    _style_dict = {
        "version": 8,
        "sources": {
            "esri-satellite": {
                "type": "raster",
                "tiles": [
                    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                ],
                "tileSize": 256,
            }
        },
        "layers": [{
            "id": "esri-satellite-layer",
            "type": "raster",
            "source": "esri-satellite",
            "minzoom": 0,
            "maxzoom": 19,
        }],
    }
    SATELLITE_STYLE = "data:application/json;base64," + base64.b64encode(json.dumps(_style_dict).encode()).decode()

    with tab1:
        st.pydeck_chart(pdk.Deck(
            layers=[scatter_layer, text_layer, arc_layer],
            initial_view_state=view_3d,
            map_style=SATELLITE_STYLE,
            tooltip={"text": "{Plot ID}\nRisk: {Risk Score}\nEncroachment: {Encroached Area} m²\nStatus: {Status}"},
        ))
        st.caption("🛰 Real satellite imagery with risk-colored markers and arc connections between high-risk plots")

    with tab2:
        st.pydeck_chart(pdk.Deck(
            layers=[column_layer, text_layer],
            initial_view_state=view_3d,
            map_style=SATELLITE_STYLE,
            tooltip={"text": "{Plot ID}\nRisk Score: {Risk Score}\nStatus: {Status}"},
        ))
        st.caption("📊 Column height = Inverse risk score (taller = higher violation risk)")

    with tab3:
        st.pydeck_chart(pdk.Deck(
            layers=[heatmap_layer],
            initial_view_state=pdk.ViewState(
                latitude=df["Lat"].mean(), longitude=df["Lon"].mean(),
                zoom=11, pitch=30,
            ),
            map_style=SATELLITE_STYLE,
        ))
        st.caption("🔥 Heatmap showing concentration of high-risk / encroached plots")

    with tab4:
        st.pydeck_chart(pdk.Deck(
            layers=[scatter_layer, text_layer],
            initial_view_state=view_top,
            map_style=SATELLITE_STYLE,
            tooltip={"text": "{Plot ID}\nRisk: {Risk Score}\nEncroachment: {Encroached Area} m²"},
        ))
        st.caption("📍 Scatter plot — marker size = encroachment area, color = risk level")

    with tab5:
        st.pydeck_chart(pdk.Deck(
            layers=[column_layer, scatter_layer, heatmap_layer, arc_layer, text_layer],
            initial_view_state=view_3d,
            map_style=SATELLITE_STYLE,
            tooltip={"text": "{Plot ID}\nRisk: {Risk Score}"},
        ))
        st.caption("🌐 Full intelligence overlay — columns + scatter + heatmap + risk arcs")

    # --- STYLED SUMMARY STATS ---
    st.markdown("---")

    high_risk = len(df[df.get("Risk Score", pd.Series([100]*len(df))) < 50])
    moderate = len(df[(df.get("Risk Score", pd.Series([100]*len(df))) >= 50) & (df.get("Risk Score", pd.Series([100]*len(df))) < 80)])
    low_risk = len(df[df.get("Risk Score", pd.Series([100]*len(df))) >= 80])
    total_enc = df["Encroached Area"].sum() if "Encroached Area" in df.columns else 0

    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 8px 0;">
        <div style="
            background: linear-gradient(135deg, #1a1f35, #0f1420);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-left: 4px solid #ef4444;
            border-radius: 14px;
            padding: 20px;
            text-align: center;
        ">
            <p style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; margin: 0 0 8px 0; text-transform: uppercase;">HIGH RISK</p>
            <p style="color: #ef4444; font-size: 32px; font-weight: 800; margin: 0; font-family: 'JetBrains Mono', monospace;">{high_risk}</p>
        </div>
        <div style="
            background: linear-gradient(135deg, #1a1f35, #0f1420);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-left: 4px solid #f59e0b;
            border-radius: 14px;
            padding: 20px;
            text-align: center;
        ">
            <p style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; margin: 0 0 8px 0; text-transform: uppercase;">MODERATE</p>
            <p style="color: #f59e0b; font-size: 32px; font-weight: 800; margin: 0; font-family: 'JetBrains Mono', monospace;">{moderate}</p>
        </div>
        <div style="
            background: linear-gradient(135deg, #1a1f35, #0f1420);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-left: 4px solid #22c55e;
            border-radius: 14px;
            padding: 20px;
            text-align: center;
        ">
            <p style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; margin: 0 0 8px 0; text-transform: uppercase;">LOW RISK</p>
            <p style="color: #22c55e; font-size: 32px; font-weight: 800; margin: 0; font-family: 'JetBrains Mono', monospace;">{low_risk}</p>
        </div>
        <div style="
            background: linear-gradient(135deg, #1a1f35, #0f1420);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-left: 4px solid #3b82f6;
            border-radius: 14px;
            padding: 20px;
            text-align: center;
        ">
            <p style="color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; margin: 0 0 8px 0; text-transform: uppercase;">TOTAL ENCROACHMENT</p>
            <p style="color: #3b82f6; font-size: 32px; font-weight: 800; margin: 0; font-family: 'JetBrains Mono', monospace;">{total_enc:,.0f}<span style="font-size: 14px; color: #64748b;"> m²</span></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- LEGEND ---
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1f35, #0f1420);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px 24px;
        margin-top: 16px;
    ">
        <p style="color: #94a3b8; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; margin: 0 0 12px 0;">MAP LEGEND</p>
        <div style="display: flex; gap: 28px; align-items: center; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 14px; height: 14px; background: #ef4444; border-radius: 50%;"></div>
                <span style="color: #e2e8f0; font-size: 12px;">High Risk (Score &lt; 50)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 14px; height: 14px; background: #f59e0b; border-radius: 50%;"></div>
                <span style="color: #e2e8f0; font-size: 12px;">Moderate (50-79)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 14px; height: 14px; background: #22c55e; border-radius: 50%;"></div>
                <span style="color: #e2e8f0; font-size: 12px;">Low Risk (80+)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 30px; height: 3px; background: linear-gradient(90deg, #ef4444, #f59e0b); border-radius: 2px;"></div>
                <span style="color: #e2e8f0; font-size: 12px;">Risk Connection Arc</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 14px; height: 14px; background: rgba(239,68,68,0.5); border-radius: 50%; box-shadow: 0 0 8px rgba(239,68,68,0.4);"></div>
                <span style="color: #e2e8f0; font-size: 12px;">Heatmap Hotspot</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# District-Wise Analytics
# ==============================
DISTRICTS = ["Raipur", "Bilaspur", "Durg", "Korba", "Rajnandgaon", "Jagdalpur", "Raigarh", "Ambikapur"]

def assign_districts(plots_data):
    for plot in plots_data:
        if "District" not in plot:
            plot["District"] = random.choice(DISTRICTS)
    return plots_data


def render_district_analytics(plots_data):
    if len(plots_data) == 0:
        st.info("No data available.")
        return

    plots_data = assign_districts(plots_data)
    df = pd.DataFrame(plots_data)

    # District summary
    district_summary = df.groupby("District").agg(
        Plots=("Plot ID", "count"),
        Avg_Risk=("Risk Score", "mean") if "Risk Score" in df.columns else ("Plot ID", "count"),
        Total_Encroachment=("Encroached Area", "sum"),
        Revenue_Risk=("Revenue Recovery", "sum"),
    ).reset_index()

    if "Risk Score" in df.columns:
        district_summary["Avg_Risk"] = df.groupby("District")["Risk Score"].mean().values
        district_summary["Avg_Risk"] = district_summary["Avg_Risk"].round(1)

    # Plotly bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=district_summary["District"],
        y=district_summary["Total_Encroachment"],
        name="Encroachment (m²)",
        marker_color="#ef4444",
    ))
    fig.add_trace(go.Bar(
        x=district_summary["District"],
        y=district_summary["Revenue_Risk"],
        name="Revenue Risk (₹)",
        marker_color="#f59e0b",
        yaxis="y2",
    ))
    fig.update_layout(
        title="District-Wise Violation & Revenue Risk",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        yaxis=dict(title="Encroachment (m²)", gridcolor="rgba(255,255,255,0.1)"),
        yaxis2=dict(title="Revenue Risk (₹)", overlaying="y", side="right", gridcolor="rgba(255,255,255,0.1)"),
        barmode="group",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(district_summary, use_container_width=True, hide_index=True)


# ==============================
# Predictive Analytics
# ==============================
def render_predictive_analytics(plots_data):
    if len(plots_data) < 3:
        st.info("Need at least 3 plots to generate predictions. Add more data.")
        return

    df = pd.DataFrame(plots_data)

    # Simulate historical trend (last 12 months)
    months = pd.date_range(end=datetime.now(), periods=12, freq="M")
    np.random.seed(42)
    base_violations = max(3, len(df[df.get("Encroached Area", pd.Series([0]*len(df))) > 0]))

    historical = []
    for i, m in enumerate(months):
        v = max(0, base_violations + np.random.randint(-2, 4) + i // 3)
        compliance = max(40, 95 - v * 3 + np.random.randint(-5, 5))
        revenue_risk = v * random.uniform(20000, 80000)
        historical.append({
            "Month": m.strftime("%b %Y"),
            "Violations": v,
            "Compliance %": compliance,
            "Revenue Risk": round(revenue_risk, 0),
        })

    hist_df = pd.DataFrame(historical)

    # Extrapolate 3 months
    last_v = hist_df["Violations"].iloc[-3:].mean()
    last_c = hist_df["Compliance %"].iloc[-3:].mean()
    trend_v = (hist_df["Violations"].iloc[-1] - hist_df["Violations"].iloc[-4]) / 3

    future_months = pd.date_range(start=datetime.now() + timedelta(days=30), periods=3, freq="M")
    for i, m in enumerate(future_months):
        pred_v = max(0, int(last_v + trend_v * (i + 1)))
        pred_c = max(30, last_c - trend_v * 2 * (i + 1))
        historical.append({
            "Month": m.strftime("%b %Y"),
            "Violations": pred_v,
            "Compliance %": round(pred_c, 1),
            "Revenue Risk": round(pred_v * 50000, 0),
        })

    full_df = pd.DataFrame(historical)

    # Plotly dual-axis chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=full_df["Month"][:12], y=full_df["Violations"][:12],
        name="Actual Violations", mode="lines+markers",
        line=dict(color="#ef4444", width=3),
        marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=full_df["Month"][11:], y=full_df["Violations"][11:],
        name="Predicted Violations", mode="lines+markers",
        line=dict(color="#ef4444", width=3, dash="dash"),
        marker=dict(size=8, symbol="diamond"),
    ))
    fig.add_trace(go.Scatter(
        x=full_df["Month"][:12], y=full_df["Compliance %"][:12],
        name="Actual Compliance %", mode="lines+markers",
        line=dict(color="#22c55e", width=3), yaxis="y2",
    ))
    fig.add_trace(go.Scatter(
        x=full_df["Month"][11:], y=full_df["Compliance %"][11:],
        name="Predicted Compliance %", mode="lines+markers",
        line=dict(color="#22c55e", width=3, dash="dash"), yaxis="y2",
        marker=dict(symbol="diamond"),
    ))

    # Add prediction zone shade
    fig.add_vrect(x0=full_df["Month"].iloc[11], x1=full_df["Month"].iloc[-1],
                  fillcolor="rgba(139,92,246,0.1)", line_width=0,
                  annotation_text="Forecast Zone", annotation_position="top left",
                  annotation_font_color="#a78bfa")

    fig.update_layout(
        title="📈 12-Month Trend + 3-Month Forecast",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"}, height=420,
        yaxis=dict(title="Violations", gridcolor="rgba(255,255,255,0.1)"),
        yaxis2=dict(title="Compliance %", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Prediction summary
    pred_trend = "📈 Increasing" if trend_v > 0 else "📉 Decreasing" if trend_v < 0 else "➡ Stable"
    st.markdown(f"""
    <div class="glass-card">
        <h4 style="color: #a78bfa; margin: 0 0 10px 0;">🔮 Prediction Summary</h4>
        <p style="color: #ccc;">Violation trend: <b style="color: {'#ef4444' if trend_v > 0 else '#22c55e'}">{pred_trend}</b></p>
        <p style="color: #ccc;">Projected violations (next quarter): <b>{int(last_v + trend_v * 2)}</b></p>
        <p style="color: #ccc;">Projected compliance: <b>{round(last_c - trend_v * 4, 1)}%</b></p>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# Natural Language Data Query
# ==============================
def render_data_query(plots_data):
    if len(plots_data) == 0:
        st.info("No data to query. Generate demo data first.")
        return

    df = pd.DataFrame(plots_data)

    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #60a5fa; margin: 0;">💬 Ask questions about your compliance data</h4>
    </div>
    """, unsafe_allow_html=True)

    query = st.selectbox("Select a query:", [
        "-- Select --",
        "Which plot has the highest encroachment?",
        "What is the total revenue at risk?",
        "How many plots are compliant?",
        "Which district has the most violations?",
        "What is the average risk score?",
        "Show me all critical plots (Risk Score < 50)",
        "What is the highest single penalty amount?",
    ])

    if query != "-- Select --":
        st.markdown("---")
        if query == "Which plot has the highest encroachment?":
            idx = df["Encroached Area"].idxmax()
            plot = df.loc[idx]
            st.success(f"🏗 **{plot['Plot ID']}** has the highest encroachment at **{plot['Encroached Area']:.2f} m²** "
                       f"with a penalty of **₹{plot['Revenue Recovery']:,.2f}**")

        elif query == "What is the total revenue at risk?":
            total = df["Revenue Recovery"].sum() + df["Revenue Loss"].sum()
            st.success(f"💰 Total revenue at risk: **₹{total:,.2f}** "
                       f"(Recovery: ₹{df['Revenue Recovery'].sum():,.2f} + Loss: ₹{df['Revenue Loss'].sum():,.2f})")

        elif query == "How many plots are compliant?":
            comp = len(df[(df["Encroached Area"] == 0) & (df["Unused Area"] == 0)])
            st.success(f"✅ **{comp}** out of **{len(df)}** plots are fully compliant ({comp/len(df)*100:.1f}%)")

        elif query == "Which district has the most violations?":
            plots_data = assign_districts(plots_data)
            df2 = pd.DataFrame(plots_data)
            viol = df2[df2["Encroached Area"] > 0].groupby("District").size()
            if len(viol) > 0:
                worst = viol.idxmax()
                st.success(f"📍 **{worst}** has the most violations with **{viol[worst]}** encroached plots")
            else:
                st.success("✅ No violations found across any district!")

        elif query == "What is the average risk score?":
            if "Risk Score" in df.columns:
                avg = df["Risk Score"].mean()
                st.success(f"📊 Average risk score: **{avg:.1f}/100** — "
                           f"{'Healthy' if avg >= 80 else 'Moderate concern' if avg >= 50 else 'Critical'}")

        elif query == "Show me all critical plots (Risk Score < 50)":
            if "Risk Score" in df.columns:
                critical = df[df["Risk Score"] < 50]
                if len(critical) > 0:
                    st.warning(f"🚨 Found **{len(critical)}** critical plots:")
                    st.dataframe(critical[["Plot ID", "Risk Score", "Encroached Area", "Status"]], hide_index=True)
                else:
                    st.success("✅ No critical plots found!")

        elif query == "What is the highest single penalty amount?":
            idx = df["Revenue Recovery"].idxmax()
            plot = df.loc[idx]
            st.success(f"💸 Highest penalty: **₹{plot['Revenue Recovery']:,.2f}** on plot **{plot['Plot ID']}** "
                       f"(Encroachment: {plot['Encroached Area']:.2f} m²)")
