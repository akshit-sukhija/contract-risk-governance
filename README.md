---

# Nexus Governance OS 🛡️

### *Deterministic Decision Intelligence for 2026's Regulatory Landscape — Optimized for AMD Ryzen™ AI*

---

## 📌 Project Overview

**Nexus Governance OS** is an enterprise-grade **Explainable Decision Intelligence System** built to handle high-stakes legal and government audits. Developed for the **AMD Slingshot Hackathon 2026**, the system addresses the "black-box" nature of traditional AI by using the **Nexus Architect engine**.

Our core philosophy is **"Decision-First, Narrative-Second."** Hard-coded deterministic rules make the final compliance ruling to ensure stability, while an LLM is used only to generate human-readable explanations.

---

## 🚀 Core Features

* **Deterministic Rule Core**: Executes logic-based legal audits independently of AI to eliminate hallucinations.
* **CRAG (Corrective RAG) Validator**: An intelligent retrieval gate that rejects low-quality or irrelevant citations to ensure grounded accuracy.
* **SHA-256 Integrity Hashing**: Automatically generates hashes for every uploaded document to ensure the audit trail remains untampered.
* **Structured Confidence Vector**: Provides a multi-dimensional trust score based on rule matches, data completeness, and retrieval quality.
* **Governance Gate**: Automated triage that maps decisions to `APPROVED`, `REVIEW_REQUIRED`, or `ESCALATE` statuses.
* **Immutable JSON Audit Logs**: Features UUID traceability and rule-versioning for full regulatory compliance.

---

## 🛠️ Technology Stack

*  **UI/Frontend**: Streamlit (Transparency Dashboard & Risk Visualizations).


*  **Backend Orchestration**: FastAPI (High-concurrency document processing).


*  **Deterministic Logic**: Custom Python-based Rule Engine utilizing YAML configurations.


*  **AI Layer**: FAISS (Local Vector Store) & LLM Explanation Service.


*  **Inference Engine**: **ONNX Runtime + DirectML** for hardware acceleration.

---

## ⚡ AMD Ryzen™ AI Synergy

Nexus Governance OS is purpose-built to leverage **AMD hardware** for privacy and performance:

1. **Local Inference**: Processes sensitive legal contracts entirely on-device, ensuring no data leakage to cloud APIs.
2. **NPU Acceleration**: Offloads LLM explanation tasks to the dedicated **AMD Ryzen™ AI NPU**, significantly reducing CPU load and power consumption.
3. **Low Latency**: Utilizes **DirectML** to provide near-instant decision support even for complex, high-density documents.

---

## 📂 System Architecture
*Figure 1: Five-Layer Deterministic Decision Intelligence Architecture optimized for AMD Ryzen™ AI.*

> **📖 Technical Documentation**: Full system architecture and NPU optimization guides are included within this repository for developer review.

---

## 💻 Quick Start

```bash
# Clone the repository
git clone https://github.com/akshit-sukhija/contract-risk-governance.git

# Install enterprise dependencies
pip install -r requirements.txt

# Launch the Transparency Dashboard
streamlit run app.py

```

---

## 🔮 Future Scope: GovScheme Setu

The Nexus Architect engine is vertically agnostic. We plan to scale this logic into the G2C sector with **GovScheme Setu**—a government scholarship finder that uses the same deterministic rules to automate eligibility matching with absolute transparency.

---

## 👥 Team: Nexus Architects

* **Akshit Sukhija** - Team Leader
* **Nexus Architects** - *AMD Slingshot Hackathon 2026 Submission*

---

## 📄 License

This project is licensed under the **MIT License**. It is open-source and free to use for further innovation in the field of Explainable AI.

---
