import streamlit as st
import re
from pathlib import Path
from typing import Optional
import PyPDF2
import plotly.graph_objects as go

# ------------------------------
# 1. THEME & BRUTALIST CSS
# ------------------------------
st.set_page_config(page_title="Nexus Architect | Contract Risk", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #0E0E0E !important; color: #E0E0E0; font-family: 'Inter', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    section[data-testid="stSidebar"] > div { background-color: #0A0A0A !important; border-right: 1px solid #1E1E1E; }
    [data-testid="stSidebarContent"] { padding: 1rem 0.75rem; }
    ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #111; }
    ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 10px; }
    #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

    /* KPI Cards */
    .kpi-card { background: linear-gradient(145deg,#161616,#111111); border: 1px solid #222; border-top: 2px solid #007BFF; padding: 1.1rem 1.2rem; border-radius: 6px; margin-bottom: 0.5rem; position: relative; overflow: hidden; }
    .kpi-card.risk { border-top-color:#FF4B4B; }
    .kpi-card.warn { border-top-color:#FFA500; }
    .kpi-card.safe { border-top-color:#00C853; }
    .kpi-label { font-size:0.68rem; color:#555; text-transform:uppercase; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; margin-bottom:0.4rem; }
    .kpi-value { font-size:2rem; font-weight:700; color:#FFFFFF; font-family:'JetBrains Mono',monospace; line-height:1; margin-bottom:0.4rem; }
    .kpi-trend { font-size:0.72rem; font-family:'JetBrains Mono',monospace; }
    .trend-up { color:#00C853; } .trend-dn { color:#FF4B4B; } .trend-nt { color:#888; }

    /* UI Elements */
    .section-header { font-size:0.7rem; color:#444; text-transform:uppercase; letter-spacing:2px; font-family:'JetBrains Mono',monospace; padding:0.5rem 0 0.75rem; border-bottom:1px solid #1E1E1E; margin-bottom:1rem; display:flex; align-items:center; justify-content:space-between; }
    .tag { background:#1A1A2E; color:#007BFF; padding:2px 8px; border-radius:20px; font-size:0.6rem; border:1px solid #007BFF33; }
    .nexus-card { background:#121212; border:1px solid #1E1E1E; padding:1.2rem; border-radius:6px; margin-bottom:0.75rem; }

    /* Badges */
    .badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.65rem; font-weight:700; font-family:'JetBrains Mono',monospace; text-transform:uppercase; }
    .badge-red   { background:rgba(255,75,75,0.12); color:#FF4B4B; border:1px solid rgba(255,75,75,0.3); }
    .badge-orange{ background:rgba(255,165,0,0.12); color:#FFA500; border:1px solid rgba(255,165,0,0.3); }
    .badge-green { background:rgba(0,200,83,0.12);  color:#00C853; border:1px solid rgba(0,200,83,0.3); }
    .badge-blue  { background:rgba(0,123,255,0.12); color:#007BFF; border:1px solid rgba(0,123,255,0.3); }

    /* Tables */
    .risk-table { width:100%; border-collapse:collapse; font-size:0.8rem; }
    .risk-table th { color:#444; text-transform:uppercase; font-size:0.62rem; letter-spacing:1px; font-family:'JetBrains Mono',monospace; padding:8px 12px; border-bottom:1px solid #1E1E1E; text-align:left; }
    .risk-table td { padding:9px 12px; border-bottom:1px solid #151515; color:#B0B0B0; }

    /* Progress */
    .progress-wrap { background:#1A1A1A; height:6px; border-radius:10px; overflow:hidden; margin:6px 0; }
    .progress-fill { height:6px; border-radius:10px; background:linear-gradient(90deg,#007BFF,#00C2FF); }

    /* Buttons */
    .stButton>button { background:#007BFF !important; color:white !important; border-radius:3px !important; font-family:'JetBrains Mono',monospace !important; font-size:0.75rem !important; text-transform:uppercase !important; width: 100%; }
    .stButton>button:hover { background:#0056b3 !important; box-shadow:0 0 20px rgba(0,123,255,0.35) !important; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────
def kpi_card(label, value, unit, trend, trend_dir="up", card_class=""):
    tc = {"up":"trend-up","dn":"trend-dn","nt":"trend-nt"}.get(trend_dir,"trend-nt")
    ar = {"up":"↑","dn":"↓","nt":"—"}.get(trend_dir,"—")
    st.markdown(f"""
    <div class="kpi-card {card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span> {unit}</span></div>
        <div class="kpi-trend {tc}">{ar} {trend}</div>
    </div>""", unsafe_allow_html=True)

def section_header(title, tag=""):
    tag_html = f'<span class="tag">{tag}</span>' if tag else ""
    st.markdown(f'<div class="section-header"><span>{title}</span>{tag_html}</div>', unsafe_allow_html=True)

def progress_bar(pct):
    return f'<div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>'

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem;">
        <div style="display:flex;align-items:center;gap:8px;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="#007BFF"><path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1Z"/></svg>
            <span style="color:#007BFF;font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;letter-spacing:2px;">NEXUS</span>
        </div>
        <div style="font-size:0.6rem;color:#333;font-family:'JetBrains Mono',monospace;text-transform:uppercase;">Architect · Compliance OS</div>
        <span class="version-tag">v1.0.6</span>
    </div>
    """, unsafe_allow_html=True)
    view = st.radio("MAIN", ["📊 Dashboard", "📤 Ingestion", "📜 Audit Log"], label_visibility="collapsed")
    with st.expander("⚙ Settings"):
        st.checkbox("AI Confidence Layer", value=True)
        st.slider("Risk Threshold", 0, 100, 70)

# ── DASHBOARD ─────────────────────────────────────────────────
if view == "📊 Dashboard":
    st.markdown("""<h2 style="color:#FFFFFF;font-size:1.5rem;font-weight:700;">AI Analysis Overview</h2>""", unsafe_allow_html=True)
    
    k1,k2,k3,k4 = st.columns(4)
    with k1: kpi_card("Risk Score","72","/100","+2 pts","dn","risk")
    with k2: kpi_card("Clauses Analyzed","47","pages","+6 pages","up")
    with k3: kpi_card("Identified Risks","5","flags","Critical: 2","dn","warn")
    with k4: kpi_card("AI Confidence","94","%","+1% verified","up","safe")

    col_main, col_side = st.columns([3,2], gap="medium")
    with col_main:
        section_header("AI RISK TREND", "LIVE")
        fig = go.Figure()
        x = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fig.add_trace(go.Scatter(x=x,y=[22,28,18,32,41,35,38,44,30,25,36,40],name="Risk Exposure",mode='lines',line=dict(color='#007BFF',width=2.5,shape='spline'),fill='tozeroy',fillcolor='rgba(0,123,255,0.07)'))
        
        # --- FIXED LINE 159: Corrected 8-digit hex to standard hex ---
        fig.add_annotation(x="Aug",y=44,text="Peak: 44%",showarrow=True,arrowhead=2,arrowcolor="#FF4B4B",font=dict(color="#FF4B4B",size=10),bgcolor="#1A0A0A",bordercolor="#FF4B4B")
        
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family="JetBrains Mono",color="#444",size=10),height=240,margin=dict(l=0,r=0,t=10,b=0),xaxis=dict(gridcolor="#151515"),yaxis=dict(gridcolor="#151515"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

        section_header("RELEVANT CASES","5 ACTIVE")
        st.markdown("""
        <table class="risk-table">
            <thead><tr><th>Case Name</th><th>Jurisdiction</th><th>Year</th><th>Status</th></tr></thead>
            <tbody>
                <tr><td>Nova Systems Corp</td><td>🇬🇧 UK</td><td>2025</td><td><span class="badge badge-green">Win</span></td></tr>
                <tr><td>Confidentiality Dispute</td><td>🇪🇺 EU</td><td>2022</td><td><span class="badge badge-blue">Settled</span></td></tr>
                <tr><td>TechSoft vs. Orion</td><td>🇬🇧 UK</td><td>2024</td><td><span class="badge badge-green">Win</span></td></tr>
            </tbody>
        </table>""", unsafe_allow_html=True)

    with col_side:
        section_header("DOCUMENT STATUS")
        st.markdown(f"""
        <div class="nexus-card">
            <div style="font-size:0.68rem;color:#444;">CURRENT FILE</div>
            <div style="color:#E0E0E0;font-weight:600;">NDA_v3.2_Draft.pdf</div>
            <div style="margin-top:1rem;">{progress_bar(91)}</div>
            <div style="font-size:0.62rem;color:#333;margin-top:4px;">Stage: Clause Analysis (91%)</div>
        </div>""", unsafe_allow_html=True)

        section_header("AI SUMMARY")
        st.markdown("""
        <div class="nexus-card">
            <div class="badge badge-orange">Medium 2.3</div>
            <p style="font-size:0.8rem; color:#8AB4D8; margin-top:10px;">
            <strong>⚑ Recommendation:</strong> Clarify "limited license" in Section 4.2. Add a liability cap to mitigate exposure.
            </p>
        </div>""", unsafe_allow_html=True)
        st.button("→ View Suggested Rewrite")

# --- OTHER VIEWS (INGESTION/AUDIT) PLACEHOLDERS ---
elif view == "📤 Ingestion":
    st.markdown("### Document Ingestion")
    st.file_uploader("Upload Contract PDF", type=["pdf"])
    st.button("▶ Run Analysis")

elif view == "📜 Audit Log":
    st.markdown("### Governance Audit Log")
    st.markdown("""<div class="nexus-card">14:22:01 | Analysis Complete | Risk Score: 72/100</div>""", unsafe_allow_html=True)
