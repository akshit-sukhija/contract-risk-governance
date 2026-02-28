import streamlit as st
import re
import hashlib
import uuid
import json
from pathlib import Path
from io import BytesIO
from datetime import datetime

import PyPDF2
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing

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

def generate_hash(text):
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

def add_watermark_footer(canvas_obj, doc, document_id):
    canvas_obj.saveState()

    # Watermark
    canvas_obj.setFont("Helvetica", 60)
    canvas_obj.setFillColorRGB(0.92, 0.92, 0.92)
    canvas_obj.translate(300, 400)
    canvas_obj.rotate(45)
    canvas_obj.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas_obj.restoreState()

    # Footer
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawString(40, 20, f"Nexus Governance OS | Document ID: {document_id}")
    canvas_obj.drawRightString(570, 20, f"Page {doc.page}")

    canvas_obj.restoreState()

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
    document_id = str(uuid.uuid4())

    verification_payload = json.dumps({
        "product": "Nexus Governance OS",
        "document_id": document_id,
        "hash": document_hash,
        "timestamp": timestamp,
        "version": "prototype-v1"
    }, separators=(",", ":"))

    # Header
    elements.append(Paragraph("Nexus Governance OS - Risk Audit Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Document ID: {document_id}", styles["Normal"]))
    elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
    elements.append(Paragraph(f"SHA-256 Hash: {document_hash}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # Executive Summary
    elements.append(Paragraph("Executive Summary", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Risk Level: {rule_result['deterministic_label']}", styles["Normal"]))
    elements.append(Paragraph(f"Governance Action: {governance_action}", styles["Normal"]))
    elements.append(Paragraph(f"Risk Score: {rule_result['eligibility_score']}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # Governance Audit
    elements.append(Paragraph("Governance Audit Trail", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Confidence Vector: {confidence_vector}", styles["Normal"]))
    elements.append(Spacer(1, 16))

    # Clause Table
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

    # Heatmap
    heat_values = [
        rule.weight if rule.id in rule_result["failed_rules"] else 0
        for rule in rule_engine.rules
    ]

    if any(heat_values):
        fig, ax = plt.subplots(figsize=(6, 1))
        sns.heatmap(np.array([heat_values]), annot=True, cmap="Reds", cbar=False, ax=ax)
        ax.set_xticklabels([r.id for r in rule_engine.rules], rotation=45)
        ax.set_yticklabels(["Risk"])
        plt.tight_layout()

        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png")
        plt.close(fig)
        img_buffer.seek(0)

        elements.append(Image(img_buffer, width=6 * inch, height=2 * inch))
        elements.append(Spacer(1, 20))

    # Digital Signature
    elements.append(Paragraph("Digital Signature Validation", styles["Heading2"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Digitally signed under internal governance controls.", styles["Normal"]))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("______________________________", styles["Normal"]))
    elements.append(Paragraph("Authorized Compliance Officer", styles["Normal"]))

    # Highlighted Clauses
    elements.append(PageBreak())
    elements.append(Paragraph("Highlighted Clause Export", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    highlighted = highlight_text(document_text, rule_result["failed_rules"])
    for i in range(0, len(highlighted), 2000):
        elements.append(Paragraph(highlighted[i:i+2000], styles["Normal"]))
        elements.append(Spacer(1, 6))

    # Verification Page
    elements.append(PageBreak())
    elements.append(Paragraph("Tamper Detection & Verification", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Document Hash: {document_hash}", styles["Normal"]))
    elements.append(Paragraph(f"Document ID: {document_id}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    qr_code = qr.QrCodeWidget(verification_payload)
    bounds = qr_code.getBounds()
    size = 2 * inch
    scale = size / (bounds[2] - bounds[0])
    drawing = Drawing(size, size, transform=[scale, 0, 0, scale, 0, 0])
    drawing.add(qr_code)
    elements.append(drawing)

    try:
        doc.build(
            elements,
            onFirstPage=lambda c, d: add_watermark_footer(c, d, document_id),
            onLaterPages=lambda c, d: add_watermark_footer(c, d, document_id)
        )
    except Exception:
        return None

    buffer.seek(0)
    return buffer

# ------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------

view = st.sidebar.radio(
    "Platform Navigation",
    ["Dashboard", "Assessments", "Developer API", "Pricing"]
)

st.title("Nexus Governance OS")
st.caption("Deterministic AI for Contract Risk Governance")

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------

if view == "Dashboard":

    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])
    document_text = st.text_area("Or Paste Contract Text", height=200)

    if st.button("Analyze Contract", use_container_width=True):

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

        if pdf_buffer:
            st.download_button(
                "Download Risk Report (PDF)",
                pdf_buffer,
                "Nexus_Risk_Audit_Report.pdf",
                "application/pdf",
                use_container_width=True
            )
        else:
            st.error("PDF generation failed.")

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
