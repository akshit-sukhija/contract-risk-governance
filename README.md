---

# Nexus Governance OS 🛡️

### *The Future of Auditable Decision Intelligence — Powered by AMD Ryzen™ AI*

---

## 📌 Project Overview

**Nexus Governance OS** is an enterprise-grade **Explainable Decision Intelligence System** designed for high-stakes legal and government auditing. Built on the proprietary **Nexus Architect engine**, it solves the "hallucination" and "black-box" problems of standard LLMs by implementing a **"Decision-First, Narrative-Second"** architecture.

Unlike probabilistic AI systems, Nexus Governance OS uses a hard-coded **Deterministic Rule Engine** to make final rulings, utilizing Local AI exclusively for human-readable explanations. This ensures that every decision is stable, auditable, and grounded in verifiable legal benchmarks.

---

## 🚀 Key Features

* **Deterministic Rule Engine**: Zero-hallucination core that evaluates documents against hard-coded compliance sets.
* **CRAG (Corrective RAG) Validator**: An intelligent retrieval gate that automatically rejects weak or low-similarity citations to prevent "blind RAG".
* **SHA-256 Integrity Hashing**: Generates unique document hashes to ensure source files remain untampered throughout the audit lifecycle.
* **Structured Confidence Vector**: A multi-dimensional trust metric that measures rule accuracy, data completeness, and retrieval similarity.
* **Governance Gate**: Automated triage mapping results to `APPROVED`, `REVIEW_REQUIRED`, or `ESCALATE` based on real-time risk thresholds.
* **Immutable JSON Audit Logs**: Comprehensive logs featuring rule versions, timestamps, and UUID traceability for total regulatory compliance.

---

## 🛠️ Technology Stack

* **Frontend**: Streamlit (Transparency Dashboard & Plotly risk visualization).
* **Backend**: FastAPI / Python (Document ingestion & Orchestration).
* **AI Layer**: FAISS (Local Vector Store) & ONNX Runtime.
* **Hardware Acceleration**: AMD Ryzen™ AI NPU via DirectML.
* **Security**: PyPDF2 (Hashing) & ReportLab (Verifiable PDF Reports).

---

## ⚡ AMD Ryzen™ AI Integration

This project is specifically optimized for **AMD Ryzen™ AI NPUs** to deliver a "Local-First" experience:

1. **NPU-Powered Explanations**: Uses **ONNX Runtime + DirectML** to offload the LLM explanation service to the dedicated AI engine, saving CPU cycles.
2. **Privacy-First Design**: Sensitive legal contracts are processed entirely on-device. No data ever leaves the local hardware, ensuring 100% data privacy.
3. **Ultra-Low Latency**: Hardware-accelerated vector retrieval and rule execution allow for real-time audits of 100+ page documents.

---

## 📂 Architecture

The system follows a modular **Five-Layer Architecture**:

1. **Client Layer**: Streamlit Dashboard for real-time audit monitoring.
2. **API Layer**: FastAPI service handling hashing and evaluation requests.
3. **Core Engine**: The deterministic rule set and confidence computation logic.
4. **AI Layer**: Hardware-accelerated explanation service (ONNX/DirectML).
5. **Data Layer**: Immutable logs and version-controlled rule configurations.

---

## 💻 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/akshit-sukhija/contract-risk-governance.git

# Navigate to project directory
cd contract-risk-governance

# Install dependencies
pip install -r requirements.txt

# Run the Transparency Dashboard
streamlit run app.py

```

---

## 🔮 Future Scope: GovScheme Setu

The Nexus Architect engine is vertically agnostic. Our next expansion involves scaling this deterministic logic into the G2C sector with **GovScheme Setu**—an intelligent government scholarship finder that automates eligibility verification with the same level of auditability.

---

## 👥 Team: Nexus Architects

* **Akshit Sukhija** (Team Leader)
* **Nexus Architects** - *AMD Slingshot Hackathon 2026*

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
