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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

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

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

body { background: var(--bg-dark); color: var(--text-primary); }

.block-container { padding: 3rem 4rem; max-width: 1200px; }

.hero { padding-bottom: 2rem; margin-bottom: 3rem; border-bottom: 2px solid var(--primary); }
.hero h1 { font-size: 2.6rem; font-weight: 700; margin-bottom: 0.5rem; }
.hero p { color: var(--text-secondary); }

.module { font-size: 0.8rem; letter-spacing: 1.5px; text-transform: uppercase;
          margin-bottom: 1rem; color: var(--text-muted); font-weight: 600; }

.card { background: var(--bg-card); border: 1px solid var(--border);
        padding: 2rem; border-radius: 12px; margin-bottom: 2rem;
        transition: all 0.25s ease; }

.card:hover { border-color: var(--primary); }

.stButton > button {
    background: var(--primary);
    color: white;
    font-weight: 600;
    padding: 12px 24px;
    border-radius: 6px;
    border: none;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: var(--primary-light);
    transform: translateY(-1px);
}

.exec-banner {
    padding: 1.8rem;
    border-radius: 10px;
    margin-top: 2rem;
}

.kpi-strip { display: flex; gap: 1.5rem; margin-top: 2rem; margin-bottom: 2rem; }

.kpi-card {
    flex: 1;
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 1.5rem;
    border-radius: 8px;
}

.kpi-value { font-size: 2rem; font-weight: 700; }

.pricing-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 2rem;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.25s ease;
    height: 100%;
}

.pricing-card:hover {
    border-color: var(--primary);
    box-shadow: 0 6px 30px rgba(13,71,161,0.15);
    transform: translateY(-4px);
}

.pricing-selected {
    border: 2px solid var(--primary);
    box-shadow: 0 6px 40px rgba(13,71,161,0.25);
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
    step = max(1, value // 20 or 1)
    for i in range(0, value + 1, step):
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

        st.markdown(f"""
        <div class="exec-banner" style="border-left:6px solid {risk_color(rule_result['deterministic_label'])}; background:#1A202C;">
            <h3>Executive Risk Summary</h3>
            <p><strong>Risk Classification:</strong> {rule_result['deterministic_label']}</p>
            <p><strong>Governance Action:</strong> {governance_action}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1: animate_metric("Risk Exposure Index", rule_result["eligibility_score"])
        with col2: animate_metric("Failed Rules", len(rule_result["failed_rules"]))
        with col3: animate_metric("Passed Rules", len(rule_result["passed_rules"]))

        fig_gauge = go.Figure(go.Pie(
            values=[rule_result["eligibility_score"], 100-rule_result["eligibility_score"]],
            hole=0.7))
        fig_gauge.update_layout(showlegend=False, paper_bgcolor="#0F1419",
                                font=dict(color="white"), title="Risk Severity Gauge")
        st.plotly_chart(fig_gauge, use_container_width=True)

        fig_pie = px.pie(names=["Passed","Failed"],
                         values=[len(rule_result["passed_rules"]),
                                 len(rule_result["failed_rules"])],
                         hole=0.5)
        fig_pie.update_layout(paper_bgcolor="#0F1419", font_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)

        categories = list(confidence_vector.keys())
        values = list(confidence_vector.values())
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0,1], visible=True)),
                                showlegend=False, paper_bgcolor="#0F1419",
                                font=dict(color="white"))
        st.plotly_chart(fig_radar, use_container_width=True)

# -------------------------------------------------
# PRICING
# -------------------------------------------------
elif view == "Pricing":

    if "selected_plan" not in st.session_state:
        st.session_state.selected_plan = "Pro"

    def select_plan(plan):
        st.session_state.selected_plan = plan

    col1, col2, col3 = st.columns(3)

    for col, plan, desc in [
        (col1,"Free","Basic contract analysis<br>Limited audit visibility"),
        (col2,"Pro","Full XAI trace<br>AI Advisory Layer<br>PDF Risk Reports"),
        (col3,"Enterprise","API Access<br>Batch Processing<br>Compliance Dashboard")
    ]:
        with col:
            selected = "pricing-selected" if st.session_state.selected_plan==plan else ""
            if st.button(" ", key=f"{plan}_card", use_container_width=True):
                select_plan(plan)
            st.markdown(f"""
            <div class="pricing-card {selected}">
                <h3>{plan}</h3>
                {desc}<br><br>
                <strong>{'Most Popular' if plan=='Pro' else 'Select Plan →'}</strong>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:2rem; padding:1rem; background:#1A202C;
    border-radius:8px; border-left:4px solid var(--primary);">
        <strong>Selected Plan:</strong> {st.session_state.selected_plan}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Plan Comparison")

    st.table({
        "Feature": ["Risk Engine","XAI Trace","Governance Override","PDF Reports","API Access"],
        "Free":["✔","✖","✖","✖","✖"],
        "Pro":["✔","✔","✔","✔","✖"],
        "Enterprise":["✔","✔","✔","✔","✔"]
    })

    st.markdown("""
    <div style="margin-top:2rem; font-size:0.9rem; color:var(--text-secondary);">
    Demo Mode: Stripe integration placeholder.
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# ASSESSMENTS
# -------------------------------------------------
elif view == "Assessments":
    st.markdown('<div class="empty-state">No assessments yet.</div>', unsafe_allow_html=True)

# -------------------------------------------------
# DEVELOPER API
# -------------------------------------------------
elif view == "Developer API":
    st.code("""
curl -X POST https://api.nexusgovernance.ai/evaluate \\
-H "Content-Type: application/json" \\
-d '{"document_text": "Contract text here"}'
""")
