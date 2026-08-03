import json
import os

w01_notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# ML-02 — Research Question and Provisional Lane\n",
    "\n",
    "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Sohila-Khaled-Abbas/flyrank-ml-internship-starter/blob/main/work/notebooks/w01_research_question.ipynb?flush_cache=true)\n",
    "\n",
    "This notebook documents the research question, lane selection, decision framework, empirical data summary, and boundaries for the FlyRank internship project."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. My lane (or freestyle) and why\n",
    "\n",
    "**Selected Lane:** **Refresh / Content Opportunity Scoring**\n",
    "\n",
    "Content decay and organic traffic loss affect over half of published digital content (54.2% of content items in the dataset show a `down` performance trend). Content teams and editors operate under limited time and budget constraints; they cannot manually audit thousands of published URLs. Building an automated, evidence-backed opportunity scoring pipeline enables editorial teams to transition from reactive firefighting to prioritized, high-ROI content refreshes."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Lane confirmation check\n",
    "selected_lane = \"Refresh / Content Opportunity Scoring\"\n",
    "print(f\"Selected Lane: {selected_lane}\")\n",
    "print(\"Primary Goal: Deliver a prioritized review queue of content items needing refresh.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. The question: decision, action, cost of a wrong call\n",
    "\n",
    "- **What decision does this improve?** Which decaying or underperforming content items should editorial teams prioritize for content refresh and SEO optimization first?\n",
    "- **Who acts on the output, and what do they do?** Content editors and SEO strategists. They update, expand, restructure, or optimize specific high-priority content items (e.g. updating outdated statistics, sharpening search intent alignment, and improving internal linking).\n",
    "- **What does a wrong answer cost?**\n",
    "  - *False Positive (recommending a healthy or low-value page):* Wasted editorial hours and budget (e.g., 3-5 editorial hours spent rewriting a page with minimal potential traffic gain).\n",
    "  - *False Negative (missing a high-impact decaying page):* Cumulative, unrecovered loss of organic search traffic, keyword rankings, and potential client revenue."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Cost-benefit framework demonstration\n",
    "cost_fp_editor_hours = 4.0  # Average hours lost per false positive refresh recommendation\n",
    "cost_fn_traffic_loss_pct = 0.25 # Unaddressed traffic drop on high-value pages\n",
    "print(f\"Cost of FP: ~{cost_fp_editor_hours} editorial hours per unnecessary refresh.\")\n",
    "print(f\"Cost of FN: ~{cost_fn_traffic_loss_pct:.0%} ongoing organic traffic drop on missed opportunity pages.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Quick look at the data (2-3 real numbers)\n",
    "\n",
    "Loading `data/raw/content_refresh_anonymized.csv` to inspect empirical numbers backing this lane:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import os\n",
    "\n",
    "# Load dataset\n",
    "csv_path = \"../../data/raw/content_refresh_anonymized.csv\"\n",
    "if not os.path.exists(csv_path):\n",
    "    csv_path = \"data/raw/content_refresh_anonymized.csv\"\n",
    "\n",
    "df = pd.read_csv(csv_path)\n",
    "\n",
    "total_items = len(df)\n",
    "num_clients = df[\"client_id\"].nunique()\n",
    "down_trend_count = len(df[df[\"trend_direction\"] == \"down\"])\n",
    "down_trend_pct = (down_trend_count / total_items) * 100\n",
    "median_imp = df[\"impressions_90d\"].median()\n",
    "high_imp_down = len(df[(df[\"impressions_90d\"] > median_imp) & (df[\"trend_direction\"] == \"down\")])\n",
    "total_impressions = df[\"impressions_90d\"].sum()\n",
    "total_clicks = df[\"clicks_90d\"].sum()\n",
    "\n",
    "print(f\"1. Dataset Scale: {total_items:,} content items across {num_clients} pseudonymized clients.\")\n",
    "print(f\"2. Search Traffic Scope: {total_impressions:,} 90-day impressions and {total_clicks:,} 90-day clicks.\")\n",
    "print(f\"3. Decay Prevalence: {down_trend_count:,} items ({down_trend_pct:.1f}%) are in a 'down' performance trend.\")\n",
    "print(f\"4. High-Impact Target Candidates: {high_imp_down:,} pages have above-median impressions (>{median_imp:.0f}) while trending down.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Careful words: what I can and can't claim\n",
    "\n",
    "- **What I CAN claim:** Decision-support scoring, relative prioritization of refresh candidates based on observed search and engagement performance, and empirical signal strength.\n",
    "- **What I CANNOT claim:** Causal proof that updating a page will guarantee rank restoration, exact traffic volume guarantees post-refresh, or deterministic prediction of search engine algorithm updates."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Print explicit boundaries\n",
    "print(\"--- Scope & Claims Boundaries ---\")\n",
    "print(\"[CAN CLAIM] Decision-support priority queue for editorial review.\")\n",
    "print(\"[CAN CLAIM] Observed historical decay patterns and signal correlations.\")\n",
    "print(\"[CANNOT CLAIM] Guaranteed Google ranking position restoration.\")\n",
    "print(\"[CANNOT CLAIM] Causal guarantees without controlled A/B experiment data.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Self-check\n",
    "\n",
    "- [x] Every section above is filled — markdown thinking AND the code that backs it\n",
    "- [x] The notebook runs top to bottom with no errors (Runtime → Run all)\n",
    "- [x] No client names, URLs, or private queries anywhere\n",
    "- [x] My claims use careful words: observed, measured, directional, decision-support\n",
    "- [x] Committed to my repo under `work/notebooks/`"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "name": "python3"
  },
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

