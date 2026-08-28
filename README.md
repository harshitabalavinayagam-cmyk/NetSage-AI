# 🌐 NetSage AI

## Evidence-First Network Troubleshooting Copilot

NetSage AI is an intelligent network troubleshooting application that analyzes network symptoms, topology information, and command output to identify possible network issues.

The system follows an evidence-first approach by combining deterministic rule-based detection, evidence quality analysis, confidence scoring, risk assessment, network health scoring, explainable diagnosis, and human review.

---

## 🎯 Problem Statement

Network troubleshooting often requires administrators to manually analyze multiple sources of information such as symptoms, topology details, and command outputs. This process can be time-consuming and may lead to inconsistent diagnosis, especially when the available evidence is incomplete.

NetSage AI assists users by analyzing available network evidence and providing an explainable troubleshooting recommendation. The system is designed to support human decision-making rather than automatically modifying network configurations.

---

## ✨ Key Features

- 📂 Analyze existing network troubleshooting cases
- ✨ Analyze custom network cases
- ⚡ Quick demo scenarios for project demonstrations
- 🧠 Rule-based network fault detection
- 📊 Diagnosis confidence scoring
- 🔬 Intelligent evidence quality analysis
- 🚦 Diagnosis risk level assessment
- 🏥 Network health score
- 🧭 Troubleshooting decision path
- 🔍 Explainable AI diagnosis transparency
- 🛠️ Recommended troubleshooting steps
- 👤 Human review and feedback
- 📊 Human review analytics
- 📈 Diagnosis history and learning insights
- 📄 Professional diagnostic report generation
- 🛡️ Responsible AI safeguards

---

## 🧠 Supported Network Concepts

The system can analyze network cases related to:

- VLAN
- DHCP
- DNS
- Routing
- Switching
- IP Addressing
- WiFi
- Firewall

Additional concepts can also be analyzed through the custom case option.

---

## 🏗️ System Workflow

```text
Network Case
     ↓
Evidence Collection
     ↓
Rule-Based Analysis
     ↓
Diagnosis + Confidence
     ↓
Evidence Quality Analysis
     ↓
Risk Assessment
     ↓
Network Health Score
     ↓
Explainable Diagnosis
     ↓
Troubleshooting Recommendations
     ↓
Human Review
     ↓
Analytics and Learning History
```

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- CSV-based data storage

---

## 📂 Project Structure

```text
NetSage-AI/
│
├── app.py
├── generate_cases.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── cases.csv
│   ├── diagnosis_history.csv
│   └── review_log.csv
│
├── docs/
│   └── responsible_ai.md
│
├── engine/
│   ├── __init__.py
│   ├── diagnosis_engine.py
│   └── rule_checker.py
│
├── outputs/
│   └── .gitkeep
│
└── prompts/
    └── diagnose_prompt.md
```

---

## 🚀 Installation and Running

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project folder

```bash
cd NetSage_AI
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

---

## 🧪 Quick Demo

Use the **Quick Demo Case** mode and select scenarios such as:

- 🟦 VLAN Mismatch
- 🟩 DHCP Pool Exhaustion
- 🟨 DNS Failure
- 🟥 Interface Down

Then click:

```text
🧠 Run NetSage Diagnosis
```

---

## 🛡️ Responsible AI

NetSage AI does not automatically modify network configurations.

All recommendations should be reviewed by a qualified human before applying changes to a production network.

The system is designed as a decision-support and troubleshooting assistant.

---

## 🚀 Future Enhancements

- Integration with live network devices
- Support for additional network protocols
- Machine learning-based anomaly detection
- Real-time monitoring
- Knowledge graph for network dependencies
- Advanced historical pattern analysis

---

## 👩‍💻 Author

Harshita
