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
