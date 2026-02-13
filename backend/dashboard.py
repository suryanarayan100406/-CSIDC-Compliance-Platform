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

# Matplotlib dark theme
plt.rcParams.update({
    'figure.facecolor': '#1a1f35',
    'axes.facecolor': '#1a1f35',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#94a3b8',
    'text.color': '#f1f5f9',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#1e293b',
    'figure.titlesize': 14,
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
# Risk Score Gauge Helper
# ==============================
def render_risk_gauge(score):
    """Render a color-coded risk score gauge."""
    if score >= 80:
        color = "#22c55e"  # green
        label = "✅ LOW RISK"
    elif score >= 50:
        color = "#f59e0b"  # yellow/amber
        label = "⚠️ MODERATE RISK"
    else:
        color = "#ef4444"  # red
        label = "🚨 HIGH RISK"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e1e2f, #2d2d44);
        border-radius: 12px; padding: 20px; margin: 10px 0;
        border-left: 6px solid {color};
    ">
        <p style="color: #aaa; margin: 0 0 5px 0; font-size: 12px;">COMPLIANCE RISK SCORE</p>
        <div style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 48px; font-weight: bold; color: {color};">{score}</span>
            <span style="font-size: 14px; color: #aaa;">/100</span>
        </div>
        <div style="
            background: #333; border-radius: 8px; height: 12px;
            margin: 10px 0; overflow: hidden;
        ">
            <div style="
                width: {score}%; height: 100%; border-radius: 8px;
                background: {color};
                transition: width 0.3s;
            "></div>
        </div>
        <p style="color: {color}; font-weight: bold; margin: 0;">{label}</p>
    </div>
    """, unsafe_allow_html=True)


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
# Alert Panel (Feature 5)
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

    bg_color = "#dc2626" if has_encroachment else "#16a34a"
    border_color = "#fca5a5" if has_encroachment else "#86efac"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {bg_color}22, {bg_color}11);
        border: 2px solid {border_color};
        border-radius: 12px; padding: 18px 24px; margin-bottom: 20px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div>
                <p style="color: {border_color}; font-size: 11px; margin: 0; font-weight: 600; letter-spacing: 1px;">🚨 REAL-TIME ALERTS</p>
                <p style="color: white; font-size: 24px; font-weight: bold; margin: 4px 0 0 0;">
                    {critical_violations} Critical Violation{'s' if critical_violations != 1 else ''}
                </p>
            </div>
            <div style="text-align: center;">
                <p style="color: #ccc; font-size: 11px; margin: 0;">REVENUE AT RISK</p>
                <p style="color: #fbbf24; font-size: 22px; font-weight: bold; margin: 4px 0 0 0;">₹{total_revenue_risk:,.2f}</p>
            </div>
            <div style="text-align: center;">
                <p style="color: #ccc; font-size: 11px; margin: 0;">HIGHEST RISK PLOT</p>
                <p style="color: #f87171; font-size: 22px; font-weight: bold; margin: 4px 0 0 0;">{highest_risk_plot} ({highest_risk_score})</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# Executive Summary Generator (Feature 6)
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
    elif compliance_rate >= 50:
        overall_status = "Moderate Concern"
        status_icon = "🟡"
    else:
        overall_status = "Critical"
        status_icon = "🔴"

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
        background: linear-gradient(135deg, #1e1e2f, #2d2d44);
        border-radius: 12px; padding: 20px; margin: 10px 0;
        border-left: 6px solid #8b5cf6;
    ">
        <p style="color: #a78bfa; font-size: 12px; font-weight: 600; letter-spacing: 1px; margin: 0 0 10px 0;">
            🤖 AI EXECUTIVE SUMMARY
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(summary_text)


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
# Sidebar Navigation
# ==============================
st.sidebar.title("📌 CSIDC Compliance Platform")
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

st.sidebar.markdown(f"**Plots in memory:** {len(st.session_state.plots_data)}")


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
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.bar(
                ["Encroachments", "Underutilized", "Compliant"],
                [
                    len(df[df["Encroached Area"] > 0]),
                    len(df[(df["Unused Area"] > 0) & (df["Encroached Area"] == 0)]),
                    compliant,
                ],
                color=["#ef4444", "#f59e0b", "#22c55e"],
            )
            ax.set_title("Plot Distribution")
            st.pyplot(fig)

        with c2:
            if "Risk Score" in df.columns:
                fig2, ax2 = plt.subplots(figsize=(5, 3))
                risk_bins = [
                    len(df[df["Risk Score"] >= 80]),
                    len(df[(df["Risk Score"] >= 50) & (df["Risk Score"] < 80)]),
                    len(df[df["Risk Score"] < 50]),
                ]
                ax2.pie(
                    risk_bins,
                    labels=["Low Risk (80+)", "Moderate (50-79)", "High Risk (<50)"],
                    colors=["#22c55e", "#f59e0b", "#ef4444"],
                    autopct="%1.1f%%",
                    startangle=90,
                )
                ax2.set_title("Risk Score Distribution")
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

    # Legend
    st.markdown("""
    **Legend:** 🔴 Encroachment &nbsp;&nbsp; 🟠 Underutilized &nbsp;&nbsp; 🟢 Compliant
    """)


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
            fig, ax = plt.subplots(figsize=(5, 3.5))
            enc_count = len(df[df["Encroached Area"] > 0])
            unused_count = len(df[(df["Unused Area"] > 0) & (df["Encroached Area"] == 0)])
            comp_count = len(df) - enc_count - unused_count
            ax.bar(
                ["Compliant", "Encroached", "Underutilized"],
                [comp_count, enc_count, unused_count],
                color=["#22c55e", "#ef4444", "#f59e0b"],
            )
            ax.set_title("Compliance Breakdown")
            st.pyplot(fig)

        with c2:
            if "Risk Score" in df.columns:
                fig2, ax2 = plt.subplots(figsize=(5, 3.5))
                ax2.hist(df["Risk Score"], bins=10, color="#6366f1", edgecolor="#333")
                ax2.set_xlabel("Risk Score")
                ax2.set_ylabel("# Plots")
                ax2.set_title("Risk Score Distribution")
                st.pyplot(fig2)

        st.markdown("---")

        # Revenue analysis
        st.subheader("💰 Revenue Impact Analysis")
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
            st.info("⚖ **Tolerance (25 m²) applied** — Minor deviations below 25 m² treated as zero. Plot classified as compliant within tolerance.")

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
        st.markdown(f"**Total Inspections:** {len(df)}")

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
    ### Deployment Architecture — CSIDC Industrial Compliance Intelligence Platform

    This platform is built on a modular, scalable architecture designed for
    real-time compliance monitoring of industrial land parcels across Chhattisgarh.
    """)

    # Architecture components using columns
    arch1, arch2 = st.columns(2)

    with arch1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e1e2f, #2d2d44);
            border-radius: 12px; padding: 20px; margin: 8px 0;
            border-left: 6px solid #3b82f6;
        ">
            <h4 style="color: #60a5fa; margin: 0 0 10px 0;">🖥 Frontend — Streamlit</h4>
            <ul style="color: #ccc; font-size: 14px;">
                <li>Interactive dashboards & real-time analytics</li>
                <li>Role-based access control (Inspector/Admin)</li>
                <li>PDF report generation & CSV export</li>
                <li>Folium satellite map integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e1e2f, #2d2d44);
            border-radius: 12px; padding: 20px; margin: 8px 0;
            border-left: 6px solid #22c55e;
        ">
            <h4 style="color: #4ade80; margin: 0 0 10px 0;">🌍 GIS Engine — Shapely + PyProj</h4>
            <ul style="color: #ccc; font-size: 14px;">
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
            background: linear-gradient(135deg, #1e1e2f, #2d2d44);
            border-radius: 12px; padding: 20px; margin: 8px 0;
            border-left: 6px solid #f59e0b;
        ">
            <h4 style="color: #fbbf24; margin: 0 0 10px 0;">⚙ Backend — Flask REST API</h4>
            <ul style="color: #ccc; font-size: 14px;">
                <li>RESTful endpoints for all GIS operations</li>
                <li>Compliance scoring engine (0–100)</li>
                <li>Legal risk classification & recommendation</li>
                <li>Tolerance threshold filtering (25 m²)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e1e2f, #2d2d44);
            border-radius: 12px; padding: 20px; margin: 8px 0;
            border-left: 6px solid #8b5cf6;
        ">
            <h4 style="color: #a78bfa; margin: 0 0 10px 0;">🛰 Satellite Visualization — Folium</h4>
            <ul style="color: #ccc; font-size: 14px;">
                <li>ESRI World Imagery satellite tiles</li>
                <li>Color-coded plot markers (Red/Yellow/Green)</li>
                <li>Interactive popups with compliance details</li>
                <li>Multi-plot overlay for state-wide monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Flow diagram using Streamlit layout
    st.subheader("📐 Data Flow Diagram")

    st.markdown("""
    <div style="
        background: #1a1a2e; border-radius: 12px; padding: 30px;
        text-align: center; font-family: monospace;
    ">
        <div style="display: flex; align-items: center; justify-content: center; gap: 10px; flex-wrap: wrap;">
            <div style="background: #3b82f6; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold;">
                📄 GeoJSON Input
            </div>
            <span style="color: #666; font-size: 24px;">→</span>
            <div style="background: #f59e0b; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold;">
                ⚙ Flask API
            </div>
            <span style="color: #666; font-size: 24px;">→</span>
            <div style="background: #22c55e; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold;">
                🌍 Shapely/PyProj
            </div>
            <span style="color: #666; font-size: 24px;">→</span>
            <div style="background: #8b5cf6; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold;">
                📊 Compliance Score
            </div>
            <span style="color: #666; font-size: 24px;">→</span>
            <div style="background: #ef4444; padding: 12px 20px; border-radius: 8px; color: white; font-weight: bold;">
                🖥 Streamlit Dashboard
            </div>
        </div>
        <div style="margin-top: 20px; color: #888; font-size: 12px;">
            GeoJSON → Boundary Comparison → Area Calculation → Risk Scoring → Visualization & Reporting
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API endpoints table
    st.subheader("🔌 API Endpoints")
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
