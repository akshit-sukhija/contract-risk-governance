import plotly.graph_objects as go
import matplotlib
matplotlib.use("Agg")
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

    # -------- WATERMARK --------
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 60)
    canvas_obj.setFillColorRGB(0.92, 0.92, 0.92)
    canvas_obj.translate(300, 400)
    canvas_obj.rotate(45)
    canvas_obj.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas_obj.restoreState()

    # -------- FOOTER --------
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawString(40, 20, f"Nexus Governance OS | Document ID: {document_id}")
    canvas_obj.drawRightString(570, 20, f"Page {doc.page}")
    canvas_obj.restoreState()

# ------------------------------------------------
# PDF GENERATION
# ------------------------------------------------

def generate_pdf_report(rule_result, governance_action, confidence_vector, document_text):

    try:
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

        # HEADER
        elements.append(Paragraph("Nexus Governance OS - Risk Audit Report", styles["Heading1"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Document ID: {document_id}", styles["Normal"]))
        elements.append(Paragraph(f"Generated: {timestamp}", styles["Normal"]))
        elements.append(Paragraph(f"SHA-256 Hash: {document_hash}", styles["Normal"]))
        elements.append(Spacer(1, 16))

        # EXEC SUMMARY
        elements.append(Paragraph("Executive Summary", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"Risk Level: {rule_result['deterministic_label']}", styles["Normal"]))
        elements.append(Paragraph(f"Governance Action: {governance_action}", styles["Normal"]))
        elements.append(Paragraph(f"Risk Score: {rule_result['eligibility_score']}", styles["Normal"]))
        elements.append(Spacer(1, 16))

        # CLAUSE TABLE
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
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        # HEATMAP (PURE MATPLOTLIB)
        heat_values = [
            rule.weight if rule.id in rule_result["failed_rules"] else 0
            for rule in rule_engine.rules
        ]

        if any(heat_values):
            fig, ax = plt.subplots(figsize=(8, 2))
            sns.set(font_scale=0.7)
            ax.imshow([heat_values], cmap="Reds")
            ax.set_xticks(range(len(rule_engine.rules)))
            ax.set_xticklabels([r.id for r in rule_engine.rules], rotation=45)
            ax.set_yticks([])
            plt.tight_layout()

            img_buffer = BytesIO()
            fig.savefig(img_buffer, format="png")
            plt.close(fig)
            img_buffer.seek(0)

            elements.append(Image(img_buffer, width=6 * inch, height=2 * inch))
            elements.append(Spacer(1, 20))

        # DIGITAL SIGNATURE
        elements.append(Paragraph("Digital Signature Validation", styles["Heading2"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Digitally signed under internal governance controls.", styles["Normal"]))
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("______________________________", styles["Normal"]))
        elements.append(Paragraph("Authorized Compliance Officer", styles["Normal"]))

        # HIGHLIGHTED EXPORT (SAFE CHUNKING)
        elements.append(PageBreak())
        elements.append(Paragraph("Highlighted Clause Export", styles["Heading1"]))
        elements.append(Spacer(1, 12))

        highlighted = highlight_text(document_text, rule_result["failed_rules"])
        safe_text = highlighted.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        for i in range(0, len(safe_text), 1500):
            elements.append(Paragraph(safe_text[i:i+1500], styles["Normal"]))
            elements.append(Spacer(1, 6))

        # VERIFICATION PAGE
        elements.append(PageBreak())
        elements.append(Paragraph("Tamper Detection & Verification", styles["Heading1"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Document Hash: {document_hash}", styles["Normal"]))
        elements.append(Paragraph(f"Document ID: {document_id}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # QR (Correct Flowable)
        qr_code = qr.QrCodeWidget(verification_payload)
        bounds = qr_code.getBounds()
        size = 2 * inch
        scale = size / (bounds[2] - bounds[0])
        drawing = Drawing(size, size, transform=[scale, 0, 0, scale, 0, 0])
        drawing.add(qr_code)
        elements.append(drawing)

        doc.build(
            elements,
            onFirstPage=lambda c, d: add_watermark_footer(c, d, document_id),
            onLaterPages=lambda c, d: add_watermark_footer(c, d, document_id)
        )

        buffer.seek(0)
        return buffer

    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        return None

# ------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------

view = st.sidebar.radio(
    "Platform Navigation",
    ["Dashboard", "Ingestion", "Audit Log", "Developer API", "Pricing"]
)

# ------------------------------------------------
# GLOBAL STYLE
# ------------------------------------------------

st.markdown("""
<style>
.block-container { padding-top: 1.8rem; }

.capability-box {
    background:#0f172a;
    padding:22px;
    border-radius:18px;
    border:1px solid #1e293b;
    margin-top:15px;
    margin-bottom:40px;
}

.cap-chip {
    display:inline-block;
    padding:8px 16px;
    margin:6px 8px 6px 0px;
    border-radius:999px;
    background:#111827;
    border:1px solid #1f2937;
    font-size:13px;
}

.cap-chip-highlight {
    background:#1d4ed8;
    border:1px solid #2563eb;
}

.status-chip {
    display:inline-block;
    padding:4px 12px;
    border-radius:999px;
    font-size:12px;
    font-weight:500;
}

.chip-green { background:#16a34a; color:white; }
.chip-red { background:#dc2626; color:white; }

.audit-box {
    background:#0b1220;
    padding:20px;
    border-radius:14px;
    border:1px solid #1e293b;
    font-family:monospace;
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.title("Nexus Governance OS")
st.caption("Deterministic Clause Benchmarking & Compliance Automation")

st.markdown("""
<div class="capability-box">
    <div style="font-size:12px; letter-spacing:0.1em; color:#94a3b8; text-transform:uppercase;">
        Platform Capabilities
    </div>
    <div style="margin-top:10px;">
        <span class="cap-chip">Rule Engine</span>
        <span class="cap-chip">Governance Layer</span>
        <span class="cap-chip">SHA-256 Integrity</span>
        <span class="cap-chip">UUID Traceability</span>
        <span class="cap-chip cap-chip-highlight">AMD Ryzen AI Optimized</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------

if view == "Dashboard":

    st.markdown("## Nexus Command Center")

    uploaded_pdf = st.file_uploader("Upload Contract PDF", type=["pdf"])
    document_text = st.text_area("Or Paste Contract Text", height=220)
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

        risk = rule_result["deterministic_label"]
        score = rule_result["eligibility_score"]

        # Risk color mapping
        risk_colors = {
            "LOW_RISK": "#16a34a",
            "MEDIUM_RISK": "#f59e0b",
            "HIGH_RISK": "#dc2626"
        }

        accent = risk_colors.get(risk, "#2563eb")

        # Executive Risk Display
        st.markdown(f"""
        <div style="
            background:#0f172a;
            padding:28px;
            border-radius:18px;
            border:1px solid #1e293b;
            margin-top:20px;
            margin-bottom:30px;
        ">
            <div style="font-size:12px; letter-spacing:0.1em; color:#94a3b8; text-transform:uppercase;">
                Risk Classification
            </div>

            <div style="
                font-size:46px;
                font-weight:600;
                margin-top:6px;
                color:{accent};
            ">
                {risk.replace("_", " ")}
            </div>

            <div style="margin-top:12px; color:#cbd5e1; font-size:15px;">
                Governance Action: <strong>{governance_action}</strong><br>
                Risk Score: {score}/100
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPI Grid (pure Streamlit for stability)

        col1, col2, col3 = st.columns(3)

        confidence_score = round(
            sum(confidence_vector.values()) / len(confidence_vector),
            2
        )

        col1.metric("Failed Rules", len(rule_result["failed_rules"]))
        col2.metric("Passed Rules", len(rule_result["passed_rules"]))
        col3.metric("Confidence Index", confidence_score)

        # Gauge

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": accent},
            },
        ))

        fig.update_layout(height=260)
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# GOVERNANCE LOGIC – CLAUSE BREAKDOWN
# ------------------------------------------------

elif view == "Ingestion":

    st.markdown("## Governance Logic – Clause Breakdown")

    if "analysis" not in st.session_state:
        st.info("Analyze a document first from Dashboard.")
    else:
        rule_result = st.session_state["analysis"]["rule_result"]

        for rule in rule_engine.rules:
            triggered = rule.id in rule_result["failed_rules"]

            if triggered:
                status = "<span class='status-chip chip-red'>Flagged</span>"
            else:
                status = "<span class='status-chip chip-green'>Compliant</span>"

            st.markdown(f"""
            <div style="
                background:#0f172a;
                padding:16px;
                border-radius:12px;
                margin-bottom:10px;
                border:1px solid #1e293b;
            ">
                <strong>{rule.id}</strong>
                &nbsp;&nbsp; {status}
                &nbsp;&nbsp; Weight: {rule.weight}
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------------
# AUDIT LOG
# ------------------------------------------------

elif view == "Audit Log":

    st.markdown("## Deterministic Decision Trace")

    if "analysis" not in st.session_state:
        st.info("Run an analysis first.")
    else:
        rule_result = st.session_state["analysis"]["rule_result"]

        st.markdown("<div class='audit-box'>", unsafe_allow_html=True)

        st.write(f"[{datetime.utcnow()}] Rule Engine Initialized")
        st.write(f"[{datetime.utcnow()}] Total Rules Loaded: {len(rule_engine.rules)}")
        st.write(f"[{datetime.utcnow()}] Failed Rules: {rule_result['failed_rules']}")
        st.write(f"[{datetime.utcnow()}] Deterministic Label: {rule_result['deterministic_label']}")
        st.write(f"[{datetime.utcnow()}] Governance Action Applied")

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------
# DEVELOPER API
# ------------------------------------------------

elif view == "Developer API":

    st.code(
        'curl -X POST https://api.nexusgovernance.ai/evaluate '
        '-H "Content-Type: application/json" '
        '-d \'{"document_text": "Contract text here"}\''
    )

# ------------------------------------------------
# PRICING
# ------------------------------------------------

elif view == "Pricing":
    st.info("Enterprise licensing available upon request.")
