# Sohila Khaled · Applied ML & Search Intelligence Portfolio

[![Live Site](https://img.shields.io/badge/Live_Site-GitHub_Pages-0EA5E9?style=flat-square)](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/)
[![FlyRank AI](https://img.shields.io/badge/FlyRank_AI-ML_Internship_2026-6366F1?style=flat-square)](https://flyrank.ai)

Official portfolio and **PF-04 Deliverable (Personal Website & DNS Subdomain Walkthrough)** for **Sohila Khaled**, Applied ML Intern & Search Intelligence Engineer at FlyRank AI (July 2026 Cohort).

---

## 🌐 Verified Live Links
- 🏠 **Live Public HTTPS Site**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/)
- 🌐 **PF-04 DNS Deliverable Page**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/dns-walkthrough.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/dns-walkthrough.html)
- 📄 **Deployed Research Paper**: [https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/paper.html](https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/paper.html)
- 💼 **LinkedIn Profile**: [https://linkedin.com/in/sohila-khaled](https://linkedin.com/in/sohila-khaled)
- 📅 **1-on-1 Booking Link**: [https://cal.com/sohila-khaled/15min](https://cal.com/sohila-khaled/15min)
- 🎯 **Target Subdomain**: `sohilakhaled.flyrank.ai`

---

## 📁 Repository Structure

```text
flyrank-ml-internship-starter/
├── index.html              # Hero section, technical skills, 5 featured projects, contact links
├── about.html              # Full CV/Resume, career summary, community leadership, certifications
├── dns-walkthrough.html    # PF-04 Deliverable: Interactive Mermaid.js DNS diagram & checklist
├── paper.html              # Deployed Capstone Research Paper (9 complete sections)
├── cases.html              # Framed 3-beat Search Intelligence case studies
├── css/
│   └── styles.css          # Modern CSS design tokens, dark/light theme, responsive grid cards
├── js/
│   └── main.js            # Theme switcher, mobile drawer, checklist persistence, Mermaid init
├── work/
│   ├── notebooks/          # All 10 executed ML internship Jupyter notebooks
│   └── outputs/            # Baseline CSVs and FL-06 Word Document specification
├── submission/
│   └── paper_url.txt       # Direct paper URL submission link
└── README.md               # Repository & deployment documentation
```

---

## 🚀 GitHub Pages & CNAME Custom Subdomain Walkthrough

### **Part 1: Deploying Static Site to GitHub Pages**
1. Commit all files (`index.html`, `about.html`, `dns-walkthrough.html`, `css/styles.css`, `js/main.js`) to the `main` branch:
   ```bash
   git add .
   git commit -m "Deploy modern applied ML portfolio site"
   git push origin main
   ```
2. In GitHub repository settings $\rightarrow$ **Pages** $\rightarrow$ Build and deployment:
   - Source: **Deploy from a branch**
   - Branch: `main` / `(root)`
3. Save settings. The site will be live over HTTPS at `https://sohila-khaled-abbas.github.io/flyrank-ml-internship-starter/` in ~30 seconds.

---

### **Part 2: Configuring Custom Subdomain (`sohilakhaled.flyrank.ai`)**
When FlyRank Ops grants the subdomain at capstone approval time:
1. **FlyRank Ops DNS Provisioning**:
   Ops creates the CNAME record:  
   `sohilakhaled.flyrank.ai CNAME sohila-khaled-abbas.github.io`
2. **Repository CNAME Configuration**:
   Add `sohilakhaled.flyrank.ai` to GitHub Pages **Custom domain** setting or create a `CNAME` file in the repo root containing `sohilakhaled.flyrank.ai`.
3. **Verify DNS & HTTPS Padlock**:
   - Verify resolution: `dig sohilakhaled.flyrank.ai CNAME`
   - Check **Enforce HTTPS** in GitHub Pages settings.
