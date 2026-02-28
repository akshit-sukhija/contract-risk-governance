import streamlit as st
import re
from pathlib import Path
from typing import Optional
import PyPDF2
import plotly.graph_objects as go

from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.scoring.scoring import calculate_confidence_vector
from explainable_ai.core.trace.decision_trace import generate_decision_trace
from explainable_ai.core.explanation.ai_explainer import generate_ai_explanation

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Contract Risk Governance",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
POLICY_PATH = BASE_DIR / "explainable_ai" / "policies" / "rules.yaml"
rule_engine = RuleEngine(POLICY_PATH)

# -----------------------------
# DARK THEME
# -----------------------------
st.markdown("""
<style>
body {background-color: #0E0E0E; color: #E0E0E0;}
.block-container {padding: 2rem;}
.kpi-box {
    background: #151515;
    padding: 1rem;
    border-radius: 6px;
    border-top: 3px solid #007BFF;
}
.badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
}
.badge-high {background:#3A0E0E;color:#FF4B4B;}
.badge-medium {background:#3A2A0E;color:#FFA500;}
.badge-low {background:#0E3A1E;color:#00C853;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
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
                    lambda m: f"<span style='color:#FF4B4B;font-weight:bold'>{m.group(0)}</span>",
                    highlighted
                )
    return highlighted

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Nexus Architect")
view = st.sidebar.radio("Navigation", ["Dashboard", "Audit Trace"])

enable_ai = st.sidebar.checkbox("Enable AI Explanation")

# -----------------------------
# MAIN DASHBOARD
# -----------------------------
if view == "Dashboard":

    st.title("Contract Risk Governance Engine")

    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])
    document_text = st.text_area("Or Paste Contract Text", height=200)
    analyze = st.button("Run Risk Analysis")

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

        governance_decision = apply_governance_layer(
            deterministic_label=rule_result["deterministic_label"],
            confidence_vector=confidence_vector,
            crag_blocked=False,
        )

        trace = generate_decision_trace(
            input_data={"document_text": document_text},
            passed_rules=rule_result["passed_rules"],
            failed_rules=rule_result["failed_rules"],
            eligibility_score=rule_result["eligibility_score"],
            confidence_vector=confidence_vector,
            governance_decision=governance_decision,
        )

        ai_explanation: Optional[str] = None
        if enable_ai:
            ai_explanation = generate_ai_explanation(trace, governance_decision)

        # ---------------- EXECUTIVE SUMMARY ----------------
        st.markdown("## Executive Summary")

        col1, col2, col3 = st.columns(3)

        risk_level = rule_result["deterministic_label"]
        if risk_level == "HIGH_RISK":
            badge_class = "badge-high"
        elif risk_level == "MEDIUM_RISK":
            badge_class = "badge-medium"
        else:
            badge_class = "badge-low"

        col1.markdown(f"<div class='kpi-box'>Risk Score<br><h2>{rule_result['eligibility_score']}</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='kpi-box'>Governance Decision<br><h2>{governance_decision}</h2></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='kpi-box'>Risk Level<br><span class='badge {badge_class}'>{risk_level}</span></div>", unsafe_allow_html=True)

        # ---------------- RISK CHART ----------------
        st.markdown("## Risk Distribution")

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
                marker_color="#FF4B4B"
            ))

            fig.update_layout(
                plot_bgcolor="#0E0E0E",
                paper_bgcolor="#0E0E0E",
                font=dict(color="#E0E0E0")
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No risk clauses detected.")

        # ---------------- HIGHLIGHTED TEXT ----------------
        st.markdown("## Highlighted Contract")

        highlighted = highlight_keywords(
            document_text,
            rule_engine.rules,
            rule_result["failed_rules"]
        )

        st.markdown(
            f"<div style='padding:15px;border:1px solid #222;height:300px;overflow:auto'>{highlighted}</div>",
            unsafe_allow_html=True
        )

        # ---------------- PLAIN ENGLISH ----------------
        st.markdown("## Plain English Interpretation")

        if ai_explanation:
            st.write(ai_explanation)
        else:
            st.info("This contract contains risk clauses. Professional review recommended.")

        # ---------------- STORE TRACE ----------------
        st.session_state["trace"] = trace

# -----------------------------
# AUDIT TRACE VIEW
# -----------------------------
elif view == "Audit Trace":

    st.title("Governance Decision Trace")

    if "trace" not in st.session_state:
        st.info("Run analysis first.")
    else:
        for step in st.session_state["trace"]:
            st.json(step)
