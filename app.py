import streamlit as st
import re
from pathlib import Path
import PyPDF2
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.scoring.scoring import calculate_confidence_vector

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Nexus Governance OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
POLICY_PATH = BASE_DIR / "explainable_ai" / "policies" / "rules.yaml"
rule_engine = RuleEngine(POLICY_PATH)

# -------------------------------------------------
# ENTERPRISE DESIGN SYSTEM
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --primary: #0D47A1;
    --primary-light: #1565C0;
    --accent: #00BCD4;

    --success: #4CAF50;
    --warning: #FF9800;
    --error: #F44336;

    --bg-dark: #0F1419;
    --bg-card: #1A202C;
    --border: #2D3748;

    --text-primary: #FFFFFF;
    --text-secondary: #A0AEC0;
    --text-muted: #718096;
}

body {
    background: var(--bg-dark);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding: 3rem 4rem;
    max-width: 1200px;
}

.hero {
    padding-bottom: 2rem;
    margin-bottom: 3rem;
    border-bottom: 2px solid var(--primary);
}

.hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
}

.hero p {
    color: var(--text-secondary);
}

.module {
    font-size: 0.8rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 1rem;
    color: var(--text-muted);
    font-weight: 600;
}

.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    transition: 0.2s ease;
}

.card:hover {
    border-color: var(--primary);
}

.stButton > button {
    background: var(--primary);
    color: white;
    font-weight: 600;
    padding: 12px 24px;
    border-radius: 6px;
    border: none;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: var(--primary-light);
    transform: translateY(-1px);
}

.exec-banner {
    padding: 1.8rem;
    border-radius: 8px;
    margin-top: 2rem;
}

.kpi-strip {
    display: flex;
    gap: 1.5rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
}

.kpi-card {
    flex: 1;
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 1.5rem;
    border-radius: 8px;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
}

.empty-state {
    padding: 4rem;
    text-align: center;
    border: 2px dashed var(--border);
    border-radius: 8px;
    color: var(--text-secondary);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def extract_pdf_text(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def risk_color(level):
    return {
        "HIGH_RISK": "#F44336",
        "MEDIUM_RISK": "#FF9800",
        "LOW_RISK": "#4CAF50"
    }.get(level, "#0D47A1")

def animate_metric(label, value):
    placeholder = st.empty()
    for i in range(0, value + 1, max(1, value // 20 or 1)):
        placeholder.markdown(f"<div class='kpi-card'><div>{label}</div><div class='kpi-value'>{i}</div></div>", unsafe_allow_html=True)
        time.sleep(0.01)
    placeholder.markdown(f"<div class='kpi-card'><div>{label}</div><div class='kpi-value'>{value}</div></div>", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
view = st.sidebar.radio("Platform Navigation",
                        ["Dashboard", "Assessments", "Developer API", "Pricing"])

# -------------------------------------------------
# HERO
# -------------------------------------------------
st.markdown("""
<div class="hero">
<h1>Nexus Governance OS</h1>
<p>Deterministic AI for Contract Risk Governance • Built for the 2026 Compliance Era</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
if view == "Dashboard":

    st.markdown('<div class="module">Module 1 — Contract Ingestion</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])
    document_text = st.text_area("Or Paste Contract Text", height=200)

    st.markdown('</div>', unsafe_allow_html=True)

    if document_text.strip() or uploaded_pdf:

        if uploaded_pdf:
            document_text = extract_pdf_text(uploaded_pdf)

        rule_result = rule_engine.evaluate(document_text)

        confidence_vector = calculate_confidence_vector(
            passed_rules=rule_result["passed_rules"],
            failed_rules=rule_result["failed_rules"],
            total_rules=len(rule_engine.rules),
            retrieval_similarity=1.0,
            data_completeness=1.0,
        )

        governance_action = apply_governance_layer(
            deterministic_label=rule_result["deterministic_label"],
            confidence_vector=confidence_vector,
            crag_blocked=False,
        )

        # Executive Banner
        st.markdown(f"""
        <div class="exec-banner" style="border-left:6px solid {risk_color(rule_result['deterministic_label'])}; background:#1A202C;">
            <h3>Executive Risk Summary</h3>
            <p><strong>Risk Classification:</strong> {rule_result['deterministic_label']}</p>
            <p><strong>Governance Action:</strong> {governance_action}</p>
        </div>
        """, unsafe_allow_html=True)

        # KPI Strip with animation
        col1, col2, col3 = st.columns(3)
        with col1:
            animate_metric("Risk Exposure Index", rule_result["eligibility_score"])
        with col2:
            animate_metric("Failed Rules", len(rule_result["failed_rules"]))
        with col3:
            animate_metric("Passed Rules", len(rule_result["passed_rules"]))

        # Risk Severity Donut Gauge
        fig_gauge = go.Figure(go.Pie(
            values=[rule_result["eligibility_score"],
                    100 - rule_result["eligibility_score"]],
            hole=0.7
        ))

        fig_gauge.update_layout(
            title="Risk Severity Gauge",
            showlegend=False,
            paper_bgcolor="#0F1419",
            font=dict(color="white")
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

        # Pie Chart
        fig_pie = px.pie(
            names=["Passed", "Failed"],
            values=[len(rule_result["passed_rules"]),
                    len(rule_result["failed_rules"])],
            hole=0.5
        )
        fig_pie.update_layout(paper_bgcolor="#0F1419",
                              font_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Radar Chart
        categories = list(confidence_vector.keys())
        values = list(confidence_vector.values())

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            paper_bgcolor="#0F1419",
            font=dict(color="white"),
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# -------------------------------------------------
# ASSESSMENTS
# -------------------------------------------------
elif view == "Assessments":

    st.subheader("Recent Risk Assessments")

    if "history" not in st.session_state:
        st.markdown("""
        <div class="empty-state">
            No assessments yet.
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------
# DEVELOPER API
# -------------------------------------------------
elif view == "Developer API":

    st.subheader("API-First Architecture")

    st.code("""
curl -X POST https://api.nexusgovernance.ai/evaluate \\
-H "Content-Type: application/json" \\
-d '{"document_text": "Contract text here"}'
""")

# -------------------------------------------------
# PRICING
# -------------------------------------------------
elif view == "Pricing":

    st.subheader("Platform Plans")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card"><h3>Free</h3>Basic contract analysis</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card" style="border:2px solid var(--primary);"><h3>Pro</h3>Full XAI trace</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card"><h3>Enterprise</h3>API Access</div>', unsafe_allow_html=True)
