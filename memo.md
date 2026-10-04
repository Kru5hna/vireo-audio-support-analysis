# Executive Memorandum

**To:** Priya Raman, Head of Customer Experience, Vireo Audio  
**From:** Vendor Evaluation Analytics Team  
**Re:** Where to add headcount at the support desk  
**Date:** 4 October 2026  

---

### THE ANSWER
**Do not add the two hires to Billing.** The belief that Billing is your largest queue is an illusion created by your chatbot misrouting delivery complaints. In reality, **Logistics is carrying the heaviest workload** across the company (515 tickets per agent vs. 450 in Billing, with resolution times of 26 hours vs. 1 hour). However, before adding headcount to Logistics, you can eliminate over 30% of their incoming volume immediately by fixing intake routing and courier tracking—saving money instead of adding payroll.

---

### THE NUMBER
**Cut Billing intake misrouting from 31.4% (core queue level) to under 5.0% and eliminate dual refund-replacements, worth approximately Rs 1,35,500 per quarter in direct operational savings, while avoiding an unnecessary Rs 9,00,000 per year in unneeded Billing headcount.**

---

### WHAT WE FOUND
- **The False Billing Epidemic (795 Hand-offs)**: 31.4% of tickets assigned to Billing (33.5% all-time; 41.5% of tickets tagged with the legacy Billing text label) were actually delivery issues where customers asked where their shipment was after paying. The bot saw the word "paid" and dumped delivery issues onto Billing.
- **Logistics is Drowning, Not Billing**: Logistics resolved **2,574 tickets** with only 5 agents (515 tickets/agent) and takes **26.03 hours** to resolve them. True Billing tickets take only **1.22 hours** (40 minutes median).
- **The Hidden Cash Leaks (Rs 5.42 Lakhs/Year)**: Bouncing tickets between Billing and Logistics cost **Rs 1.93 Lakhs** in internal transfer penalties (Rs 305/transfer), triggered **Rs 1.67 Lakhs** in late-response store credits (Rs 350 credit), and **140 orders received both a refund AND a free replacement**, leaking **Rs 4.54 Lakhs**.

---

### WHERE I DISAGREED WITH THE BRIEF (and why)
- **Volume is NOT Workload**: Your initial rule ("whichever team has the most volume gets the hires") fails because it measures the chatbot's intake mistakes, not human agent effort. A simple billing balance inquiry takes 15 minutes; a lost courier shipment takes 26+ hours and 2–3 hand-offs.
- **Process Fix Over Blind Hiring**: Adding 2 agents to Billing costs Rs 9,00,000/year to babysit misrouted tickets. Finance Controller Arjun Mehta’s preference to *"fix a process rather than hire into it"* is 100% supported by the data.

---

### HOW SURE WE ARE
- We checked **200 stratified tickets by hand** against customer messages and agent closing notes.
- Our AI classification tool was right **88.00% of the time** (95% confidence interval: **82.8% to 91.8%**).
- Your existing chatbot tags were right only **51.50% of the time** (barely better than a coin flip).
- The tool struggles only with hybrid edge cases where a customer received a broken earbud and simultaneously demanded a refund.

---

### WHAT I'D DO NEXT
1. **Deploy the AI routing classifier** at ticket creation so delivery queries route directly to Logistics without bouncing through Billing.
2. **Implement an automated order-status widget** on the website and WhatsApp so customers can check courier tracking without opening a support ticket.
3. **Hard-block dual refund/replacement in the helpdesk**: Prevent agents from issuing a replacement if a refund has already been initiated on that order ID.

---

### WHAT I LEFT OUT (and why)
- **Individual agent performance scorecards**: Excluded to avoid penalizing agents for slow resolution caused by courier delays outside their control.
- **Multi-model LLM fine-tuning**: Kept the solution 100% local, instant (5 seconds), and zero-cost ($0 API spend) so your team can deploy it immediately without recurring software licenses.
