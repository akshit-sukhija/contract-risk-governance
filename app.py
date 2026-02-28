import streamlit as st
import re
from pathlib import Path
from typing import Optional
import PyPDF2
import plotly.graph_objects as go
from datetime import datetime

from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.scoring.scoring import calculate_confidence_vector
from explainable_ai.core.trace.decision_trace import generate_decision_trace
from explainable_ai.core.explanation.ai_explainer import generate_ai_explanation

# ------------------------------------------------
# CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="Nexus Governance OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
POLICY_PATH = BASE_DIR / "explainable_ai" / "policies" / "rules.yaml"
rule_engine = RuleEngine(POLICY_PATH)

# ------------------------------------------------
# THEME
# ------------------------------------------------
st.markdown("""
<style>
body { background:#0F1117; color:#E5E7EB; }
.block-container { padding:2rem 3rem; }

.module { font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; color:#6B7280; margin-top:2rem; }

.kpi-box {
    background:#161B22;
    padding:1.3rem;
    border-radius:8px;
}

.kpi-value {
    font-size:2rem;
    font-weight:600;
}

.highlight-box {
    padding:1rem;
    border:1px solid #1F2937;
    border-radius:6px;
    max-height:350px;
    overflow:auto;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DEMO MODE BADGE
# ------------------------------------------------
st.markdown("""
<div style='position:fixed;top:20px;right:20px;
background:#1F2937;padding:6px 12px;
border-radius:20px;font-size:0.7rem;color:#9CA3AF;z-index:9999;'>
Demo Mode • Hackathon Build
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# HERO SECTION
# ------------------------------------------------
st.markdown("""
<div style='margin-bottom:2rem'>
    <div style='font-size:2.2rem;font-weight:700'>Nexus Governance OS</div>
    <div style='font-size:1rem;color:#9CA3AF;margin-top:6px'>
        Deterministic AI for Contract Risk Governance
    </div>
    <div style='font-size:0.85rem;color:#6B7280;margin-top:4px'>
        Built for the 2026 Legal-Tech Compliance Era
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='margin-bottom:2rem;color:#6B7280;font-size:0.8rem'>
✓ Deterministic Rule Engine  
✓ Governance Override Layer  
✓ Explainable Audit Trace  
✓ API-First Architecture
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# HELPERS
# ------------------------------------------------
def extract_pdf_text(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def highlight_keywords(text, rules, failed_rules):
    highlighted = text
    for rule in rules:
        if rule.id in failed_rules:
            for keyword in rule.keywords:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                highlighted = pattern.sub(
                    lambda m: f"<span style='color:#EF4444;font-weight:600'>{m.group(0)}</span>",
                    highlighted
                )
    return highlighted

def risk_color(level):
    return {
        "HIGH_RISK": "#EF4444",
        "MEDIUM_RISK": "#F59E0B",
        "LOW_RISK": "#10B981"
    }.get(level, "#3B82F6")

# ------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------
view = st.sidebar.radio(
    "Platform Navigation",
    ["Dashboard", "Assessments", "Developer API", "Pricing"]
)

enable_ai = st.sidebar.checkbox("Enable AI Advisory Layer")

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------
if view == "Dashboard":

    st.markdown("<div class='module'>Module 1 — Contract Ingestion</div>", unsafe_allow_html=True)

    st.markdown("<div style='background:#161B22;padding:1.5rem;border-radius:8px;margin-bottom:1.5rem'>", unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])
    document_text = st.text_area("Or Paste Contract Text", height=180)
    analyze = st.button("Create Risk Assessment")

    st.markdown("</div>", unsafe_allow_html=True)

    if analyze:

        if uploaded_pdf:
            document_text = extract_pdf_text(uploaded_pdf)

        if not document_text.strip():
            st.error("Contract text required.")
            st.stop()

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

        # Executive Risk Summary
        st.markdown(f"""
        <div style='
            background:#161B22;
            padding:1.5rem;
            border-radius:8px;
            border-left:6px solid {risk_color(rule_result["deterministic_label"])};
            margin-top:1.5rem;
        '>
            <div style='font-size:1.1rem;font-weight:600'>
                Executive Risk Summary
            </div>
            <div style='margin-top:8px'>
                <strong>Classification:</strong> {rule_result["deterministic_label"]}<br>
                <strong>Governance Action:</strong> {governance_action}<br>
                <strong>Risk Exposure Index:</strong> {rule_result["eligibility_score"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPI Strip
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<div class='kpi-box'>Risk Exposure Index</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-value'>{rule_result['eligibility_score']}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='kpi-box'>Risk Classification</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='kpi-value' style='color:{risk_color(rule_result['deterministic_label'])}'>"
                f"{rule_result['deterministic_label']}</div>",
                unsafe_allow_html=True
            )

        with col3:
            st.markdown("<div class='kpi-box'>Governance Action</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='kpi-value'>{governance_action}</div>", unsafe_allow_html=True)

# ------------------------------------------------
# ASSESSMENTS VIEW
# ------------------------------------------------
elif view == "Assessments":

    st.title("Recent Risk Assessments")

    if "history" not in st.session_state or not st.session_state.history:
        st.info("No assessments yet.")
    else:
        for item in st.session_state.history:
            color = risk_color(item["risk"])
            st.markdown(f"""
            <div style='background:#161B22;padding:1rem;border-radius:6px;
            margin-bottom:10px;border-left:6px solid {color}'>
            <strong>{item['time']}</strong><br>
            Risk: {item['risk']}<br>
            Score: {item['score']}<br>
            Governance: {item['decision']}
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------
# DEVELOPER API
# ------------------------------------------------
elif view == "Developer API":

    st.title("Nexus Governance API")
    st.markdown("API-First Architecture for Enterprise Integration")

    st.markdown("### POST /evaluate")

    st.code("""
curl -X POST https://api.nexusgovernance.ai/evaluate \\
-H "Content-Type: application/json" \\
-d '{
  "document_text": "Contract text here"
}'
""")

# ------------------------------------------------
# PRICING
# ------------------------------------------------
elif view == "Pricing":

    st.title("Platform Plans")

    st.markdown("""
    <div style='font-size:1rem;color:#9CA3AF;margin-bottom:1.5rem'>
    Flexible governance plans for legal teams and enterprises.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background:#161B22;padding:1.5rem;border-radius:8px'>
        <h3>Free</h3>
        Basic contract analysis<br>
        Limited audit visibility
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background:#1E293B;padding:1.5rem;border-radius:8px;
        border:2px solid #3B82F6;
        box-shadow:0 0 20px rgba(59,130,246,0.15);'>
        <h3>Pro</h3>
        Full XAI trace<br>
        AI Advisory Layer<br>
        PDF Risk Report
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background:#161B22;padding:1.5rem;border-radius:8px'>
        <h3>Enterprise</h3>
        API Access<br>
        Batch Processing<br>
        Compliance Dashboard
        </div>
        """, unsafe_allow_html=True)
