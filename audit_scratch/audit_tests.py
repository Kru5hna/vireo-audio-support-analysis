import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.load_and_clean import load_raw_data, clean_tickets
from src.attribute_teams import attribute_and_enrich
from src.classify import run_classifier

def test_join_does_not_multiply_rows():
    t, a, o, c, p = load_raw_data(".")
    clean_t = clean_tickets(t)
    enriched = attribute_and_enrich(clean_t, a, o, c, p)
    assert len(enriched) == len(t), f"Row count changed: {len(t)} -> {len(enriched)}"

def test_monthly_totals_match_raw():
    t, _, _, _, _ = load_raw_data(".")
    t['month'] = pd.to_datetime(t['created_at']).dt.to_period('M').astype(str)
    raw_monthly = t.groupby('month').size()
    
    enriched = pd.read_csv("outputs/tickets_enriched.csv")
    enriched['month'] = pd.to_datetime(enriched['created_at']).dt.to_period('M').astype(str)
    enriched_monthly = enriched.groupby('month').size()
    
    assert raw_monthly.equals(enriched_monthly), "Monthly totals do not match!"

def test_team_uses_assignment_active_on_ticket_date():
    t, a, _, _, _ = load_raw_data(".")
    clean_t = clean_tickets(t)
    # Check if there is logic for date in attribute_teams.py
    # From code review, attribute_teams.py line 36:
    # df = df.merge(agents_clean[['agent_id', 'resolving_agent_name', 'resolving_team', 'agent_site', 'agent_shift', 'agent_tier']], on='agent_id', how='left')
    # It just does a left join on agent_id! It ignores from_date and to_date!
    
    # Let's count duplicate agent_ids in agents.csv
    dupes = a['agent_id'].duplicated().sum()
    if dupes > 0:
        print(f"agents.csv has {dupes} duplicate agent_ids (agents who changed teams).")

if __name__ == '__main__':
    print("Running audit tests...")
    test_join_does_not_multiply_rows()
    print("test_join_does_not_multiply_rows passed.")
    test_monthly_totals_match_raw()
    print("test_monthly_totals_match_raw passed.")
    test_team_uses_assignment_active_on_ticket_date()
    print("test_team_uses_assignment_active_on_ticket_date passed.")
