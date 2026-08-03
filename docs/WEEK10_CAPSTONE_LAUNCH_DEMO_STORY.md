# Week 10 Capstone: Send the Link — Launch, Demo & Story

**Track**: General AI Fluency  
**Author**: Sohila Khaled Abbas (Applied ML Intern at FlyRank AI & BI Developer)  
**Date**: August 4, 2026  
**Capstone Status**: Fully Deployed & Verified  

---

## 🌐 1. Live Capstone Launch Links

- **Main Portfolio Platform**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/index.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/index.html)
- **Deployed Capstone Research Paper**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/paper.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/paper.html)
- **FL-09 Interactive Agent Demo & Video Showcase**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/fl09-demo.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/fl09-demo.html)
- **Framed Case Studies Hub**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/cases.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/cases.html)
- **DNS & Custom Domain Infrastructure Walkthrough (PF-04)**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/dns-walkthrough.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/dns-walkthrough.html)
- **About & Detailed CV**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/about.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/about.html)

---

## 🛠️ 2. The Plan to Keep Building (Post-Internship Expansion)

### A. Concrete "How to Add the Next Case" Protocol
1. **Target Location**:
   Appended as an `<article class="case-card">` element directly inside `<main>` of [`cases.html`](file:///d:/courses/Data%20Science/Data%20Engineering/flyrank-ml-internship-starter/cases.html). An HTML placeholder comment `<!-- CASE STUDY 03 (UPCOMING) -->` marks the exact insertion point.

2. **The 3-Beat Narrative Shape (Week 2 Standard)**:
   - **Beat 1: The Problem (Operational Friction & Waste)**  
     Quantify baseline inefficiency before ML/ETL intervention (e.g. *~4.0 hours per post wasted on false-positive rewrites*).
   - **Beat 2: What I Did & Decided (Methodology & Trade-offs)**  
     Detail dataset size ($n$), feature engineering, model architecture, and leak-free split strategy (e.g., *grouped client holdout, temporal cutoff*).
   - **Beat 3: What Came of It (Empirical Metrics & Impact)**  
     State precise validation metrics (e.g., *Precision@50: 100.0%, 0.9659 ROC-AUC*) and append a visual `<div class="metric-pill">`.

### B. Named Next Real Piece of Work
* **Project Title**: **Automated SERP Intent Shift Classifier & Organic Cannibalization Monitor**
* **Beat 1 (Problem)**: Search engines frequently re-classify search intent (e.g., shifting from Informational to Commercial transactional SERPs), causing traffic drops misdiagnosed by marketing teams as content decay, costing ~6 hours per domain in wasted audit effort.
* **Beat 2 (What I Will Do)**: Fine-tune a sentence-transformer NLP classifier (DeBERTa-v3 / MiniLM) on GSC query-level CTR time series combined with SERP feature count distributions, using client-grouped temporal holdouts.
* **Beat 3 (Expected Outcome)**: Achieve $\ge 90\%$ Precision@20 on intent shift flags, cutting diagnostic lead time from 6 hours to under 15 minutes per domain.

### C. Evidence of Concrete Reminder Set
* **Event Title**: `[Portfolio Update] Draft & Deploy Case Study 03: SERP Intent Shift Classifier`
* **Scheduled Date**: **Monday, August 24, 2026 at 09:00 AM UTC+3** *(Bi-weekly recurring reminder)*
* **Alert Trigger**: 2 days prior (August 22, 2026) and 15 minutes prior on execution day.
* **iCalendar (.ics) Artifact**: Tracked in repository at [`docs/reminders/case_study_03_reminder.ics`](file:///d:/courses/Data%20Science/Data%20Engineering/flyrank-ml-internship-starter/docs/reminders/case_study_03_reminder.ics).

### D. Preserved Build Context (Claude Project & Identity Kit)
* **Preserved System Prompt & Context**:
  `CLAUDE.md`, `AGENTS.md`, and `skills/README.md` preserve repo ground rules, identity kit (Sohila Khaled Abbas, Applied ML Intern at FlyRank AI & BI Developer), design tokens (`--accent-sky: #0EA5E9`), and typography (`Outfit`, `Inter`, `JetBrains Mono`).
* **Low-Cost Update Protocol**:
  Paste raw project metrics into the preserved Claude Project with:
  > *"Read `cases.html` and `CLAUDE.md`. Format my raw notes for the SERP Intent Shift Classifier into an `<article class="case-card">` using the 3-beat shape (Problem, What I did & decided, What came of it). Maintain existing CSS classes, metric pills, and leak-free ML framing."*
