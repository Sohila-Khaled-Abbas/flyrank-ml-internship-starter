# Week 9 — The Plan to Keep Building
**Track**: General AI Fluency  
**Author**: Sohila Khaled Abbas (Applied ML Intern at FlyRank AI)  
**Date**: August 4, 2026  

---

## 1. Concrete "How to Add the Next Case" Protocol

### Where the Next Case Study Will Live
All framed case studies reside on the live portfolio page at [`cases.html`](file:///d:/courses/Data%20Science/Data%20Engineering/flyrank-ml-internship-starter/cases.html), styled using the established design system (`css/styles.css`). When a new piece of work is ready, it is appended as an `<article class="case-card">` component directly inside `<main>` of `cases.html`.

### The 3-Beat Update Procedure (Week 2 Shape)
Every new case study must strictly follow the three-beat narrative structure:

1. **Beat 1: The Problem (Baseline & Pain Point)**
   - Define the concrete operational/business friction (e.g., wasted hours, high false-positive rate, unmonitored signal drift).
   - State the baseline metric before intervention (e.g., ~4.0 hours per article manual review, 0% automated detection).

2. **Beat 2: What I Did & Decided (Methodology & Trade-offs)**
   - Specify data sources, sample sizes ($n$), and feature engineering strategy.
   - Highlight explicit architectural decisions and anti-leakage controls (e.g., temporal/client-grouped holdout splits, target isolation).

3. **Beat 3: What Came of It (Measurable Impact)**
   - Provide empirical validation metrics (e.g., Precision@K, ROC-AUC, lift over random baseline, operational time saved).
   - Include a visual `<div class="metric-pill">` summarizing key numbers.

### HTML Template Code snippet for `cases.html`
```html
<article class="case-card">
    <span class="case-tag">Case Study 03 · [Sub-domain / Track]</span>
    <h2>[Project Title]</h2>
    <div class="beat">
        <div class="beat-title">Beat 1: The Problem</div>
        <p>[Problem description, operational waste, and baseline metrics]</p>
    </div>
    <div class="beat">
        <div class="beat-title">Beat 2: What I Did & Decided</div>
        <p>[Data pipeline, ML model choice, leak-free validation, and trade-offs]</p>
    </div>
    <div class="beat">
        <div class="beat-title">Beat 3: What Came of It</div>
        <p>[Empirical outcomes, precision/recall, time saved, and business impact]</p>
        <div class="metric-pill">[Key Metric 1] | [Key Metric 2]</div>
    </div>
</article>
```

---

## 2. Named Next Real Piece of Work

**Project Title**: *Automated SERP Intent Shift Classifier & Organic Cannibalization Monitor*

- **The Problem (Beat 1)**: Search engine algorithms periodically alter search intent classification for key query clusters (e.g., shifting from Informational to Commercial transactional results). Content teams mistake these shifts for content quality decay or technical errors, wasting tens of engineering hours attempting on-page optimizations for queries where SERP features no longer favor long-form articles.
- **Technical Execution (Beat 2)**: Train an NLP classifier using sentence-transformer embeddings (DeBERTa-v3 / MiniLM) combined with Google Search Console (GSC) query-level click/impression distributions and SERP feature counts. Validate using a temporal domain holdout split to prevent lookahead bias.
- **Target Outcome (Beat 3)**: Achieve $\ge 90\%$ Precision@20 on intent-shift flags, reducing traffic drop diagnostic time from 6 hours to under 15 minutes per domain.

---

## 3. Evidence of Concrete Reminder Set

- **Calendar Event Title**: `[Portfolio Update] Draft & Deploy Case Study 03: SERP Intent Shift Classifier`
- **Scheduled Time**: Monday, August 24, 2026 at 09:00 AM UTC+3 (Recurring bi-weekly until published)
- **Alert Nudges**: 
  - 2 days prior (Saturday, August 22, 2026 at 09:00 AM)
  - 15 minutes prior on execution day
- **iCalendar (.ics) Artifact**: Generated and tracked in repository at [`docs/reminders/case_study_03_reminder.ics`](file:///d:/courses/Data%20Science/Data%20Engineering/flyrank-ml-internship-starter/docs/reminders/case_study_03_reminder.ics).

---

## 4. Preserved Build Context (Claude Project / AI Assistant Setup)

To make future updates take **less than 10 minutes** instead of requiring a complete rebuild:

1. **System Identity & Stack Preservation**:
   - `CLAUDE.md` and `AGENTS.md` preserve repo ground rules, identity kit (Sohila Khaled Abbas, Applied ML Intern at FlyRank AI & BI Developer), color tokens (`--accent-sky: #0EA5E9`), and typography (`Outfit`, `Inter`, `JetBrains Mono`).
   - `skills/README.md` acts as the router so future tasks load general skills (e.g., `writing-honest-claims`, `deploying-static-pages`).

2. **Single-Prompt Update Protocol for Future Case Studies**:
   Paste the raw experimental notes into the preserved Claude Project with the prompt:
   > *"Read `cases.html` and `CLAUDE.md`. Format my raw notes for the SERP Intent Shift Classifier into an `<article class="case-card">` using the 3-beat shape (Problem, What I did & decided, What came of it). Maintain existing CSS classes, metric pills, and leak-free ML framing."*
