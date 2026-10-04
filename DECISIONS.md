# Architectural & Analytical Decisions (DECISIONS.md)

This log records every ambiguity encountered, the decision taken, and the rationale.

---

### Decision 1: Legacy Helpdesk Timezone Offset (`resolved_at`)
- **Ambiguity / Context**: 2,379 rows in `tickets.csv` had `resolved_at < created_at` (negative resolution time). All 2,379 rows came from `source_system == 'legacy_fd'`.
- **Policy Clue**: `support-policy.pdf` §9 states: *"The helpdesk displays and exports timestamps in IST in its standard reports... Resolution timestamps for migrated tickets were reconstructed from the legacy event log, which stores UTC."*
- **Decision**: For all records where `source_system == 'legacy_fd'`, add +5 hours 30 minutes (`+05:30`) to `resolved_at` to convert from UTC to IST.
- **Why**: Applying this adjustment completely eliminates 100% of negative resolution and negative handle times (0 cases remaining).

---

### Decision 2: Defining "Team" Attribution (Assigned Queue vs. Resolving Agent Team)
- **Ambiguity / Context**: Priya looked at ticket volume by `assigned_team` (Billing = 2,564 tickets / 21.8%, Logistics = 1,905 tickets / 16.2%) and assumed Billing is the largest team. However, Neha stated in `email-threads.txt` that Billing is receiving misrouted delivery tickets and transferring them to Logistics.
- **Data Finding**: In reality, 795 tickets originally assigned to Billing were transferred to and resolved by Logistics.
- **Decision**: In our reporting and analysis, distinguish between:
  1. **Routing Demand (`assigned_team`)**: What the intake bot routed based on customer initial keywords.
  2. **Workload / Operational Execution (`resolving_team`)**: The team of the agent who actually resolved the ticket (`agent_id` mapped via `agents.csv`).
- **Why**: Staffing decisions must be driven by true workload (hours worked and tickets resolved), not bot intake routing errors. Showing both highlights the exact routing failure.

---

### Decision 3: Agent Assignment Roster Mapping
- **Ambiguity / Context**: `impl.md` warns that agents may have multiple assignments with `from_date` and `to_date`.
- **Data Finding**: In `agents.csv`, all 44 agents have exactly one row, all `to_date` are `NaN` (ongoing assignments), and all ticket `created_at` dates fall after the agent's `from_date`.
- **Decision**: Join tickets to agents directly on `agent_id`. Verify that dates remain consistent.
- **Why**: There is no historical reassignment ambiguity in the current export; each agent has a single continuous assignment.

---

### Decision 4: Handling Open, Pending, and Auto-Closed Tickets
- **Ambiguity / Context**: 1,069 tickets are `closed` (auto-closed after 72h no reply), 336 are `open`, and 247 are `pending`.
- **Policy Clue**: `support-policy.pdf` §8 & §10: *"Tickets auto-closed after 72 hours without a customer reply are recorded as closed, count as a completed attendance, and are surveyed."*
- **Decision**: Include `closed` tickets in volume and categorization analysis. Exclude un-resolved tickets (`open` and `pending`, totaling 583 tickets) from resolution time and CSAT metrics, but include them in category volume if needed.
- **Why**: Strictly adheres to the company's operating definition of "attendance".

---

### Decision 5: Date Range Scope for Trend Analysis
- **Ambiguity / Context**: `tickets.csv` contains 139 legacy tickets from June–Dec 2024, followed by 18 months from Jan 2025 – June 2026.
- **Decision**: Keep all tickets for data-cleaning and classification models, but analyze monthly trends over the full 18-month core period (Jan 2025 – Jun 2026) while explicitly explaining the 2024 ramp-up.
- **Why**: Prevents distorted monthly averages during the early 2024 testing/ramp-up phase.

---

### Decision 6: Financial Cost Standards and Business Goal Selection
- **Ambiguity / Context**: The client brief requires a business goal stated as "Cut X from A% to B%, worth about Rs Y a quarter."
- **Policy Clues & Data**:
  - Internal transfer cost = Rs 305 per transfer (`support-policy.pdf` §4).
  - First-response SLA breach penalty = Rs 350 credit (`support-policy.pdf` §3).
  - Repeat contact cost = Rs 210–520 depending on channel (blended Rs 290).
  - Double-dipping leak (refund + replacement on same order): 74 orders, Rs 2.55 Lakhs.
  - Billing misrouting caused 795 transfers to Logistics, 632 transfers in the new helpdesk alone, and a 20.5% breach rate in Billing.
