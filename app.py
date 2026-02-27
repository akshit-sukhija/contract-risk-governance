import streamlit as st
import re
from pathlib import Path
from typing import Optional
import PyPDF2
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.scoring.scoring import calculate_confidence_vector
from explainable_ai.core.trace.decision_trace import generate_decision_trace
from explainable_ai.core.explanation.ai_explainer import generate_ai_explanation

# ------------------------------
# Dark Professional Theme
# ------------------------------

st.set_page_config(page_title="Contract Risk Governance", layout="wide")

st.markdown("""
<style>
body {background-color: #0E1117; color: #FAFAFA;}
.block-container {padding-top: 2rem;}
h1, h2, h3 {color: #FFFFFF;}
</style>
""", unsafe_allow_html=True)

st.title("Contract Risk Governance Dashboard")
st.caption("Deterministic Explainable AI for Legal Risk Review")

BASE_DIR = Path(__file__).resolve().parent
POLICY_PATH = BASE_DIR / "explainable_ai" / "policies" / "rules.yaml"

rule_engine = RuleEngine(POLICY_PATH)

# ------------------------------
# PDF Text Extraction
# ------------------------------

def extract_pdf_text(uploaded_file) -> str:
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return ""

# ------------------------------
# Input Section
# ------------------------------

st.markdown("## Upload or Paste Contract")

col1, col2 = st.columns(2)

with col1:
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

with col2:
    document_text = st.text_area("Or paste contract text", height=200)

enable_ai = st.checkbox("Enable AI Explanation (Non-Authoritative)")
analyze = st.button("Analyze Contract")

# ------------------------------
# Processing
# ------------------------------

if analyze:

    if uploaded_pdf:
        document_text = extract_pdf_text(uploaded_pdf)

    if not document_text or not document_text.strip():
        st.error("Please provide contract text.")
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

    # ------------------------------
    # Executive Summary
    # ------------------------------

    st.markdown("---")
    st.markdown("## Executive Summary")

    st.write(f"**Risk Level:** {rule_result['deterministic_label']}")
    st.write(f"**Governance Decision:** {governance_decision}")
    st.write(f"**Risk Score:** {rule_result['eligibility_score']}")

    # ------------------------------
    # Risk Distribution Chart
    # ------------------------------

    st.markdown("## Risk Distribution")

    labels = []
    weights = []

    for rule in rule_engine.rules:
        if rule.id in rule_result["failed_rules"]:
            labels.append(rule.id)
            weights.append(rule.weight)

    if weights:
        fig = plt.figure()
        plt.bar(labels, weights)
        plt.xticks(rotation=45)
        plt.ylabel("Risk Weight")
        st.pyplot(fig)
    else:
        st.info("No risk clauses detected.")

    # ------------------------------
    # Clause Severity Scoring
    # ------------------------------

    st.markdown("## Clause Severity Breakdown")

    for rule in rule_engine.rules:
        if rule.id in rule_result["failed_rules"]:
            st.error(f"{rule.id} → Severity Weight: {rule.weight}")
        else:
            st.success(f"{rule.id} → No Risk Triggered")

    # ------------------------------
    # Highlighted Text
    # ------------------------------

    st.markdown("## Highlighted Legal Text")

    highlighted_text = document_text
    for rule_id in rule_result["failed_rules"]:
        rule = next((r for r in rule_engine.rules if r.id == rule_id), None)
        if rule:
            for keyword in rule.keywords:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                highlighted_text = pattern.sub(
                    lambda m: f"<span style='color:red;font-weight:bold'>{m.group(0)}</span>",
                    highlighted_text
                )

    st.markdown(
        f"<div style='padding:15px;border:1px solid #444;border-radius:6px;height:300px;overflow:auto'>{highlighted_text}</div>",
        unsafe_allow_html=True
    )

    # ------------------------------
    # Plain English Panel
    # ------------------------------

    st.markdown("## Plain English Interpretation")

    if ai_explanation:
        st.write(ai_explanation)
    else:
        st.info("This contract contains legally significant clauses that may require professional review.")

    # ------------------------------
    # Downloadable PDF Report
    # ------------------------------

    def generate_pdf_report():
        file_path = "risk_report.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Contract Risk Governance Report", styles["Heading1"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Risk Level: {rule_result['deterministic_label']}", styles["Normal"]))
        elements.append(Paragraph(f"Governance Decision: {governance_decision}", styles["Normal"]))
        elements.append(Paragraph(f"Risk Score: {rule_result['eligibility_score']}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Flagged Clauses:", styles["Heading2"]))

        for rule_id in rule_result["failed_rules"]:
            elements.append(Paragraph(rule_id, styles["Normal"]))

        doc.build(elements)
        return file_path

    report_file = generate_pdf_report()

    with open(report_file, "rb") as f:
        st.download_button(
            label="Download Risk Report (PDF)",
            data=f,
            file_name="Contract_Risk_Report.pdf",
            mime="application/pdf"
        )

    # ------------------------------
    # Technical Trace
    # ------------------------------

    with st.expander("Technical Decision Trace"):
        for step in trace:
            st.write(step)