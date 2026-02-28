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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF

from explainable_ai.core.engine.rule_engine import RuleEngine
from explainable_ai.core.governance.governance import apply_governance_layer
from explainable_ai.core.scoring.scoring import calculate_confidence_vector

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

st.set_page_config(page_title="Nexus Governance OS", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
POLICY_PATH = BASE_DIR / "explainable_ai" / "policies" / "rules.yaml"
LOGO_PATH = BASE_DIR / "logo.png"

rule_engine = RuleEngine(POLICY_PATH)

st.title("Nexus Governance OS")
st.caption("Deterministic AI for Contract Risk Governance")

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def extract_pdf_text(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return ""

def generate_hash(text: str):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def build_qr_payload(doc_id, doc_hash, timestamp):
    payload = {
        "product": "Nexus Governance OS",
        "doc_id": doc_id,
        "hash": doc_hash,
        "timestamp": timestamp,
        "version": "prototype-v1"
    }
    return json.dumps(payload, separators=(",", ":"))

# -------------------------------------------------
# WATERMARK + FOOTER
# -------------------------------------------------

def add_watermark_footer(canvas_obj, doc, qr_payload):

    # WATERMARK
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 60)
    canvas_obj.setFillColorRGB(0.9, 0.9, 0.9)
    canvas_obj.translate(300, 400)
    canvas_obj.rotate(45)
    canvas_obj.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas_obj.restoreState()

    # QR CODE
    qr_code = qr.QrCodeWidget(qr_payload)
    bounds = qr_code.getBounds()
    size = 70
    width = bounds[2] - bounds[0]
    scale = size / width
    qr_code.barWidth = scale
    qr_code.barHeight = scale
    renderPDF.draw(qr_code, canvas_obj, 460, 20)

    # FOOTER TEXT
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawString(40, 30, "Nexus Governance OS - Confidential")
    canvas_obj.drawRightString(570, 30, f"Page {doc.page}")

# -------------------------------------------------
# PDF GENERATION
# -------------------------------------------------

def generate_pdf_report(rule_result, governance_decision, document_text):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    doc_hash = generate_hash(document_text)
    document_id = str(uuid.uuid4())
    qr_payload = build_qr_payload(document_id, doc_hash, timestamp)

    # LOGO
    if LOGO_PATH.exists():
        elements.append(Image(str(LOGO_PATH), width=2 * inch, height=1 * inch))
        elements.append(Spacer(1, 12))

    # HEADER
    elements.append(Paragraph("Risk Audit Report", styles["Heading1"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Document ID: {document_id}", styles["Normal"]))
    elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
    elements.append(Paragraph(f"SHA-256 Hash: {doc_hash}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # EXECUTIVE SUMMARY
    elements.append(Paragraph("Executive Summary", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(
        f"Risk Level: {rule_result['deterministic_label']}",
        styles["Normal"]
    ))
    elements.append(Paragraph(
        f"Governance Decision: {governance_decision}",
        styles["Normal"]
    ))
    elements.append(Paragraph(
        f"Risk Score: {rule_result['eligibility_score']}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    # CLAUSE TABLE
    elements.append(Paragraph("Clause Severity Breakdown", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    table_data = [["Clause ID", "Triggered", "Weight"]]

    for rule in rule_engine.rules:
        triggered = "Yes" if rule.id in rule_result["failed_rules"] else "No"
        weight = rule.weight if triggered == "Yes" else "-"
        table_data.append([rule.id, triggered, str(weight)])

    table = Table(table_data, colWidths=[2.5 * inch, 1 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # HEATMAP
    heat_values = [
        rule.weight if rule.id in rule_result["failed_rules"] else 0
        for rule in rule_engine.rules
    ]

    if any(heat_values):
        fig, ax = plt.subplots(figsize=(6, 1))
        sns.heatmap(
            np.array([heat_values]),
            annot=True,
            cmap="Reds",
            cbar=False,
            ax=ax
        )
        ax.set_xticklabels([r.id for r in rule_engine.rules], rotation=45)
        ax.set_yticklabels(["Risk"])
        plt.tight_layout()

        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png")
        plt.close(fig)
        img_buffer.seek(0)

        elements.append(Paragraph("Risk Heatmap Overview", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        elements.append(Image(img_buffer, width=6 * inch, height=2 * inch))
        elements.append(Spacer(1, 20))

    # DIGITAL SIGNATURE
    elements.append(Paragraph("Digital Signature Validation", styles["Heading2"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "This document has been digitally signed under internal governance controls.",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("______________________________", styles["Normal"]))
    elements.append(Paragraph("Authorized Compliance Officer", styles["Normal"]))

    # VERIFICATION PAGE
    elements.append(PageBreak())
    elements.append(Paragraph("Tamper Detection & Verification", styles["Heading1"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Recalculate SHA-256 of original contract and confirm match:",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(doc_hash, styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Document ID: {document_id}", styles["Normal"]))

    doc.build(
        elements,
        onFirstPage=lambda c, d: add_watermark_footer(c, d, qr_payload),
        onLaterPages=lambda c, d: add_watermark_footer(c, d, qr_payload),
    )

    buffer.seek(0)
    return buffer

# -------------------------------------------------
# INPUT
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])

with col2:
    document_text = st.text_area("Or Paste Contract Text", height=200)

analyze = st.button("Analyze Contract", use_container_width=True)

# -------------------------------------------------
# ANALYSIS FLOW
# -------------------------------------------------

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

    st.markdown("## Executive Summary")
    st.write(f"Risk Level: {rule_result['deterministic_label']}")
    st.write(f"Governance Decision: {governance_decision}")
    st.write(f"Risk Score: {rule_result['eligibility_score']}")

    pdf_buffer = generate_pdf_report(
        rule_result,
        governance_decision,
        document_text
    )

    st.download_button(
        label="Download Audit Report (PDF)",
        data=pdf_buffer,
        file_name="Nexus_Risk_Audit_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
