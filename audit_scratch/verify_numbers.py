"""
audit_scratch/verify_numbers.py
Independent re-derivation of all rupee figures from raw data + policy costs.
"""
import pandas as pd
import numpy as np

# Load the categorised dataset (final output)
df = pd.read_csv("outputs/tickets_categorised.csv")
df['created_at'] = pd.to_datetime(df['created_at'])

# Policy costs
TRANSFER_COST = 305.0
SLA_BREACH_PENALTY = 350.0

# Core 18-month period
core = df[df['created_at'] >= '2025-01-01'].copy()
num_quarters = 6.0

print("="*60)
print("INDEPENDENT FINANCIAL VERIFICATION")
print("="*60)

# 1. Billing Misrouting
bp_assigned = core[core['assigned_team'] == 'Billing']
total_bp = len(bp_assigned)
misrouted_bp = len(bp_assigned[bp_assigned['resolving_team'] != 'Billing'])
print(f"\nBilling assigned tickets: {total_bp}")
print(f"Billing misrouted (resolved by other team): {misrouted_bp}")
print(f"Misrouting rate: {misrouted_bp/total_bp:.1%}")

# Transfers from Billing
bp_transfers = bp_assigned['transfers_recorded'].sum()
bp_transfer_cost = bp_transfers * TRANSFER_COST
bp_transfer_quarterly = bp_transfer_cost / num_quarters
print(f"\nBilling transfers total: {bp_transfers}")
print(f"Transfer cost total: Rs {bp_transfer_cost:,.2f}")
print(f"Transfer cost quarterly: Rs {bp_transfer_quarterly:,.2f}")

# SLA Breaches on Billing
bp_breaches = bp_assigned['is_sla_breach'].sum()
bp_breach_cost = bp_breaches * SLA_BREACH_PENALTY
bp_breach_quarterly = bp_breach_cost / num_quarters
print(f"\nBilling SLA breaches: {bp_breaches}")
print(f"Breach penalty total: Rs {bp_breach_cost:,.2f}")
print(f"Breach penalty quarterly: Rs {bp_breach_quarterly:,.2f}")

# Double-dipping
dd = core[core['is_double_dipped_order'] == True]
dd_orders = dd['order_id'].nunique()
dd_leakage_total = dd['refund_amount_inr'].sum()
dd_leakage_quarterly = dd_leakage_total / num_quarters
print(f"\nDouble-dip orders: {dd_orders}")
print(f"Double-dip leakage total: Rs {dd_leakage_total:,.2f}")
print(f"Double-dip leakage quarterly: Rs {dd_leakage_quarterly:,.2f}")

# Total
total_quarterly = bp_transfer_quarterly + bp_breach_quarterly + dd_leakage_quarterly
total_annual = total_quarterly * 4
print(f"\n{'='*60}")
print(f"TOTAL QUARTERLY PROCESS SAVINGS: Rs {total_quarterly:,.2f}")
print(f"TOTAL ANNUAL PROCESS SAVINGS: Rs {total_annual:,.2f}")

# Compare with claimed values
print(f"\n{'='*60}")
print("COMPARISON WITH MEMO CLAIMS:")
print(f"  Claimed quarterly savings: Rs 1,35,500")
print(f"  Computed quarterly savings: Rs {total_quarterly:,.2f}")
print(f"  Match: {'YES' if abs(total_quarterly - 135500) < 500 else 'CLOSE' if abs(total_quarterly - 135500) < 2000 else 'NO'}")

# Headcount analysis
print(f"\n{'='*60}")
print("HEADCOUNT VERIFICATION:")
team_agents = {'Chat Frontline': 15, 'Email Frontline': 7, 'Escalations & Warranty': 6, 
               'Logistics': 5, 'Voice Frontline': 4, 'Billing': 4, 'Returns Desk': 3}
resolved = core['resolving_team'].value_counts()
for team, agents in sorted(team_agents.items(), key=lambda x: resolved.get(x[0], 0)/x[1], reverse=True):
    vol = resolved.get(team, 0)
    per_agent = vol / agents
    res_time = core[core['resolving_team'] == team]['resolution_hours'].median()
    print(f"  {team}: {vol} resolved, {per_agent:.1f}/agent, median {res_time:.2f}h")

# Row count verification
print(f"\n{'='*60}")
print("ROW COUNT VERIFICATION:")
raw_tickets = pd.read_csv("tickets.csv")
enriched = pd.read_csv("outputs/tickets_enriched.csv")
categorised = pd.read_csv("outputs/tickets_categorised.csv")
print(f"  Raw tickets.csv: {len(raw_tickets)}")
print(f"  tickets_enriched.csv: {len(enriched)}")
print(f"  tickets_categorised.csv: {len(categorised)}")
print(f"  Row preservation: {'PASS' if len(raw_tickets) == len(enriched) == len(categorised) else 'FAIL'}")

# Check 'Other / Unclear' category
print(f"\n{'='*60}")
print("OTHER/UNCLEAR CATEGORY CHECK:")
other_count = (categorised['predicted_category'] == 'Other / Unclear').sum()
print(f"  Tickets classified as 'Other / Unclear': {other_count}")
print(f"  Claimed 0% Other bucket: {'CONFIRMED' if other_count == 0 else 'FAILED - ' + str(other_count) + ' tickets!'}")