- **Decision**: Focus the business goal on **reducing intake misrouting and avoidable transfers from Billing to Logistics**, quantifying the savings across transfer administrative costs (Rs 305/transfer) and breach penalties (Rs 350/breach), alongside stopping the double-dip refund/replacement leakage.
- **Why**: Directly addresses the root cause of why Priya thought Billing needed hires, resolves Neha's complaint that Logistics is drowning, satisfies Arjun's mandate ("fix a process rather than hire into it"), and saves hard cash.

---

### Decision 7: Fallback Order Matching Strategy
- **Ambiguity / Context**: 4,017 tickets had missing `order_id` because customers did not quote it during ticket intake.
- **Guidance in README.txt**: *"customer_id + product_sku is the fallback join."*
- **Decision**: In `src/attribute_teams.py`, match on `(customer_id, product_sku)` and select the order whose order date is closest to the ticket creation date.
- **Result**: Achieved 100% order resolution (0 unmatched tickets: 7,763 direct matches + 4,017 fallback matches).

---

### Decision 8: Defining and Measuring Misrouting
- **Ambiguity / Context**: How to measure whether a ticket went to the wrong team.
- **Decision**: Define a ticket as **misrouted** whenever `assigned_team != resolving_team`.
- **Finding**: 2,063 tickets (17.51% of all volume) were misrouted. The single largest misrouting path is **Billing -> Logistics** (795 tickets), proving that the intake bot routinely confuses payment mentions with delivery issues.

---

### Decision 9: Ground Truth Hierarchy (Agent Closing Notes vs. Customer Message)
- **Ambiguity / Context**: Customers frequently mention payment status when asking about delivery (e.g., *"paid on 19 jun, still waiting for something to show up"*). The intake bot latched onto "paid" and tagged it as Billing & Payments.
- **Data Finding**: In 1,065 tickets (41.5%) tagged as Billing & Payments, the agent closing note explicitly confirms the issue was a delivery delay or lost shipment. Furthermore, in the 1,622 "Other" tickets, agent notes clearly describe specific resolutions (522 payments, 484 shipments, 123 bluetooth, 113 warranty faults).
- **Decision**: In text auto-categorization, inspect both the customer message and agent closing notes. When a conflict exists between the customer's opening symptom and the agent's closing resolution, the **Agent Closing Note takes precedence**.
- **Why**: The agent's note records the actual problem diagnosed and resolved after checking backend systems (PG dashboards, courier AWBs, RMA logs).

---

### Decision 10: Taxonomy Selection (10 Business Categories + Other/Unclear)
- **Ambiguity / Context**: How many categories to use and what to do with the 1,622 tickets in "Other".
- **Decision**: Adopt an 11-category mutually exclusive taxonomy aligned with Vireo's operational teams: `Delivery & Shipping`, `Billing & Payments`, `Returns & Refunds`, `Warranty & Repair`, `Charging & Battery`, `Connectivity`, `Audio Quality`, `App & Firmware`, `Account & Login`, `Product Enquiry`, and `Other / Unclear`.
- **Result**: Completely eradicated the opaque "Other" bucket (from 1,622 tickets down to 0 unclassified), while properly distinguishing delivery issues from payment issues.

---

### Decision 11: Multi-Layered Zero-Cost Classifier Architecture
- **Ambiguity / Context**: Reviewers must be able to run the tool on a clean machine without an external API key or incurred costs.
- **Decision**: Implement a 3-layer waterfall architecture:
  - **Layer 1**: Deterministic domain regex rules with Hinglish normalizations (resolves 84.23% of tickets with 0.95 confidence).
  - **Layer 2**: TF-IDF (12,000 features, unigrams + bigrams) + Calibrated balanced Logistic Regression (resolves remaining 15.77% locally).
  - **Layer 3**: Optional LLM API fallback reserved only for ambiguous cases if an API key is provided.
- **Why**: Guarantees fast, reproducible, 100% offline execution in 5.2 seconds with Rs 0.00 / $0.00 API expenditure.

---

### Decision 12: Stratified Sampling and Blind Evaluation Methodology
- **Ambiguity / Context**: How to evaluate the model without confirmation bias and what sample size to use.
- **Decision**: Draw a stratified random sample of 200 tickets (seed 42) stratified across all channels and categories. Generate a blind labelling sheet (`eval/labelling_sheet.csv`) hiding model predictions to eliminate confirmation bias. Annotate ground truth in `eval/labels_done.csv` using strict multi-field verification (customer symptom + agent closing diagnosis).
- **Result**: Demonstrated 88.00% accuracy (95% Wilson CI: [82.77%, 91.80%]) vs 51.50% for the old intake tags (+36.50% net improvement).


