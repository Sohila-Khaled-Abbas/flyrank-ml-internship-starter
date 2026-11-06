# Sohila Khaled Abbas · Applied ML & Search Intelligence Portfolio

[![Live Site](https://img.shields.io/badge/Live_Site-GitHub_Pages-0EA5E9?style=flat-square)](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/)
[![Research Paper](https://img.shields.io/badge/Research_Paper-Live_Page-10B981?style=flat-square)](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/paper.html)
[![FlyRank AI Verified](https://img.shields.io/badge/FlyRank_AI-Verified_Graduate-6366F1?style=flat-square)](https://aifluency.flyrank.ai/verify/sohilakhaled)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

Official portfolio and applied machine-learning project by **Sohila Khaled Abbas** (Machine Learning Engineer Intern at FlyRank AI | BI Developer).

---

## 🌐 Verified Live Deliverable Links

- 🏠 **Main Portfolio & Live Priority Playground**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/)
- 📄 **Deployed Capstone Research Paper**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/paper.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/paper.html)
- 🤖 **FL-09 Autonomous Agent Showcase**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/fl09-demo.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/fl09-demo.html)
- 🎥 **FL-09 Demo Video**: [https://youtu.com/flyrank-agent-fl09-demo](https://youtu.com/flyrank-agent-fl09-demo)
- 📊 **Framed Case Studies Hub**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/cases.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/cases.html)
- 🌐 **DNS Subdomain Walkthrough (PF-04)**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/dns-walkthrough.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/dns-walkthrough.html)
- 🎓 **Verified Graduate Credential**: [https://aifluency.flyrank.ai/verify/sohilakhaled](https://aifluency.flyrank.ai/verify/sohilakhaled)
- 💼 **LinkedIn Profile**: [https://linkedin.com/in/sohilakabbas](https://linkedin.com/in/sohilakabbas)

---

## ⚠️ Validation status — temporal audit in progress

The project work covered both the 30,000-row starter snapshot and the approximately 79-million-row daily warehouse release queried with DuckDB. The original 30,000-row snapshot experiment is retained as a historical exploratory artifact, **not a valid prospective model evaluation**. Its feature aggregates and the `trend_direction` target are calculated from overlapping recent-period windows. A client-grouped split prevents client overlap, but it does not prevent temporal leakage. The previously published Precision@K and ROC-AUC figures are withdrawn pending a point-in-time rebuild from daily warehouse data. Do not use the old metrics as evidence of predictive performance.

See [the temporal validation remediation plan](docs/temporal-validation-remediation.md).

---

## 📁 Repository Structure

```text
flyrank-ml-internship-starter/
├── index.html              # Main platform with live interactive ML Priority Calculator
├── about.html              # Full CV/Resume, career history, certifications, and technical stack
├── cases.html              # Framed 3-beat Search Intelligence case studies
├── paper.html              # Deployed Capstone Research Paper (9 complete sections)
├── fl09-demo.html          # FL-09 Deliverable: Demo video player, timestamps, reproduction guide
├── dns-walkthrough.html    # PF-04 Deliverable: Mermaid.js DNS diagram & provisioning checklist
├── favicon.svg             # Vector brand monogram mark ([ SK ])
├── CNAME                   # Custom domain routing (sohilakhaled.flyrank.ai)
├── css/
│   ├── styles.css          # Design system tokens, dark/light theme, responsive layout
│   └── fl09-styles.css     # FL-09 showcase styles, video player card, timestamp grid
├── js/
│   ├── main.js            # Theme switcher, mobile nav, interactive priority calculator
│   └── fl09-interactive.js # Timestamp scrubber & copy code buttons
├── n8n/
│   └── flyrank_content_refresh_workflow.json # Exported Docker n8n automation workflow
├── scripts/
│   ├── n8n_pipeline_handler.py # Agent pipeline execution handler
│   ├── 01_prepare_features.py  # Snapshot feature preparation (not point-in-time validation)
│   ├── 02_baseline_score.py    # Hand-written heuristic baseline
│   ├── 03_train_model.py       # Random Forest classifier with grouped client split
│   └── 04_evaluate_and_export.py # Evaluation metrics & action playbook export
├── work/
│   ├── notebooks/          # All 10 executed ML internship Jupyter notebooks
│   └── outputs/            # Evaluation metrics JSON, charts, and CSV action receipts
├── docs/
│   ├── WEEK03_CONSISTENCY_NOT_TALENT.md # Visual identity kit, content map, rejection notes
│   ├── FL09_AGENT_DOCUMENTATION_AND_DEMO.md # Agent technical specification & video guide
│   ├── FL10_FINAL_PACKAGE_RETROSPECTIVE_AND_CAPSTONE.md # Capstone master index & retrospective
│   └── WEEK09_PLAN_TO_KEEP_BUILDING.md # Next project roadmap & calendar reminder
└── submission/
    └── paper_url.txt       # Direct paper URL submission link
```

---

## 🚀 Quickstart: Reproducing the Agent Locally

```bash
# 1. Clone repo and setup environment
git clone https://github.com/Sohila-Khaled-Abbas/flyrank-ml-internship-starter.git
cd flyrank-ml-internship-starter
python -m venv venv
# On Windows: .\venv\Scripts\activate | On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# 2. Run the end-to-end ML pipeline
python scripts/03_train_model.py --allow-exploratory-snapshot  # exploratory only; not temporal validation
python scripts/04_evaluate_and_export.py  # exploratory outputs only until point-in-time data is implemented

# 3. (Optional) Run n8n webhook workflow with Docker
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n:latest
python scripts/n8n_pipeline_handler.py
```

---

## 🤖 Transparency Diligence (AI Fluency Framework)

> *"I built the n8n automation workflows, pipeline scaffolding, and CSS styling using Claude Code. I implemented and reviewed the original data-preparation and client-grouped experiment, then documented the temporal-window limitation and withdrew unvalidated predictive-performance claims."*  
> — **Sohila Khaled Abbas**
