# 3-Minute Screen-Recording Script

This script guides the required $\le 3$-minute non-slide walkthrough demonstrating the repo, prompt iterations, evaluation evidence, charts, and discarded approaches.

---

### Segment 1 (0:00 – 0:20): Repo Overview & The Headline Number
- **What to Show on Screen:**  
  Show the GitHub repository / VS Code project root with `src/`, `outputs/`, `eval/`, and `README.md`.
- **What to Say:**  
  *"Hi, I’m walking through our AI-assisted support triage tool for Vireo Audio. The tool processes 11,780 support tickets in 5 seconds with zero API cost and 88% accuracy. Our headline business finding directly addresses Head of CX Priya Raman's hiring question: **Do not hire into Billing.** By cutting intake misrouting from 41.5% to under 5% and stopping dual refund-replacements, Vireo can save **Rs 1,35,500 per quarter** in direct waste while avoiding an unneeded **Rs 9 Lakhs per year** in Billing headcount."*

---

### Segment 2 (0:20 – 1:00): Prompt & Architecture Evolution (v1 $\to$ v2 $\to$ v3)
- **What to Show on Screen:**  
  Open `src/classify.py` and scroll through Layer 1 and Layer 2.
- **What to Say:**  
  *"Let’s look at how our architecture evolved across three versions:*
  - ***v1 (The Flawed Baseline)***: *Initially, we tested a single-pass LLM prompt looking only at customer opening messages. It made the exact same mistake as Vireo's chatbot: whenever a customer said 'I paid 5 days ago, where is my order?', it classified it as Billing. It was slow and cost money.*
  - ***v2 (Agent Note Grounding)***: *We realized that customer text contains misleading symptoms, but agent closing notes record true technical and courier diagnoses. In v2, we established a strict hierarchy: agent closing notes take precedence over customer opening text.*
  - ***v3 (The Zero-Cost Hybrid Pipeline)***: *Instead of paying for an API on all 11,780 tickets, v3 uses deterministic regex rules with Hinglish normalizations for 84% of tickets, and a local scikit-learn TF-IDF model for the remaining 16%. It runs in 5 seconds with zero external cost."*

---

### Segment 3 (1:00 – 1:40): Evaluation Evidence & Error Analysis
- **What to Show on Screen:**  
  Open `eval/eval_report.md` showing the Benchmark Comparison Table and Calibration Table.
- **What to Say:**  
  *"How do we know it works? We drew a stratified random sample of 200 tickets across all categories and channels, and evaluated blindly against hand-labelled ground truth:*
  - *The AI tool achieved **88.00% accuracy** with a 95% Wilson confidence interval of **[82.8%, 91.8%]**.*
  - *This outperforms the status quo chatbot tags (**51.50%**) by **+36.50% net improvement**.*
  - *The calibration table shows that high-confidence tickets achieve over 91% accuracy, while low-confidence tickets accurately flag ambiguous multi-issue queries (e.g. shipping delay plus hardware defect)."*

---

### Segment 4 (1:40 – 2:20): Charts & Headcount Decision Pushback
- **What to Show on Screen:**  
  Open `outputs/charts/monthly_by_team.png` and `outputs/charts/headcount_workload_analysis.png`.
- **What to Say:**  
  *"Now to the core business question: Should Priya put the two hires into Billing?*
  - *Looking at chart 2, Priya saw Billing as 22% of intake demand. But looking at actual resolution, **Logistics resolved 2,574 tickets while Billing resolved only 1,798**.*
  - *Looking at chart 3, Logistics carries **515 tickets per agent** (highest in the company) with a median resolution time of **26 hours**, and endured 795 transfers from Billing.*
  - *Billing tickets take only 1.2 hours to resolve. Adding 2 agents to Billing would waste Rs 9 Lakhs a year. Logistics is carrying the real weight, but fixing intake routing eliminates ~30% of Logistics volume before hiring anyone."*

---

### Segment 5 (2:20 – 3:00): Thrown-Away Work & Limitations
- **What to Show on Screen:**  
  Open `LIMITATIONS.md` and `outputs/charts/financial_leakage_and_savings.png`.
- **What to Say:**  
  *"Finally, what did we throw away and what is still wrong?*
  - ***Discarded Work***: *We discarded per-agent individual scorecards because courier delays unfairly distort frontline metrics. We also threw away heavy transformer models in favor of a fast, local TF-IDF solution.*
  - ***Known Limitations***: *The tool currently enforces single-label classification on multi-issue tickets, and 3rd-party courier delays cannot be solved by software alone.*
  - *To run the full suite from scratch on any machine, just run `python src/load_and_clean.py` followed by `src/attribute_teams.py`, `src/classify.py`, `src/evaluate.py`, and `src/analysis.py`. Everything runs in under 15 seconds."*