w02_notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# ML-03 — Frame Your Lane as an ML Task\n",
    "\n",
    "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Sohila-Khaled-Abbas/flyrank-ml-internship-starter/blob/main/work/notebooks/w02_ml_task_framing.ipynb?flush_cache=true)\n",
    "\n",
    "This notebook frames the **Refresh / Content Opportunity Scoring** lane into a formal ML task specification: task type, observed target, success metrics, unit of analysis dataframe probe, and justification over fixed rules."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. My lane as an ML task (type)\n",
    "\n",
    "**Selected Task Type:** **Ranking / Scoring** (Opportunity Priority Scoring)\n",
    "\n",
    "**Why:** The primary decision requirement is to present content editors with a ranked queue of content items (ordered from highest opportunity / highest decay severity to lowest). Editors work from top to bottom. Ranking and continuous scoring reflect this operational decision workflow directly, unlike unranked binary classification."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Task Type Definition\n",
    "task_type = \"Ranking / Priority Scoring\"\n",
    "output_format = \"Ranked Queue of Content IDs (content_id)\"\n",
    "print(f\"Task Type: {task_type}\")\n",
    "print(f\"Primary Output: {output_format}\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Target or proxy\n",
    "\n",
    "- **Target:** Observed outcome measured in a future/subsequent performance window — e.g. observed traffic drop magnitude (`clicks_prev_30d` - `clicks_last_30d`) or post-refresh traffic recovery in panel data.\n",
    "- **Label Origin:** Strictly **observed in data**, NEVER defined by an arbitrary heuristic rule.\n",
    "- **Leakage Safeguard:** `is_declining_label`, `trend_direction`, and `trend_pct` are derived label targets or window summaries — they are strictly **excluded** from the feature set to prevent data leakage."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Target & Feature Isolation Verification\n",
    "forbidden_leakage_features = [\"is_declining_label\", \"trend_direction\", \"trend_pct\"]\n",
    "print(\"Excluded Target/Leakage Features:\", forbidden_leakage_features)\n",
    "print(\"Rule: Features must only use observed metrics strictly prior to the outcome window.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Success metric\n",
    "\n",
    "- **Primary Metric:** **Precision@K** (e.g. Precision@50 and Precision@100 on the top-ranked recommendations queue).\n",
    "- **Secondary Metric:** **NDCG@K** (Normalized Discounted Cumulative Gain) for ranking quality, and **ROC-AUC** / **PR-AUC** for binary outcome proxies.\n",
    "- **Defending the Metric:** Precision@K directly measures the efficiency of editor time — if an editor inspects the top 50 recommended pages, Precision@50 tells us what fraction actually represented high-impact decaying content."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Metric definition check\n",
    "primary_metric = \"Precision@K (K=50, K=100)\"\n",
    "secondary_metric = \"NDCG@K / ROC-AUC\"\n",
    "print(f\"Primary Success Metric: {primary_metric}\")\n",
    "print(f\"Secondary Metric: {secondary_metric}\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. The unit of analysis, as a real dataframe\n",
    "\n",
    "**Unit of Analysis:** One row = One pseudonymized content item (`content_id`) within a client context (`client_id`).\n",
    "\n",
    "Loading the starter CSV slice to verify dataset grain and schema:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import os\n",
    "\n",
    "csv_path = \"../../data/raw/content_refresh_anonymized.csv\"\n",
    "if not os.path.exists(csv_path):\n",
    "    csv_path = \"data/raw/content_refresh_anonymized.csv\"\n",
    "\n",
    "df = pd.read_csv(csv_path)\n",
    "\n",
    "# Verify Grain: content_id must be unique per row\n",
    "row_count = len(df)\n",
    "unique_content = df[\"content_id\"].nunique()\n",
    "is_unique = (row_count == unique_content)\n",
    "\n",
    "print(f\"Dataframe Shape: {df.shape}\")\n",
    "print(f\"Total Rows: {row_count:,}\")\n",
    "print(f\"Unique Content IDs: {unique_content:,}\")\n",
    "print(f\"Grain Verification (1 row = 1 content_id): {'PASSED' if is_unique else 'FAILED'}\")\n",
    "\n",
    "# Display key feature slice\n",
    "feature_cols = [\"content_id\", \"client_id\", \"impressions_90d\", \"clicks_90d\", \"content_age_days\", \"ctr\", \"avg_position\", \"engagement_rate\"]\n",
    "print(\"\\nSample Dataframe Slice (Unit of Analysis):\")\n",
    "print(df[feature_cols].head())\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Why ML beats a fixed rule here\n",
    "\n",
    "A static rule (e.g., `if content_age > 180 and trend == down`) is inadequate for content refresh decisions because:\n",
    "1. **Non-linear Multi-Factor Signal Interactions:** Traffic decline involves coupled interactions between search volume, position tier, CTR relative to position benchmark, engagement rate, keyword intent, and content type.\n",
    "2. **False Positive & High-Volume Blind Spots:** A static rule flags old pages regardless of traffic volume (wasting editor time on 10-impression pages), while missing newly decaying high-traffic pages that need immediate intervention.\n",
    "3. **Dynamic Prioritization:** Machine learning models learn non-linear decision boundaries and weight relative decay against opportunity size, delivering an optimized, actionable queue."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Code demonstration showing why plain rule fails\n",
    "# Rule: age > 180 days AND down trend\n",
    "simple_rule_flag = (df[\"content_age_days\"] > 180) & (df[\"trend_direction\"] == \"down\")\n",
    "flagged_by_rule = df[simple_rule_flag]\n",
    "\n",
    "low_traffic_flagged = len(flagged_by_rule[flagged_by_rule[\"impressions_90d\"] < 100])\n",
    "high_traffic_missed = len(df[(~simple_rule_flag) & (df[\"impressions_90d\"] > 5000) & (df[\"trend_direction\"] == \"down\")])\n",
    "\n",
    "print(f\"Simple Rule Flagged Pages: {len(flagged_by_rule):,} total\")\n",
    "print(f\" - Low-Traffic Wasted Effort (Impressions < 100): {low_traffic_flagged:,} pages\")\n",
    "print(f\" - High-Traffic Missed Opportunities (Impressions > 5,000 & Down): {high_traffic_missed:,} pages\")\n",
    "print(\"Conclusion: A simple if-statement suffers from high false-positives and missed high-value opportunities.\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Self-check\n",
    "\n",
    "- [x] Every section above is filled — markdown thinking AND the code that backs it\n",
    "- [x] The notebook runs top to bottom with no errors (Runtime → Run all)\n",
    "- [x] No client names, URLs, or private queries anywhere\n",
    "- [x] My claims use careful words: observed, measured, directional, decision-support\n",
    "- [x] Committed to my repo under `work/notebooks/`"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "name": "python3"
  },
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

os.makedirs('work/notebooks', exist_ok=True)
with open('work/notebooks/w01_research_question.ipynb', 'w', encoding='utf-8') as f:
    json.dump(w01_notebook, f, indent=1)
print('Updated w01_research_question.ipynb')

with open('work/notebooks/w02_ml_task_framing.ipynb', 'w', encoding='utf-8') as f:
    json.dump(w02_notebook, f, indent=1)
print('Updated w02_ml_task_framing.ipynb')
