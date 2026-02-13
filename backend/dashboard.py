import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from shapely.geometry import shape
from datetime import datetime
from premium_features import (
    inject_premium_theme, render_premium_header, render_plotly_gauge,
    render_3d_map, render_district_analytics, render_predictive_analytics,
    render_data_query,
)

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

BACKEND_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="CSIDC Compliance Intelligence Platform", layout="wide", initial_sidebar_state="expanded")

# ==============================
# Session State Initialization
# ==============================
if "plots_data" not in st.session_state:
    st.session_state.plots_data = []

# Inject premium dark theme
inject_premium_theme()

# Matplotlib dark theme - Professional Control Room Style
plt.rcParams.update({
    'figure.facecolor': '#1a1f35',
    'axes.facecolor': '#1a1f35',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#94a3b8',
    'text.color': '#f1f5f9',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#0f1420',
    'grid.alpha': 0.3,
    'figure.titlesize': 14,
    'axes.labelsize': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
})


# ==============================
# PDF Generator
# ==============================
def generate_pdf(report_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>CSIDC Industrial Compliance Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    table_data = [["Metric", "Value"]]
    for key, value in report_data.items():
        table_data.append([key, str(value)])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


# ==============================
# Compute Risk Score (0-100) locally
# ==============================
def compute_risk_score(enc_area, unused_area, unused_pct):
    score = 100
    if enc_area > 0:
        score -= 40
    if unused_pct > 20:
        score -= 30
    elif unused_pct > 0:
        score -= 10  # minor deviation
    return max(score, 0)


# ==============================
# Alert Panel (Feature 5) - Control Room Style
# ==============================
def render_alert_panel():
    plots = st.session_state.plots_data
    if len(plots) == 0:
        return

    df = pd.DataFrame(plots)
    critical_violations = len(df[df["Encroached Area"] > 0])
    total_revenue_risk = df["Revenue Recovery"].sum() + df["Revenue Loss"].sum()
    has_encroachment = critical_violations > 0

    # Find highest risk plot
    if "Risk Score" in df.columns:
        highest_risk_idx = df["Risk Score"].idxmin()
        highest_risk_plot = df.loc[highest_risk_idx, "Plot ID"]
        highest_risk_score = df.loc[highest_risk_idx, "Risk Score"]
    else:
        highest_risk_plot = "N/A"
        highest_risk_score = "N/A"

    bg_gradient = "linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%)" if has_encroachment else "linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.1) 100%)"
    border_color = "#ef4444" if has_encroachment else "#22c55e"
    icon = "🚨" if has_encroachment else "✅"

    st.markdown(f"""
    <div style="
        background: {bg_gradient};
        border: 2px solid {border_color};
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 28px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
            <div>
                <p style="
                    color: {border_color};
                    font-size: 11px;
                    margin: 0 0 8px 0;
                    font-weight: 700;
                    letter-spacing: 1.5px;
                    text-transform: uppercase;
                ">{icon} REAL-TIME COMPLIANCE ALERTS</p>
                <p style="
                    color: #f1f5f9;
                    font-size: 32px;
                    font-weight: 800;
                    margin: 0;
                    font-family: 'JetBrains Mono', monospace;
                    letter-spacing: -0.5px;
                ">{critical_violations} <span style="font-size: 18px; color: #94a3b8; font-weight: 600;">Critical Violation{'s' if critical_violations != 1 else ''}</span></p>
            </div>
            <div style="text-align: center; padding: 0 20px;">
                <p style="
                    color: #94a3b8;
                    font-size: 11px;
                    margin: 0 0 6px 0;
                    font-weight: 600;
                    letter-spacing: 1.2px;
                    text-transform: uppercase;
                ">REVENUE AT RISK</p>
                <p style="
                    color: #fbbf24;
                    font-size: 28px;
                    font-weight: 700;
                    margin: 0;
                    font-family: 'JetBrains Mono', monospace;
                ">₹{total_revenue_risk:,.2f}</p>
            </div>
            <div style="text-align: center;">
                <p style="
                    color: #94a3b8;
                    font-size: 11px;
                    margin: 0 0 6px 0;
                    font-weight: 600;
                    letter-spacing: 1.2px;
                    text-transform: uppercase;
                ">HIGHEST RISK PLOT</p>
                <p style="
                    color: #ef4444;
                    font-size: 28px;
                    font-weight: 700;
                    margin: 0;
                    font-family: 'JetBrains Mono', monospace;
                ">{highest_risk_plot}</p>
                <p style="
                    color: #f87171;
                    font-size: 14px;
                    margin: 4px 0 0 0;
                    font-weight: 600;
                ">Risk Score: {highest_risk_score}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# Executive Summary Generator (Feature 6) - Enhanced
# ==============================
def render_executive_summary():
    plots = st.session_state.plots_data
    if len(plots) == 0:
        return

    df = pd.DataFrame(plots)
    total = len(df)
    enc_count = len(df[df["Encroached Area"] > 0])
    unused_count = len(df[df["Unused Area"] > 0])
    compliant_count = total - len(df[(df["Encroached Area"] > 0) | (df["Unused Area"] > 0)])
    compliance_rate = round(compliant_count / total * 100, 1) if total > 0 else 0
    total_recovery = df["Revenue Recovery"].sum()
    total_loss = df["Revenue Loss"].sum()
    total_risk = total_recovery + total_loss

    if compliance_rate >= 80:
        overall_status = "Healthy"
        status_icon = "🟢"
        status_color = "#22c55e"
    elif compliance_rate >= 50:
        overall_status = "Moderate Concern"
        status_icon = "🟡"
        status_color = "#f59e0b"
    else:
        overall_status = "Critical"
        status_icon = "🔴"
        status_color = "#ef4444"

    summary_text = (
        f"Across **{total} monitored industrial plots**, the overall compliance status is "
        f"**{status_icon} {overall_status}** with a compliance rate of **{compliance_rate}%**. "
        f"**{enc_count} plot(s)** show boundary encroachment requiring immediate revenue recovery of "
        f"**₹{total_recovery:,.2f}**, while **{unused_count} plot(s)** are underutilized, resulting in "
        f"lease revenue loss of **₹{total_loss:,.2f}**. Total revenue at risk stands at "
        f"**₹{total_risk:,.2f}**. "
    )

    if enc_count > 0:
        summary_text += (
            f"Immediate enforcement action is recommended for encroached plots to recover "
            f"₹{total_recovery:,.2f} in penalties. "
        )
    if unused_count > 0:
        summary_text += (
            f"Underutilized plots should be reviewed for lease renegotiation or reallocation."
        )

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 14px;
        padding: 24px 28px;
        margin: 20px 0;
        border-left: 4px solid #8b5cf6;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <div style="
                background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                width: 40px;
                height: 40px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            ">🤖</div>
            <div>
                <p style="
                    color: #a78bfa;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 1.5px;
                    margin: 0;
                    text-transform: uppercase;
                ">AI-POWERED EXECUTIVE SUMMARY</p>
                <p style="
                    color: #64748b;
                    font-size: 12px;
                    margin: 2px 0 0 0;
                    font-weight: 500;
                ">Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
        <div style="
            color: #e2e8f0;
            font-size: 14px;
            line-height: 1.8;
            font-weight: 500;
        ">
            {summary_text}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# Demo Data Generator (Feature 4)
# ==============================
def generate_demo_plots(n=20):
    demo_plots = []
    for i in range(n):
        plot_type = random.choice(["compliant", "encroached", "underutilized"])
        if plot_type == "compliant":
            enc = 0
            unused = 0
        elif plot_type == "encroached":
            enc = round(random.uniform(30, 500), 2)
            unused = round(random.uniform(0, 50), 2)
        else:
            enc = 0
            unused = round(random.uniform(100, 800), 2)

        land_rate = random.choice([1500, 2000, 2500, 3000])
        lease_rate = random.choice([100, 150, 200])
        penalty = round(enc * land_rate, 2)
        loss = round(unused * lease_rate, 2)

        total_ref_area = round(random.uniform(2000, 10000), 2)
        unused_pct = round((unused / total_ref_area) * 100, 2) if total_ref_area > 0 else 0
        risk_score = compute_risk_score(enc, unused, unused_pct)

        if enc > 0:
            status = "Encroachment"
        elif unused_pct > 20:
            status = "Underutilized"
        else:
            status = "Compliant"

        demo_plots.append({
            "Plot ID": f"P-{len(st.session_state.plots_data) + i + 1}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Encroached Area": enc,
            "Unused Area": unused,
            "Unused %": unused_pct,
            "Revenue Recovery": penalty,
            "Revenue Loss": loss,
            "Risk Score": risk_score,
            "Status": status,
            "Lat": round(21.25 + random.uniform(-0.05, 0.05), 6),
            "Lon": round(81.63 + random.uniform(-0.05, 0.05), 6),
        })
    return demo_plots


# ==============================
# Sidebar Navigation - Control Room Style
# ==============================
st.sidebar.markdown("""
<div style="text-align: center; padding: 20px 0 10px 0;">
    <div style="
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        width: 60px;
        height: 60px;
        border-radius: 14px;
        margin: 0 auto 12px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    ">📌</div>
    <h2 style="
        color: #f1f5f9;
        font-size: 18px;
        font-weight: 800;
        margin: 0 0 4px 0;
        letter-spacing: -0.3px;
    ">CSIDC</h2>
    <p style="
        color: #64748b;
        font-size: 11px;
        margin: 0;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    ">Compliance Intelligence</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Feature 8: Role-Based Access
role = st.sidebar.selectbox("👤 Select Role", ["Admin", "Inspector"])

if role == "Admin":
    page_options = [
        "📊 Overview Dashboard",
        "🗺 Multi-Plot Monitoring",
        "🌐 3D Risk Map & Heatmap",
        "📈 Analytics & Trends",
        "🔮 Predictive Analytics",
        "🏘 District-Wise Analytics",
        "🔍 Single Plot Comparison",
        "📋 Inspection History",
        "💬 Data Query",
        "🏗 System Architecture",
    ]
else:
    page_options = [
        "🔍 Single Plot Comparison",
    ]

page = st.sidebar.radio("Select Module", page_options)

st.sidebar.markdown("---")

# Feature 4: Demo Data Button in sidebar
if st.sidebar.button("🎲 Generate Demo Dataset (20 Plots)"):
    demo = generate_demo_plots(20)
    st.session_state.plots_data.extend(demo)
    # Force map regeneration
    if "multi_map" in st.session_state:
        del st.session_state.multi_map
    st.sidebar.success(f"✅ {len(demo)} demo plots added!")
    st.rerun()

if st.sidebar.button("🗑 Clear All Data"):
    st.session_state.plots_data = []
    if "multi_map" in st.session_state:
        del st.session_state.multi_map
    st.sidebar.success("✅ All data cleared!")
    st.rerun()

st.sidebar.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 14px;
    margin-top: 20px;
    text-align: center;
">
    <p style="
        color: #64748b;
        font-size: 10px;
        margin: 0 0 4px 0;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    ">PLOTS IN MEMORY</p>
    <p style="
        color: #3b82f6;
        font-size: 24px;
        font-weight: 700;
        margin: 0;
        font-family: 'JetBrains Mono', monospace;
    ">{len(st.session_state.plots_data)}</p>
</div>
""", unsafe_allow_html=True)


# ==============================
# PAGE: Overview Dashboard
# ==============================
if page == "📊 Overview Dashboard":

    render_premium_header("State-Level Compliance Overview", "Real-time monitoring of industrial plot compliance across Chhattisgarh")

    # Feature 5: Alert Panel
    render_alert_panel()

    if len(st.session_state.plots_data) == 0:
        st.info("No plots analyzed yet. Use **Generate Demo Dataset** or run a Single Plot Comparison to add data.")
    else:
        df = pd.DataFrame(st.session_state.plots_data)

        total_plots = len(df)
        violations = len(df[(df["Encroached Area"] > 0) | (df["Unused Area"] > 0)])
        compliant = total_plots - violations
        compliance_rate = round(compliant / total_plots * 100, 2)

        total_leakage = df["Revenue Recovery"].sum() + df["Revenue Loss"].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Plots Monitored", total_plots)
        col2.metric("Violations Detected", violations)
        col3.metric("Compliance Rate (%)", compliance_rate)
        col4.metric("Total Revenue Leakage (₹)", f"{round(total_leakage,2):,}")

        st.markdown("---")

        # Charts
        c1, c2 = st.columns(2)
        with c1:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(
                ["Encroachments", "Underutilized", "Compliant"],
                [
                    len(df[df["Encroached Area"] > 0]),
                    len(df[(df["Unused Area"] > 0) & (df["Encroached Area"] == 0)]),
                    compliant,
                ],
                color=["#ef4444", "#f59e0b", "#22c55e"],
                edgecolor='#0a0e1a',
                linewidth=2
            )
            ax.set_title("Plot Distribution", fontweight='bold', pad=15)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)

        with c2:
            if "Risk Score" in df.columns:
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                risk_bins = [
                    len(df[df["Risk Score"] >= 80]),
                    len(df[(df["Risk Score"] >= 50) & (df["Risk Score"] < 80)]),
                    len(df[df["Risk Score"] < 50]),
                ]
                wedges, texts, autotexts = ax2.pie(
                    risk_bins,
                    labels=["Low Risk (80+)", "Moderate (50-79)", "High Risk (<50)"],
                    colors=["#22c55e", "#f59e0b", "#ef4444"],
                    autopct="%1.1f%%",
                    startangle=90,
                    wedgeprops=dict(edgecolor='#0a0e1a', linewidth=2)
                )
                for text in texts:
                    text.set_color('#94a3b8')
                    text.set_fontsize(10)
                for autotext in autotexts:
                    autotext.set_color('#f1f5f9')
                    autotext.set_fontweight('bold')
                ax2.set_title("Risk Score Distribution", fontweight='bold', pad=15)
                st.pyplot(fig2)

        st.markdown("---")

        # Feature 6: Executive Summary
        render_executive_summary()


# ==============================
# PAGE: Multi-Plot Monitoring Map
# ==============================
elif page == "🗺 Multi-Plot Monitoring":

    render_premium_header("Multi-Plot Monitoring Map", "Satellite view of all monitored industrial plots")

    if "multi_map" not in st.session_state:

        multi_map = folium.Map(
            location=[21.25, 81.63],
            zoom_start=12,
            tiles="Esri.WorldImagery"
        )

        if len(st.session_state.plots_data) == 0:
            st.info("No plots available on the map. Run Single Plot Comparison or generate demo data.")
        else:
            for i, plot in enumerate(st.session_state.plots_data):
                lat = plot.get("Lat", 21.25 + random.uniform(-0.03, 0.03))
                lon = plot.get("Lon", 81.63 + random.uniform(-0.03, 0.03))

                if plot["Encroached Area"] > 0:
                    color = "red"
                    status = "Encroachment"
                elif plot["Unused Area"] > 0:
                    color = "orange"
                    status = "Underutilized"
                else:
                    color = "green"
                    status = "Compliant"

                risk_label = plot.get("Risk Score", "N/A")

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=f"<b>{plot['Plot ID']}</b><br>Status: {status}<br>Risk: {risk_label}/100"
                ).add_to(multi_map)

        st.session_state.multi_map = multi_map

    st_folium(st.session_state.multi_map, width=1000, height=600)

    # Legend - Styled
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px 24px;
        margin-top: 20px;
        display: inline-block;
    ">
        <p style="
            color: #94a3b8;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            margin: 0 0 12px 0;
        ">MAP LEGEND</p>
        <div style="display: flex; gap: 24px; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #ef4444; border-radius: 50%;"></div>
                <span style="color: #e2e8f0; font-size: 13px; font-weight: 500;">Encroachment</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #f59e0b; border-radius: 50%;"></div>
                <span style="color: #e2e8f0; font-size: 13px; font-weight: 500;">Underutilized</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #22c55e; border-radius: 50%;"></div>
                <span style="color: #e2e8f0; font-size: 13px; font-weight: 500;">Compliant</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# PAGE: Analytics & Trends
# ==============================
elif page == "📈 Analytics & Trends":

    render_premium_header("Violation Analytics & Trends", "Compliance breakdown, risk distribution, and revenue impact analysis")

    # Feature 5: Alert Panel
    render_alert_panel()

    if len(st.session_state.plots_data) == 0:
        st.info("No analytics available yet. Run comparisons or generate demo data to populate.")
    else:
        df = pd.DataFrame(st.session_state.plots_data)

        c1, c2 = st.columns(2)

        with c1:
            fig, ax = plt.subplots(figsize=(6, 4.5))
            enc_count = len(df[df["Encroached Area"] > 0])
            unused_count = len(df[(df["Unused Area"] > 0) & (df["Encroached Area"] == 0)])
            comp_count = len(df) - enc_count - unused_count
            ax.bar(
                ["Compliant", "Encroached", "Underutilized"],
                [comp_count, enc_count, unused_count],
                color=["#22c55e", "#ef4444", "#f59e0b"],
                edgecolor='#0a0e1a',
                linewidth=2
            )
            ax.set_title("Compliance Breakdown", fontweight='bold', pad=15)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)

        with c2:
            if "Risk Score" in df.columns:
                fig2, ax2 = plt.subplots(figsize=(6, 4.5))
                ax2.hist(df["Risk Score"], bins=10, color="#6366f1", edgecolor="#0a0e1a", linewidth=1.5)
                ax2.set_xlabel("Risk Score", fontweight='bold')
                ax2.set_ylabel("# Plots", fontweight='bold')
                ax2.set_title("Risk Score Distribution", fontweight='bold', pad=15)
                ax2.spines['top'].set_visible(False)
                ax2.spines['right'].set_visible(False)
                ax2.grid(axis='y', alpha=0.3)
                st.pyplot(fig2)

        st.markdown("---")

        # Revenue analysis
        st.markdown("""
        <p style="
            color: #94a3b8;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 24px 0 16px 0;
        ">💰 REVENUE IMPACT ANALYSIS</p>
        """, unsafe_allow_html=True)
        
        rev_c1, rev_c2, rev_c3 = st.columns(3)
        rev_c1.metric("Total Recovery (₹)", f"{df['Revenue Recovery'].sum():,.2f}")
        rev_c2.metric("Total Loss (₹)", f"{df['Revenue Loss'].sum():,.2f}")
        rev_c3.metric("Combined Risk (₹)", f"{df['Revenue Recovery'].sum() + df['Revenue Loss'].sum():,.2f}")

        # Feature 6: Executive Summary
        st.markdown("---")
        render_executive_summary()


# ==============================
# PAGE: Single Plot Comparison
# ==============================
elif page == "🔍 Single Plot Comparison":

    render_premium_header("Single Plot Compliance Comparison", "Compare reference vs current boundary with GeoJSON input", live=False)

    reference_input = st.text_area("Paste Reference GeoJSON", height=150)
    current_input = st.text_area("Paste Current GeoJSON", height=150)

    col_a, col_b = st.columns(2)
    with col_a:
        land_rate = st.number_input("Land Rate (₹ per m²)", value=2000)
    with col_b:
        lease_rate = st.number_input("Lease Rate (₹ per m²)", value=150)

    if st.button("🚀 Run Comparison"):

        reference_boundary = json.loads(reference_input)
        current_boundary = json.loads(current_input)

        compare_response = requests.post(
            f"{BACKEND_URL}/compare-boundaries",
            json={
                "reference": reference_boundary,
                "current": current_boundary,
                "tolerance_m2": 25
            }
        )

        compare_data = compare_response.json()

        enc = compare_data["encroachment_area"]
        unused = compare_data["unused_area"]
        unused_pct = compare_data.get("unused_percentage", 0)
        tolerance_applied = compare_data.get("tolerance_applied", False)

        penalty = enc * land_rate
        loss = unused * lease_rate

        # Feature 1: Tolerance Threshold Display
        if tolerance_applied:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.1) 100%);
                border: 1px solid #22c55e;
                border-left: 4px solid #22c55e;
                border-radius: 12px;
                padding: 16px 20px;
                margin: 20px 0;
            ">
                <p style="
                    color: #22c55e;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 1.2px;
                    text-transform: uppercase;
                    margin: 0 0 8px 0;
                ">⚖ TOLERANCE APPLIED</p>
                <p style="
                    color: #e2e8f0;
                    font-size: 14px;
                    margin: 0;
                    line-height: 1.6;
                ">Tolerance (25 m²) applied — Minor deviations below 25 m² treated as zero. Plot classified as compliant within tolerance.</p>
            </div>
            """, unsafe_allow_html=True)

        # Metrics
        m1, m2 = st.columns(2)
        m1.metric("Encroached Area (m²)", round(enc, 2))
        m2.metric("Unused Area (m²)", round(unused, 2))

        m3, m4 = st.columns(2)
        m3.metric("Revenue Recovery (₹)", f"{round(penalty, 2):,}")
        m4.metric("Revenue Loss (₹)", f"{round(loss, 2):,}")

        # Feature 2: Risk Score Gauge (Plotly)
        risk_score = compute_risk_score(enc, unused, unused_pct)
        render_plotly_gauge(risk_score)

        # Determine status
        if enc > 0:
            status = "Encroachment"
        elif unused_pct > 20:
            status = "Underutilized"
        else:
            status = "Compliant"

        # Store the result centrally
        plot_record = {
            "Plot ID": f"P-{len(st.session_state.plots_data)+1}",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Encroached Area": enc,
            "Unused Area": unused,
            "Unused %": unused_pct,
            "Revenue Recovery": penalty,
            "Revenue Loss": loss,
            "Risk Score": risk_score,
            "Status": status,
            "Lat": round(21.25 + random.uniform(-0.05, 0.05), 6),
            "Lon": round(81.63 + random.uniform(-0.05, 0.05), 6),
        }

        st.session_state.plots_data.append(plot_record)

        # Force map regeneration
        if "multi_map" in st.session_state:
            del st.session_state.multi_map

        # PDF Report
        report_data = {
            "Plot ID": plot_record["Plot ID"],
            "Encroached Area (m²)": round(enc, 2),
            "Unused Area (m²)": round(unused, 2),
            "Unused %": unused_pct,
            "Risk Score": risk_score,
            "Revenue Recovery (₹)": round(penalty, 2),
            "Revenue Loss (₹)": round(loss, 2),
            "Status": status,
            "Tolerance Applied": "Yes" if tolerance_applied else "No",
        }

        pdf_file = generate_pdf(report_data)

        st.download_button(
            "📄 Download Compliance Report",
            pdf_file,
            "Compliance_Report.pdf",
            "application/pdf"
        )


# ==============================
# PAGE: Inspection History (Feature 3)
# ==============================
elif page == "📋 Inspection History":

    render_premium_header("Inspection History", "Complete log of all plot inspections with timestamps")

    if len(st.session_state.plots_data) == 0:
        st.info("No inspections recorded yet. Run a Single Plot Comparison or generate demo data.")
    else:
        df = pd.DataFrame(st.session_state.plots_data)

        # Display columns
        display_cols = ["Plot ID", "Timestamp", "Encroached Area", "Unused Area", "Risk Score", "Status"]
        available_cols = [c for c in display_cols if c in df.columns]

        st.dataframe(
            df[available_cols],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 16px 24px;
            margin: 20px 0;
            display: inline-block;
        ">
            <p style="
                color: #94a3b8;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1.2px;
                text-transform: uppercase;
                margin: 0 0 6px 0;
            ">TOTAL INSPECTIONS</p>
            <p style="
                color: #3b82f6;
                font-size: 28px;
                font-weight: 700;
                margin: 0;
                font-family: 'JetBrains Mono', monospace;
            ">{len(df)}</p>
        </div>
        """, unsafe_allow_html=True)

        # Export
        csv = df[available_cols].to_csv(index=False)
        st.download_button(
            "📥 Export History as CSV",
            csv,
            "inspection_history.csv",
            "text/csv"
        )


# ==============================
# PAGE: System Architecture (Feature 7)
# ==============================
elif page == "🏗 System Architecture":

    render_premium_header("System Architecture", "Platform component diagram and API endpoint reference", live=False)

    st.markdown("""
    <p style="
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.7;
        margin: 0 0 32px 0;
    ">
    This platform is built on a modular, scalable architecture designed for
    real-time compliance monitoring of industrial land parcels across Chhattisgarh.
    </p>
    """, unsafe_allow_html=True)

    # Architecture components using columns
    arch1, arch2 = st.columns(2)

    with arch1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 24px;
            margin: 0 0 16px 0;
            border-left: 4px solid #3b82f6;
        ">
            <h4 style="
                color: #60a5fa;
                margin: 0 0 16px 0;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: -0.2px;
            ">🖥 Frontend — Streamlit</h4>
            <ul style="color: #cbd5e1; font-size: 13px; line-height: 1.8; margin: 0; padding-left: 20px;">
                <li>Interactive dashboards & real-time analytics</li>
                <li>Role-based access control (Inspector/Admin)</li>
                <li>PDF report generation & CSV export</li>
                <li>Folium satellite map integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 24px;
            margin: 0;
            border-left: 4px solid #22c55e;
        ">
            <h4 style="
                color: #4ade80;
                margin: 0 0 16px 0;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: -0.2px;
            ">🌍 GIS Engine — Shapely + PyProj</h4>
            <ul style="color: #cbd5e1; font-size: 13px; line-height: 1.8; margin: 0; padding-left: 20px;">
                <li>Polygon intersection & difference operations</li>
                <li>UTM projection for accurate area calculation</li>
                <li>Boundary comparison with tolerance thresholds</li>
                <li>Auto-detect UTM zone from GeoJSON coordinates</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with arch2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 24px;
            margin: 0 0 16px 0;
            border-left: 4px solid #f59e0b;
        ">
            <h4 style="
                color: #fbbf24;
                margin: 0 0 16px 0;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: -0.2px;
            ">⚙ Backend — Flask REST API</h4>
            <ul style="color: #cbd5e1; font-size: 13px; line-height: 1.8; margin: 0; padding-left: 20px;">
                <li>RESTful endpoints for all GIS operations</li>
                <li>Compliance scoring engine (0–100)</li>
                <li>Legal risk classification & recommendation</li>
                <li>Tolerance threshold filtering (25 m²)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1f35 0%, #0f1420 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 24px;
            margin: 0;
            border-left: 4px solid #8b5cf6;
        ">
            <h4 style="
                color: #a78bfa;
                margin: 0 0 16px 0;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: -0.2px;
            ">🛰 Satellite Visualization — Folium</h4>
            <ul style="color: #cbd5e1; font-size: 13px; line-height: 1.8; margin: 0; padding-left: 20px;">
                <li>ESRI World Imagery satellite tiles</li>
                <li>Color-coded plot markers (Red/Yellow/Green)</li>
                <li>Interactive popups with compliance details</li>
                <li>Multi-plot overlay for state-wide monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Flow diagram using Streamlit layout
    st.markdown("""
    <p style="
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 32px 0 20px 0;
    ">📐 DATA FLOW DIAGRAM</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background: #0f1420;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 32px;
        text-align: center;
        font-family: monospace;
    ">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap;">
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                padding: 14px 22px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 13px;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            ">📄 GeoJSON Input</div>
            <span style="color: #475569; font-size: 28px; font-weight: bold;">→</span>
            <div style="
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                padding: 14px 22px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 13px;
                box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
            ">⚙ Flask API</div>
            <span style="color: #475569; font-size: 28px; font-weight: bold;">→</span>
            <div style="
                background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
                padding: 14px 22px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 13px;
                box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
            ">🌍 Shapely/PyProj</div>
            <span style="color: #475569; font-size: 28px; font-weight: bold;">→</span>
            <div style="
                background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                padding: 14px 22px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 13px;
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
            ">📊 Compliance Score</div>
            <span style="color: #475569; font-size: 28px; font-weight: bold;">→</span>
            <div style="
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                padding: 14px 22px;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                font-size: 13px;
                box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
            ">🖥 Streamlit Dashboard</div>
        </div>
        <div style="
            margin-top: 24px;
            color: #64748b;
            font-size: 12px;
            line-height: 1.6;
            font-family: 'Inter', sans-serif;
        ">
            GeoJSON → Boundary Comparison → Area Calculation → Risk Scoring → Visualization & Reporting
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API endpoints table
    st.markdown("""
    <p style="
        color: #94a3b8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin: 32px 0 20px 0;
    ">🔌 API ENDPOINTS</p>
    """, unsafe_allow_html=True)
    
    api_df = pd.DataFrame([
        {"Endpoint": "/compare-boundaries", "Method": "POST", "Description": "Compare reference vs current boundary with tolerance"},
        {"Endpoint": "/detect-builtup", "Method": "POST", "Description": "Detect built-up area within a boundary"},
        {"Endpoint": "/detect-encroachment", "Method": "POST", "Description": "Detect encroachment beyond boundary"},
        {"Endpoint": "/compliance-score", "Method": "POST", "Description": "Calculate 0–100 compliance risk score"},
    ])
    st.dataframe(api_df, use_container_width=True, hide_index=True)


# ==============================
# PAGE: 3D Risk Map & Heatmap
# ==============================
elif page == "🌐 3D Risk Map & Heatmap":

    render_premium_header("3D Risk Visualization & Heatmap", "Satellite-grade 3D terrain with risk-scored columns and violation heatmap overlay")
    render_3d_map(st.session_state.plots_data)


# ==============================
# PAGE: Predictive Analytics
# ==============================
elif page == "🔮 Predictive Analytics":

    render_premium_header("Predictive Compliance Analytics", "12-month historical trend analysis with 3-month AI-powered forecasting")
    render_predictive_analytics(st.session_state.plots_data)


# ==============================
# PAGE: District-Wise Analytics
# ==============================
elif page == "🏘 District-Wise Analytics":

    render_premium_header("District-Wise Compliance Analysis", "Comparative violation and revenue analytics across Chhattisgarh districts")
    render_district_analytics(st.session_state.plots_data)


# ==============================
# PAGE: Data Query
# ==============================
elif page == "💬 Data Query":

    render_premium_header("Intelligent Data Query", "Ask natural language questions about your compliance data")
    render_data_query(st.session_state.plots_data)