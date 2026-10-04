# Honest Limitations, Shortcuts & Known Issues (LIMITATIONS.md)

As required by the vendor evaluation criteria, this document transparently details every known flaw, technical shortcut, edge-case failure, and untested assumption in the submitted deliverables.

---

### 1. Multi-Issue and Compound Customer Queries
- **The Issue**: In ~3.5% of tickets, customers report multiple overlapping problems (e.g., *"my left earbud is dead AND I haven't received the charging case order VR892011, refund my money"*).
- **Current Shortcut**: The classifier enforces a single mutually exclusive category label. It assigns the ticket based on the priority waterfall (technical defect vs. shipping vs. refund).
- **Operational Risk**: If routed strictly to Logistics, the technical warranty defect must still be transferred later to Tier 2 Escalations.
- **Recommended Fix**: Implement multi-label tagging or hierarchical primary/secondary routing in v2.

---

### 2. Ambiguity in Fallback Order Matching
- **The Issue**: 4,017 tickets lacked an explicit `order_id`. We resolved 100% of them by joining on `(customer_id, product_sku)` and taking the order with the minimum time delta to ticket creation.
- **Current Shortcut**: If a customer purchased the exact same earbud SKU twice within a few weeks (e.g., one for themselves and one as a gift), our fallback heuristic selects the closest order date.
- **Operational Risk**: While product family and retail value remain identical, the specific `order_id` or `lot_code` could be misattributed in rare repeat-purchase scenarios.

---

### 3. Missing Transfer Counter on Legacy Freshdesk Rows
- **The Issue**: The `transfers` field was introduced only in the new helpdesk on 14 September 2025 (`support-policy.pdf` §9). It is blank on all 4,052 pre-migration tickets.
- **Current Shortcut**: We treated legacy transfer counts as 0 in numerical aggregations, but isolated transfer financial calculations to the 9.5 months of current helpdesk data (6 quarters normalized).
- **Operational Risk**: True historical transfer costs prior to September 2025 were likely equally high, meaning our Rs 32,127/quarter transfer savings estimate is conservative.

---

### 4. Courier SLA Externalities
- **The Issue**: Logistics resolution time is 26.03 hours (median). While we proved Logistics is overburdened, much of this handle time is driven by 3rd-party logistics courier APIs (Delhivery, Bluedart, Xpressbees) rather than internal agent slowness.
- **Current Shortcut**: The helpdesk measures `created_at` to `resolved_at`, which includes external courier transit and RTO investigation windows.
- **Operational Risk**: Hiring more logistics agents cannot solve a courier delivery partner's regional truck delay. Process automation (automated AWB tracking webhooks) is required alongside staffing.

---

### 5. Sample Size Limitations on Rare Categories
- **The Issue**: Our formal evaluation was conducted on a stratified sample of 200 tickets ($N=200$).
- **Statistical Uncertainty**: While overall accuracy has a tight 95% Wilson CI of **[82.77%, 91.80%]** ($\pm 4.52\%$), low-frequency categories like `Account & Login` ($n=7$) and `Warranty & Repair` ($n=7$) have wider individual confidence bounds.

---

### 6. Terse Hinglish and Colloquial Typo Edge Cases
- **The Issue**: 3.0% of messages contain romanized Hindi or Hinglish. While our regex lexicon normalizes 22 common terms (e.g. `paisa`, `nahi mila`, `kharab`, `bhai`), extreme typos or unmapped regional slang (e.g. *chalu nahi ho raha*, *tut gaya*) can occasionally degrade to Layer 2 with lower confidence scores ($<0.45$).
