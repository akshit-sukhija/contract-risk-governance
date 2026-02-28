import streamlit as st
import re
import hashlib
from pathlib import Path
from io import BytesIO
from datetime import datetime

import PyPDF2
import plotly.graph_objects as go
import plotly.express as px
import time

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.scoring.scoring import calculate_confidence_vector

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
# HELPERS
# ------------------------------------------------

def extract_pdf_text(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def generate_hash(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def highlight_text(text, failed_rules):
    highlighted = text
    for rule in rule_engine.rules:
        if rule.id in failed_rules:
            for keyword in rule.keywords:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                highlighted = pattern.sub(
                    lambda m: f"[FLAGGED:{m.group(0)}]",
                    highlighted
                )
    return highlighted

# ------------------------------------------------
# PDF GENERATION
# ------------------------------------------------

def generate_pdf_report(rule_result, governance_action, confidence_vector, document_text):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    document_hash = generate_hash(document_text)

    # HEADER
    elements.append(Paragraph("Nexus Governance OS - Risk Audit Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
    elements.append(Paragraph(f"Document Hash (SHA-256): {document_hash}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # EXECUTIVE SUMMARY
    elements.append(Paragraph("Executive Summary", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f"Risk Level: {rule_result['deterministic_label']}", styles["Normal"]))
    elements.append(Paragraph(f"Governance Action: {governance_action}", styles["Normal"]))
    elements.append(Paragraph(f"Risk Score: {rule_result['eligibility_score']}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # GOVERNANCE AUDIT TRAIL
    elements.append(Paragraph("Governance Audit Trail", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f"Deterministic Label: {rule_result['deterministic_label']}", styles["Normal"]))
    elements.append(Paragraph(f"Confidence Vector: {confidence_vector}", styles["Normal"]))
    elements.append(Paragraph("CRAG Blocked: False", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # CLAUSE TABLE
    elements.append(Paragraph("Clause Severity Breakdown", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    table_data = [["Clause ID", "Triggered", "Weight"]]

    for rule in rule_engine.rules:
        triggered = "Yes" if rule.id in rule_result["failed_rules"] else "No"
        weight = rule.weight if triggered == "Yes" else "-"
        table_data.append([rule.id, triggered, str(weight)])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # HIGHLIGHTED CLAUSES EXPORT
    elements.append(PageBreak())
    elements.append(Paragraph("Highlighted Clause Export", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    highlighted_version = highlight_text(document_text, rule_result["failed_rules"])

    elements.append(Paragraph(highlighted_version[:4000], styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------

view = st.sidebar.radio(
    "Platform Navigation",
    ["Dashboard", "Assessments", "Developer API", "Pricing"]
)

# ------------------------------------------------
# HERO
# ------------------------------------------------

st.title("Nexus Governance OS")
st.caption("Deterministic AI for Contract Risk Governance")

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------

if view == "Dashboard":

    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])
    document_text = st.text_area("Or Paste Contract Text", height=200)

    analyze_clicked = st.button("Analyze Contract", use_container_width=True)

    if analyze_clicked:

        if uploaded_pdf:
            document_text = extract_pdf_text(uploaded_pdf)

        if not document_text.strip():
            st.warning("Contract text required.")
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

        st.session_state["analysis"] = {
            "rule_result": rule_result,
            "governance_action": governance_action,
            "confidence_vector": confidence_vector,
            "document_text": document_text
        }

    if "analysis" in st.session_state:

        data = st.session_state["analysis"]
        rule_result = data["rule_result"]
        governance_action = data["governance_action"]
        confidence_vector = data["confidence_vector"]
        document_text = data["document_text"]

        st.subheader("Executive Summary")
        st.write("Risk Level:", rule_result["deterministic_label"])
        st.write("Governance Action:", governance_action)
        st.write("Risk Score:", rule_result["eligibility_score"])

        pdf_buffer = generate_pdf_report(
            rule_result,
            governance_action,
            confidence_vector,
            document_text
        )

        st.download_button(
            label="Download Risk Report (PDF)",
            data=pdf_buffer,
            file_name="Nexus_Risk_Audit_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ------------------------------------------------
# OTHER PAGES
# ------------------------------------------------

elif view == "Assessments":
    st.info("No assessments yet.")

elif view == "Developer API":
    st.code("""
curl -X POST https://api.nexusgovernance.ai/evaluate \\
-H "Content-Type: application/json" \\
-d '{"document_text": "Contract text here"}'
""")

elif view == "Pricing":
    st.info("Pricing plans coming soon.")
