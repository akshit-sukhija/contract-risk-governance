import streamlit as st
import re
from pathlib import Path
from typing import Optional
import PyPDF2
import plotly.graph_objects as go

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

    .kpi-card { background: linear-gradient(145deg,#161616,#111111); border: 1px solid #222; border-top: 2px solid #007BFF; padding: 1.1rem 1.2rem; border-radius: 6px; margin-bottom: 0.5rem; position: relative; overflow: hidden; }
    .kpi-card::before { content:''; position:absolute; top:0;left:0;right:0;bottom:0; background:radial-gradient(ellipse at top left,rgba(0,123,255,0.04),transparent 60%); pointer-events:none; }
    .kpi-card.risk { border-top-color:#FF4B4B; }
    .kpi-card.risk::before { background:radial-gradient(ellipse at top left,rgba(255,75,75,0.05),transparent 60%); }
    .kpi-card.warn { border-top-color:#FFA500; }
    .kpi-card.safe { border-top-color:#00C853; }
    .kpi-label { font-size:0.68rem; color:#555; text-transform:uppercase; letter-spacing:1.5px; font-family:'JetBrains Mono',monospace; margin-bottom:0.4rem; }
    .kpi-value { font-size:2rem; font-weight:700; color:#FFFFFF; font-family:'JetBrains Mono',monospace; line-height:1; margin-bottom:0.4rem; }
    .kpi-value span { font-size:0.9rem; color:#555; font-weight:400; }
    .kpi-trend { font-size:0.72rem; font-family:'JetBrains Mono',monospace; }
    .trend-up { color:#00C853; } .trend-dn { color:#FF4B4B; } .trend-nt { color:#888; }

    .section-header { font-size:0.7rem; color:#444; text-transform:uppercase; letter-spacing:2px; font-family:'JetBrains Mono',monospace; padding:0.5rem 0 0.75rem; border-bottom:1px solid #1E1E1E; margin-bottom:1rem; display:flex; align-items:center; justify-content:space-between; }
    .section-header .tag { background:#1A1A2E; color:#007BFF; padding:2px 8px; border-radius:20px; font-size:0.6rem; border:1px solid #007BFF33; }
    .nexus-card { background:#121212; border:1px solid #1E1E1E; padding:1.2rem; border-radius:6px; margin-bottom:0.75rem; }

    .badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.65rem; font-weight:700; font-family:'JetBrains Mono',monospace; text-transform:uppercase; letter-spacing:0.5px; }
    .badge-red   { background:rgba(255,75,75,0.12); color:#FF4B4B; border:1px solid rgba(255,75,75,0.3); }
    .badge-orange{ background:rgba(255,165,0,0.12); color:#FFA500; border:1px solid rgba(255,165,0,0.3); }
    .badge-green { background:rgba(0,200,83,0.12);  color:#00C853; border:1px solid rgba(0,200,83,0.3); }
    .badge-blue  { background:rgba(0,123,255,0.12); color:#007BFF; border:1px solid rgba(0,123,255,0.3); }

    .risk-table { width:100%; border-collapse:collapse; font-size:0.8rem; }
    .risk-table th { color:#444; text-transform:uppercase; font-size:0.62rem; letter-spacing:1px; font-family:'JetBrains Mono',monospace; padding:8px 12px; border-bottom:1px solid #1E1E1E; text-align:left; font-weight:500; }
    .risk-table td { padding:9px 12px; border-bottom:1px solid #151515; color:#B0B0B0; vertical-align:middle; }
    .risk-table td.name { color:#E0E0E0; font-weight:500; }
    .risk-table tr:hover td { background:rgba(255,255,255,0.02); }

    .progress-wrap { background:#1A1A1A; height:6px; border-radius:10px; overflow:hidden; margin:6px 0; }
    .progress-fill { height:6px; border-radius:10px; background:linear-gradient(90deg,#007BFF,#00C2FF); }
    .progress-fill.risk { background:linear-gradient(90deg,#FF4B4B,#FF7070); }

    .stButton>button { background:#007BFF !important; color:white !important; border:none !important; border-radius:3px !important; font-family:'JetBrains Mono',monospace !important; font-size:0.75rem !important; letter-spacing:1.5px !important; text-transform:uppercase !important; padding:0.5rem 1.5rem !important; }
    .stButton>button:hover { background:#0056b3 !important; box-shadow:0 0 20px rgba(0,123,255,0.35) !important; }

    [data-testid="stAlert"] { background:#0F1A2E !important; border:1px solid #007BFF33 !important; border-left:3px solid #007BFF !important; border-radius:4px !important; color:#B0C8E8 !important; font-size:0.82rem !important; }
    [data-testid="stRadio"] label { font-size:0.8rem !important; font-family:'JetBrains Mono',monospace !important; color:#666 !important; }
    [data-testid="stExpander"] { background:#111 !important; border:1px solid #1E1E1E !important; border-radius:4px !important; }
    [data-testid="stExpander"] summary { font-family:'JetBrains Mono',monospace !important; font-size:0.75rem !important; color:#555 !important; }

    .version-tag { display:inline-block; background:#111; border:1px solid #222; color:#444; padding:2px 7px; border-radius:10px; font-size:0.58rem; font-family:'JetBrains Mono',monospace; margin-top:4px; }
    .rec-box { background:#0A1628; border:1px solid #007BFF33; border-left:3px solid #007BFF; padding:0.9rem 1rem; border-radius:4px; font-size:0.8rem; color:#8AB4D8; line-height:1.6; }
    .rec-box strong { color:#007BFF; display:block; margin-bottom:0.4rem; font-size:0.72rem; letter-spacing:1px; text-transform:uppercase; font-family:'JetBrains Mono',monospace; }
    .stat-row { display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #151515; }
    .stat-key { color:#444; font-size:0.72rem; font-family:'JetBrains Mono',monospace; }
    .stat-val { color:#E0E0E0; font-size:0.72rem; font-family:'JetBrains Mono',monospace; }
    .log-entry { display:flex; align-items:flex-start; gap:12px; padding:0.6rem 0; border-bottom:1px solid #151515; font-size:0.76rem; }
    .log-time { color:#333; font-family:'JetBrains Mono',monospace; min-width:90px; font-size:0.68rem; }
    .log-event { color:#B0B0B0; }
    .log-event strong { color:#E0E0E0; }
    .log-dot { width:6px; height:6px; border-radius:50%; background:#007BFF; margin-top:4px; flex-shrink:0; }
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

def progress_bar(pct, risk=False):
    cls = "risk" if risk else ""
    return f'<div class="progress-wrap"><div class="progress-fill {cls}" style="width:{pct}%"></div></div>'


# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="#007BFF"><path d="M12 1L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 1Z"/></svg>
            <span style="color:#007BFF;font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;letter-spacing:2px;">NEXUS</span>
        </div>
        <div style="font-size:0.6rem;color:#333;letter-spacing:2px;font-family:'JetBrains Mono',monospace;text-transform:uppercase;">Architect · Compliance OS</div>
        <span class="version-tag">v1.0.5</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:1px;background:#1A1A1A;margin-bottom:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.58rem;color:#2A2A2A;letter-spacing:2px;font-family:JetBrains Mono,monospace;padding-bottom:4px;'>MAIN</div>", unsafe_allow_html=True)
    view = st.radio("", ["📊  Dashboard", "📤  Ingestion", "📜  Audit Log"], label_visibility="collapsed")
    st.markdown("<div style='height:1px;background:#1A1A1A;margin:1rem 0 0.75rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.58rem;color:#2A2A2A;letter-spacing:2px;font-family:JetBrains Mono,monospace;padding-bottom:4px;'>CONFIG</div>", unsafe_allow_html=True)
    with st.expander("⚙  Settings"):
        enable_ai = st.checkbox("AI Confidence Layer", value=True)
        risk_threshold = st.slider("Risk Threshold", 0, 100, 70)
        st.caption(f"Flagging clauses scoring > {risk_threshold}")
    st.markdown("<div style='height:1px;background:#1A1A1A;margin:1rem 0 0.75rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="nexus-card" style="padding:0.75rem;">
        <div class="stat-row"><span class="stat-key">Engine</span><span class="stat-val" style="color:#007BFF;">XAI Rule v3</span></div>
        <div class="stat-row"><span class="stat-key">Mode</span><span class="stat-val">Deterministic</span></div>
        <div class="stat-row"><span class="stat-key">Latency</span><span class="stat-val">~1.2s</span></div>
        <div class="stat-row" style="border:none;"><span class="stat-key">Status</span><span class="stat-val" style="color:#00C853;">● ONLINE</span></div>
    </div>""", unsafe_allow_html=True)


# ── DASHBOARD ─────────────────────────────────────────────────
if view == "📊  Dashboard":
    col_title, col_act = st.columns([3,1])
    with col_title:
        st.markdown("""
        <div style="padding-bottom:0.5rem;">
            <div style="font-size:0.65rem;color:#333;font-family:'JetBrains Mono',monospace;letter-spacing:2px;text-transform:uppercase;">Contract Risk & Governance Engine</div>
            <h2 style="color:#FFFFFF;font-size:1.5rem;font-weight:700;margin:0.1rem 0 0;">AI Analysis Overview</h2>
        </div>""", unsafe_allow_html=True)
    with col_act:
        st.markdown("<div style='padding-top:1.5rem;'>", unsafe_allow_html=True)
        st.button("⟳  Refresh Analysis")
    st.markdown("<div style='height:1px;background:#1A1A1A;margin-bottom:1.25rem;'></div>", unsafe_allow_html=True)

    k1,k2,k3,k4 = st.columns(4)
    with k1: kpi_card("Risk Score","72","/100","+2 pts this week","dn","risk")
    with k2: kpi_card("Clauses Analyzed","47","pages","+6 pages","up")
    with k3: kpi_card("Identified Risks","5","flags","Critical: 2","dn","warn")
    with k4: kpi_card("AI Confidence","94","%","+1% verified","up","safe")
    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    col_main, col_side = st.columns([3,2], gap="medium")
    with col_main:
        section_header("AI RISK TREND", "LIVE")
        fig = go.Figure()
        x = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        fig.add_trace(go.Scatter(x=x,y=[22,28,18,32,41,35,38,44,30,25,36,40],name="Risk Exposure",mode='lines',line=dict(color='#007BFF',width=2.5,shape='spline'),fill='tozeroy',fillcolor='rgba(0,123,255,0.07)'))
        fig.add_trace(go.Scatter(x=x,y=[15,20,25,18,28,30,22,35,28,20,28,32],name="Clause Flags",mode='lines',line=dict(color='#FF4B4B',width=1.5,shape='spline',dash='dot'),fill='tozeroy',fillcolor='rgba(255,75,75,0.04)'))
        fig.add_annotation(x="Aug",y=44,text="Peak: 44%",showarrow=True,arrowhead=2,arrowcolor="#FF4B4B",font=dict(color="#FF4B4B",size=10),bgcolor="#1A0A0A",bordercolor="#FF4B4B33")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family="JetBrains Mono",color="#444",size=10),height=240,margin=dict(l=0,r=0,t=10,b=0),xaxis=dict(gridcolor="#151515",showline=False,zeroline=False),yaxis=dict(gridcolor="#151515",showline=False,zeroline=False),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10,color="#444"),bgcolor="rgba(0,0,0,0)"),hovermode="x unified")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

        section_header("RELEVANT CASES","5 ACTIVE")
        st.markdown("""
        <table class="risk-table">
            <thead><tr><th>Case Name</th><th>Jurisdiction</th><th>Year</th><th>Relevance</th><th>Clause</th><th>Status</th></tr></thead>
            <tbody>
                <tr><td class="name">Nova Systems Corp</td><td>🇬🇧 UK</td><td>2025</td><td>93%</td><td>5.1</td><td><span class="badge badge-green">Win</span></td></tr>
                <tr><td class="name">Confidentiality Clause Dispute</td><td>🇪🇺 EU</td><td>2022</td><td>89%</td><td>5.2</td><td><span class="badge badge-blue">Settled</span></td></tr>
                <tr><td class="name">TechSoft vs. Orion Ltd</td><td>🇬🇧 UK</td><td>2024</td><td>94%</td><td>2.3</td><td><span class="badge badge-green">Win</span></td></tr>
                <tr><td class="name">Clause 2.3 Interpretation</td><td>🇺🇸 US</td><td>2023</td><td>86%</td><td>—</td><td><span class="badge badge-red">Loss</span></td></tr>
                <tr><td class="name">Helix Innovations Inc</td><td>🇪🇺 EU</td><td>2025</td><td>88%</td><td>7.4</td><td><span class="badge badge-blue">Settled</span></td></tr>
            </tbody>
        </table>
        <div style="font-size:0.62rem;color:#333;font-family:'JetBrains Mono',monospace;margin-top:0.5rem;">Last precedent update: Nov 2025</div>
        """, unsafe_allow_html=True)

    with col_side:
        section_header("DOCUMENT STATUS")
        st.markdown(f"""
        <div class="nexus-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-size:0.68rem;color:#444;font-family:'JetBrains Mono',monospace;margin-bottom:4px;">CURRENT FILE</div>
                    <div style="color:#E0E0E0;font-weight:600;font-size:0.9rem;">NDA_v3.2_Draft.pdf</div>
                    <div style="color:#333;font-size:0.68rem;font-family:'JetBrains Mono',monospace;margin-top:2px;">PDF · 1.1 MB</div>
                </div>
                <span class="badge badge-orange">IN REVIEW</span>
            </div>
            <div style="margin-top:1rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;font-family:'JetBrains Mono',monospace;color:#444;margin-bottom:4px;"><span>AI Review Progress</span><span style="color:#007BFF;">91%</span></div>
                {progress_bar(91)}
                <div style="font-size:0.62rem;color:#333;font-family:'JetBrains Mono',monospace;margin-top:4px;">Stage: Clause Analysis</div>
            </div>
            <div style="margin-top:1rem;">
                <div class="stat-row"><span class="stat-key">Analyzed</span><span class="stat-val">07 Nov 2025</span></div>
                <div class="stat-row"><span class="stat-key">Last Edited</span><span class="stat-val">Anna K., Associate</span></div>
                <div class="stat-row" style="border:none;"><span class="stat-key">Pages</span><span class="stat-val">47 / 51</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

        section_header("AI SUMMARY")
        st.markdown("""
        <div class="nexus-card" style="padding:0.9rem 1rem;">
            <div class="stat-row"><span class="stat-key">Risk Zone</span><span class="stat-val"><span class="badge badge-orange">Medium 2.3</span></span></div>
            <div class="stat-row"><span class="stat-key">Clause Type</span><span class="stat-val">License / IP</span></div>
            <div class="stat-row" style="border:none;"><span class="stat-key">Impact</span><span class="stat-val" style="color:#FFA500;">May affect exclusivity</span></div>
            <div class="rec-box" style="margin-top:0.75rem;">
                <strong>⚑ Recommendation</strong>
                Clarify "limited license" or replace with "non-exclusive use right" in Section 4.2. Add a 1× contract value financial cap on liability exposure.
            </div>
        </div>""", unsafe_allow_html=True)
        st.button("→  See Suggested Rewrite")

        section_header("RECENT DOCUMENTS")
        for name,meta,level in [("NDA_v3.2_Draft.pdf","PDF · 1.1 MB","high"),("SupplierContract.docx","DOC · 0.63 MB","clear"),("NDA_v4.1_Final.pdf","PDF · 1.4 MB","medium")]:
            lm={"high":("badge-red","HIGH RISK"),"medium":("badge-orange","MEDIUM"),"clear":("badge-green","CLEAR")}[level]
            st.markdown(f'<div class="nexus-card" style="padding:0.65rem 0.9rem;display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem;"><div><div style="color:#E0E0E0;font-size:0.78rem;font-weight:500;">{name}</div><div style="color:#333;font-size:0.65rem;font-family:JetBrains Mono,monospace;">{meta}</div></div><span class="badge {lm[0]}">{lm[1]}</span></div>',unsafe_allow_html=True)


# ── INGESTION ─────────────────────────────────────────────────
elif view == "📤  Ingestion":
    st.markdown('<h2 style="color:#FFF;font-size:1.4rem;font-weight:700;margin-bottom:0.25rem;">Document Ingestion</h2><div style="font-size:0.7rem;color:#333;font-family:JetBrains Mono,monospace;margin-bottom:1.5rem;">Upload and queue legal documents for XAI analysis</div>',unsafe_allow_html=True)
    col_up,col_info=st.columns([3,2],gap="medium")
    with col_up:
        section_header("UPLOAD DOCUMENT")
        uploaded_file=st.file_uploader("Drop your PDF here",type=["pdf"],help="Supports PDF up to 50MB")
        if uploaded_file:
            st.markdown(f'<div class="nexus-card" style="border-top:2px solid #00C853;"><div style="font-size:0.68rem;color:#444;font-family:JetBrains Mono,monospace;">FILE LOADED</div><div style="color:#E0E0E0;font-weight:600;margin:4px 0;">{uploaded_file.name}</div><div style="color:#333;font-size:0.68rem;font-family:JetBrains Mono,monospace;">{uploaded_file.size//1024} KB · PDF</div>{progress_bar(100)}</div>',unsafe_allow_html=True)
            if st.button("▶  Run XAI Analysis"):
                with st.spinner("Parsing document through XAI rule engine…"):
                    import time; time.sleep(1.5)
                st.success("Analysis complete. Navigate to Dashboard to view results.")
        else:
            st.markdown('<div style="border:1px dashed #252525;border-radius:6px;padding:2rem;text-align:center;background:#0D0D0D;color:#333;font-size:0.78rem;font-family:JetBrains Mono,monospace;"><div style="font-size:2rem;margin-bottom:0.5rem;">⬆</div>Drag & drop a PDF contract</div>',unsafe_allow_html=True)
        section_header("PROCESSING QUEUE")
        for fn,st_,co in [("MSA_TechSoft_2025.pdf","Queued","blue"),("NDA_v3.2_Draft.pdf","Processing","orange"),("Vendor_SLA_v1.pdf","Complete","green")]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #151515;"><span style="font-size:0.78rem;color:#B0B0B0;">{fn}</span><span class="badge badge-{co}">{st_}</span></div>',unsafe_allow_html=True)
    with col_info:
        section_header("ENGINE CONFIG")
        st.markdown("""<div class="nexus-card">
            <div class="stat-row"><span class="stat-key">Engine</span><span class="stat-val" style="color:#007BFF;">XAI Rule v3.1</span></div>
            <div class="stat-row"><span class="stat-key">Mode</span><span class="stat-val">Deterministic</span></div>
            <div class="stat-row"><span class="stat-key">Risk Threshold</span><span class="stat-val">70 / 100</span></div>
            <div class="stat-row"><span class="stat-key">Max Pages</span><span class="stat-val">200</span></div>
            <div class="stat-row" style="border:none;"><span class="stat-key">Supported</span><span class="stat-val">PDF, DOCX</span></div>
        </div>""",unsafe_allow_html=True)
        section_header("ANALYSIS BREAKDOWN")
        for label,val in [("Liability Clauses",78),("IP / License",91),("Indemnity",55),("Termination",82),("Confidentiality",67)]:
            risk=val<65
            col='"#FF4B4B"' if risk else '"#007BFF"'
            st.markdown(f'<div style="margin-bottom:0.6rem;"><div style="display:flex;justify-content:space-between;font-size:0.7rem;font-family:JetBrains Mono,monospace;color:#555;margin-bottom:3px;"><span>{label}</span><span style="color:{col[1:-1]};">{val}%</span></div>{progress_bar(val,risk=risk)}</div>',unsafe_allow_html=True)


# ── AUDIT LOG ─────────────────────────────────────────────────
elif view == "📜  Audit Log":
    st.markdown('<h2 style="color:#FFF;font-size:1.4rem;font-weight:700;margin-bottom:0.25rem;">Audit Log</h2><div style="font-size:0.7rem;color:#333;font-family:JetBrains Mono,monospace;margin-bottom:1.5rem;">Immutable record of all system events and analysis actions</div>',unsafe_allow_html=True)
    col_log,col_fil=st.columns([3,1],gap="medium")
    with col_fil:
        section_header("FILTERS")
        st.selectbox("Event Type",["All Events","Analysis","Upload","Export","Auth"],label_visibility="collapsed")
        st.date_input("From Date",label_visibility="collapsed")
        st.button("Apply Filters")
        section_header("SUMMARY")
        st.markdown("""<div class="nexus-card">
            <div class="stat-row"><span class="stat-key">Total Events</span><span class="stat-val">1,284</span></div>
            <div class="stat-row"><span class="stat-key">Today</span><span class="stat-val" style="color:#007BFF;">23</span></div>
            <div class="stat-row"><span class="stat-key">Warnings</span><span class="stat-val" style="color:#FFA500;">7</span></div>
            <div class="stat-row" style="border:none;"><span class="stat-key">Errors</span><span class="stat-val" style="color:#FF4B4B;">1</span></div>
        </div>""",unsafe_allow_html=True)
    with col_log:
        section_header("EVENT STREAM","LIVE")
        dot={"green":"#00C853","orange":"#FFA500","blue":"#007BFF","red":"#FF4B4B"}
        for ts,ev,sub,det,co in [
            ("14:22:01","Analysis Complete","NDA_v3.2_Draft.pdf","Risk Score: 72/100","green"),
            ("14:20:45","Clause Flagged","Section 4.2 — Liability","Missing financial cap detected","orange"),
            ("14:18:11","Document Uploaded","NDA_v3.2_Draft.pdf","1.1 MB · PDF validated","blue"),
            ("13:55:32","Analysis Complete","Vendor_SLA_v1.pdf","Risk Score: 34/100 — Clear","green"),
            ("13:50:10","Rule Engine Triggered","XAI Rule v3.1","Indemnity ruleset applied","blue"),
            ("13:44:08","User Auth","anna.k@firm.com","Login · 2FA verified","blue"),
            ("12:30:00","Export Generated","Report_Nov2025.pdf","Sent to anna.k@firm.com","green"),
            ("11:15:22","Warning","MSA_TechSoft_2025.pdf","Ambiguous jurisdiction clause","orange"),
            ("09:01:55","System Boot","Nexus Engine v1.0.5","All services healthy","blue"),
        ]:
            st.markdown(f'<div class="log-entry"><div class="log-time">{ts}</div><div class="log-dot" style="background:{dot[co]};"></div><div class="log-event"><strong>{ev}</strong> · {sub}<br><span style="font-size:0.68rem;color:#333;">{det}</span></div></div>',unsafe_allow_html=True)
