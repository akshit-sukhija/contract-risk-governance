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

.header-title { font-size:1.8rem; font-weight:700; }
.header-sub { font-size:0.85rem; color:#6B7280; margin-bottom:2rem; }

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
# HEADER
# ------------------------------------------------
st.markdown("<div class='header-title'>Nexus Governance OS</div>", unsafe_allow_html=True)
st.markdown("<div class='header-sub'>AI-Powered Deterministic Contract Risk Platform</div>", unsafe_allow_html=True)

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------
if view == "Dashboard":

    st.markdown("<div class='module'>Module 1 — Contract Ingestion</div>", unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])
    document_text = st.text_area("Or Paste Contract Text", height=180)
    analyze = st.button("Create Risk Assessment")

    if analyze:

        if uploaded_pdf:
            document_text = extract_pdf_text(uploaded_pdf)

        if not document_text.strip():
            st.error("Contract text required.")
            st.stop()

        # Risk Engine
        st.markdown("<div class='module'>Module 2 — Deterministic Risk Engine</div>", unsafe_allow_html=True)

        rule_result = rule_engine.evaluate(document_text)

        confidence_vector = calculate_confidence_vector(
            passed_rules=rule_result["passed_rules"],
            failed_rules=rule_result["failed_rules"],
            total_rules=len(rule_engine.rules),
            retrieval_similarity=1.0,
            data_completeness=1.0,
        )

        # Governance
        st.markdown("<div class='module'>Module 3 — Governance Layer</div>", unsafe_allow_html=True)

        governance_action = apply_governance_layer(
            deterministic_label=rule_result["deterministic_label"],
            confidence_vector=confidence_vector,
            crag_blocked=False,
        )

        # Portfolio Strip
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

        # Store in session history
        if "history" not in st.session_state:
            st.session_state.history = []

        st.session_state.history.insert(0, {
            "risk": rule_result["deterministic_label"],
            "score": rule_result["eligibility_score"],
            "decision": governance_action,
            "time": datetime.now().strftime("%H:%M:%S")
        })

        st.session_state.history = st.session_state.history[:5]

        # Visualization
        st.markdown("<div class='module'>Clause Risk Distribution</div>", unsafe_allow_html=True)

        failed = rule_result["failed_rules"]
        if failed:
            labels = []
            weights = []
            for rule in rule_engine.rules:
                if rule.id in failed:
                    labels.append(rule.id)
                    weights.append(rule.weight)

            fig = go.Figure(go.Bar(
                x=labels,
                y=weights,
                marker_color=risk_color(rule_result["deterministic_label"])
            ))

            fig.update_layout(
                height=300,
                plot_bgcolor="#0F1117",
                paper_bgcolor="#0F1117",
                font=dict(color="#E5E7EB")
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No material risk clauses detected.")

        # Highlight
        st.markdown("<div class='module'>Clause Highlighting</div>", unsafe_allow_html=True)

        highlighted = highlight_keywords(
            document_text,
            rule_engine.rules,
            rule_result["failed_rules"]
        )

        st.markdown(
            f"<div class='highlight-box'>{highlighted}</div>",
            unsafe_allow_html=True
        )

        # AI Advisory
        if enable_ai:
            st.markdown("<div class='module'>AI Advisory Layer (Non-Authoritative)</div>", unsafe_allow_html=True)

            trace = generate_decision_trace(
                input_data={"document_text": document_text},
                passed_rules=rule_result["passed_rules"],
                failed_rules=rule_result["failed_rules"],
                eligibility_score=rule_result["eligibility_score"],
                confidence_vector=confidence_vector,
                governance_decision=governance_action,
            )

            advisory = generate_ai_explanation(trace, governance_action)
            st.write(advisory)

# ------------------------------------------------
# ASSESSMENTS VIEW
# ------------------------------------------------
elif view == "Assessments":

    st.title("Recent Risk Assessments")

    if "history" not in st.session_state or not st.session_state.history:
        st.info("No assessments yet.")
    else:
        for item in st.session_state.history:
            st.markdown(f"""
            <div style='background:#161B22;padding:1rem;border-radius:6px;margin-bottom:10px'>
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

    st.markdown("### POST /evaluate")

    st.code("""
curl -X POST https://api.nexusgovernance.ai/evaluate \\
-H "Content-Type: application/json" \\
-d '{
  "document_text": "Contract text here"
}'
""")

    st.markdown("### Sample Response")

    st.json({
        "risk_classification": "HIGH_RISK",
        "risk_score": 55,
        "governance_action": "ESCALATE"
    })

# ------------------------------------------------
# PRICING
# ------------------------------------------------
elif view == "Pricing":

    st.title("Platform Plans")

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
        <div style='background:#1E293B;padding:1.5rem;border-radius:8px;border:2px solid #3B82F6'>
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
