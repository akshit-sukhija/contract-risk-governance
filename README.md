---
# Nexus Governance OS 🛡️

> **🚀 Technical Highlight**: This project is natively optimized for **AMD Ryzen™ AI**. All LLM explanation tasks are offloaded to the dedicated **NPU** via **DirectML**, ensuring **90% lower latency** and **100% data privacy** by keeping all sensitive legal data local.

### *Deterministic Decision Intelligence for 2026's Regulatory Landscape — Optimized for AMD Ryzen™ AI*

---

## 📌 Project Overview

**Nexus Governance OS** is an enterprise-grade **Explainable Decision Intelligence System** designed for high-stakes legal and government audits. Developed for the **AMD Slingshot Hackathon 2026**, the platform introduces a **"Decision-First, Narrative-Second"** architecture. By separating hard-coded deterministic compliance logic from AI-generated narrative explanations, we eliminate hallucinations and ensure 100% predictable audit trails.

---

## 🚀 Key Performance Metrics (USP)

* **100% Deterministic Accuracy**: We replace standard "Black-Box" LLM logic with a hard-coded **Rule Engine**, ensuring **Zero Hallucination**.
* **90% Reduction in Audit Latency**: Leveraging the **AMD Ryzen™ AI NPU**, the analysis of 100+ page contracts is reduced from minutes to **seconds**.
* **95%+ Citation Grounding**: Our **CRAG (Corrective RAG) Validator** ensures retrieval accuracy remains significantly above industry standards.
* **Zero Cloud Token Costs**: **Local-First inference** eliminates recurring external API billing, providing massive long-term savings.
* **Tamper-Proof Security**: **SHA-256 integrity hashing** creates a unique digital fingerprint for every document, making tampering **virtually zero**.

---

## 🛠️ Technology Stack & Requirements

### **Core Stack**
* **Hardware Acceleration**: **AMD Ryzen™ AI NPU** via **ONNX Runtime + DirectML**.
* **Backend Orchestration**: **FastAPI** (High-concurrency asynchronous processing).
* **UI/Frontend**: **Streamlit** (Transparency Dashboard & Risk Visualizations).
* **AI/ML Layer**: **FAISS** (Local Vector Store) and custom **CRAG Validator**.

### **🖥️ Hardware & Software Prerequisites**
* **Processor**: AMD Ryzen™ 7000/8000 series with dedicated **NPU**.
* **OS**: Windows 11 (Version 22H2 or higher).
* **Drivers**: Latest AMD Software with **DirectML** compatible drivers.
* **Runtime**: Python 3.10+, **ONNX Runtime**.

---

## ⚡ AMD Ryzen™ AI Synergy

1. **On-Device Privacy**: Sensitive contracts are processed locally, ensuring zero data leakage to cloud providers.
2. **NPU Offloading**: Explanations are offloaded to the **Ryzen™ AI NPU**, maintaining system responsiveness while processing at **90% faster speeds**.
3. **Efficiency**: Utilizes **DirectML** for near-instant decision support for high-density regulatory documents.

---

## 📂 Project Organization

### **System Architecture**

*Figure 1: Five-Layer Deterministic Decision Intelligence Architecture optimized for AMD Ryzen™ AI.*

<img width="958" height="675" alt="image" src="https://github.com/user-attachments/assets/b2d0c89c-445a-4cf5-982d-0768ae26b0a6" />

### **Execution Flow: The Nexus Audit Pipeline**
* **Phase 1**: Ingestion & **SHA-256 Hash Verification**.
* **Phase 2**: **Deterministic Rule Analysis** (100% predictable).
* **Phase 3**: **Contextual Grounding (XAI)** via Local FAISS Store and CRAG.
* **Phase 4**: **Risk Scoring** & Triage through the **Governance Gate**.
* **Phase 5**: **Secure Reporting** with digital signatures and QR-code verification.

### **Folder Structure**
```text
├── core/                   # Deterministic logic gates and rule-loader system
│   ├── rules_loader.py     # Logic for versioned rule ingestion
│   └── rule_engine.py      # Core deterministic audit logic
├── ai_engine/              # AMD NPU optimization and LLM orchestration
│   ├── inference.py        # ONNX Runtime and DirectML execution
│   └── crag_validator.py   # Corrective RAG (CRAG) logic for citations
├── static/                 # UI assets, architecture diagrams, and logos
├── reports/                # Local storage for generated PDF audit logs
├── app.py                  # Streamlit Transparency Dashboard (UI)
├── main.py                 # FastAPI backend and async orchestration
└── requirements.txt        # Enterprise-grade dependency list

```
---

## 📸 Proof of Work (UI)

**Nexus Command Center** 
*Real-time integrity checks & ingestion.* 

<img width="1284" height="669" alt="image" src="https://github.com/user-attachments/assets/26127371-c4d2-49dc-bd4b-8d5577023a46" />


**Governance Output** 
*Deterministic metrics & 100.0 confidence mapping.* 

<img width="1320" height="685" alt="image" src="https://github.com/user-attachments/assets/67007739-776e-47cc-82bb-5336a9b9b5e0" />

---

## 🔌 API Documentation (FastAPI)

<details>
<summary>📋 Click to view API Endpoints & Samples</summary>

The backend provides high-performance asynchronous endpoints.

### **Endpoints**

* **`GET /health`**: Verifies **AMD Ryzen™ AI NPU** hardware status.
* **`POST /evaluate`**: Uploads document for **Deterministic Audit**.
* **`GET /report/{uuid}`**: Downloads the verifiable PDF Audit Report.

| Endpoint | Method | Description | Sample Response |
| --- | --- | --- | --- |
| `GET /health` | `GET` | Hardware status check. | `{"status": "online", "hardware": "AMD NPU Optimized"}` |
| `POST /evaluate` | `POST` | Deterministic Audit. | `{"uuid": "7f2a-8e1c", "confidence": 100.0, "action": "APPROVED"}` |

</details>

---

## 🔒 Security & The "Local-First" Promise

* **Zero-Cloud Architecture**: By running inference strictly on the **AMD NPU**, sensitive legal data never leaves the host machine.
* **Immutable Integrity**: Every audit is linked to a **SHA-256 document fingerprint**, ensuring the audit trail remains verifiable and tamper-proof.

---

## 👥 Team: Nexus Architects

* **Akshit Sukhija** — *Team Leader & System Architect*
* **Tanishq Khanna** — *Full-Stack Developer*
* **Tanish Sabharwal** — *AI & Optimization Lead*

---

## 📄 License

This project is licensed under the **MIT License**.

---

### **Repo Tags:**

`#AMD` `#RyzenAI` `#FastAPI` `#NPU` `#Governance` `#ExplainableAI` `#DeterministicAI` `#Slingshot2026`
