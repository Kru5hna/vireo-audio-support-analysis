"""
src/load_and_clean.py
Loads raw datasets, applies timezone fixes for legacy Freshdesk rows,
calculates SLAs, resolution times, repeat contact flags, and cleans text.
"""

import os
import pandas as pd
import numpy as np

SLA_TARGET_MINUTES = {
    'chat': 15,
    'voice': 120,    # 2 hours
    'social': 240,   # 4 hours
    'email': 480     # 8 hours
}

CHANNEL_COST_INR = {
    'chat': 210,
    'email': 260,
    'voice': 520,
    'social': 240
}

def load_raw_data(data_dir="."):
    """Load all 5 CSV files from the specified directory."""
    paths = {
        'tickets': os.path.join(data_dir, 'tickets.csv'),
        'agents': os.path.join(data_dir, 'agents.csv'),
        'orders': os.path.join(data_dir, 'orders.csv'),
        'customers': os.path.join(data_dir, 'customers.csv'),
        'products': os.path.join(data_dir, 'products.csv')
    }
    
    dfs = {}
    for name, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")
        dfs[name] = pd.read_csv(path, low_memory=False)
    
    return dfs['tickets'], dfs['agents'], dfs['orders'], dfs['customers'], dfs['products']


def clean_tickets(tickets_df):
    """
    Cleans tickets data:
    1. Parses dates.
    2. Adjusts legacy Freshdesk resolved_at by +5:30 (UTC -> IST).
    3. Calculates response and resolution metrics.
    4. Evaluates SLA breaches based on policy targets.
    5. Flags repeat contacts (within 30 days of prior resolution).
    """
    df = tickets_df.copy()

    # 1. Parse timestamps
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['first_response_at'] = pd.to_datetime(df['first_response_at'])
    df['resolved_at'] = pd.to_datetime(df['resolved_at'])

    # 2. Fix timezone anomaly: legacy_fd resolution timestamps were stored in UTC
    legacy_mask = df['source_system'] == 'legacy_fd'
    df.loc[legacy_mask, 'resolved_at'] = df.loc[legacy_mask, 'resolved_at'] + pd.Timedelta(hours=5, minutes=30)

    # 3. Calculate handle and resolution metrics
    df['first_response_minutes'] = (df['first_response_at'] - df['created_at']).dt.total_seconds() / 60.0
    df['resolution_hours'] = (df['resolved_at'] - df['created_at']).dt.total_seconds() / 3600.0

    # 4. SLA target mapping & breach evaluation
    df['sla_target_minutes'] = df['channel'].map(SLA_TARGET_MINUTES)
    df['is_sla_breach'] = df['first_response_minutes'] > df['sla_target_minutes']
    df['sla_breach_penalty_inr'] = np.where(df['is_sla_breach'], 350.0, 0.0)

    # 5. Clean text fields
    df['customer_message'] = df['customer_message'].fillna('').astype(str).str.strip()
    df['agent_notes'] = df['agent_notes'].fillna('').astype(str).str.strip()

    # 6. Flag repeat contacts (policy §10: contact within 30 days of resolution)
    df = df.sort_values(['customer_id', 'created_at']).reset_index(drop=True)
    df['prev_resolved_at'] = df.groupby('customer_id')['resolved_at'].shift(1)
    df['days_since_prev_resolution'] = (df['created_at'] - df['prev_resolved_at']).dt.total_seconds() / 86400.0
    df['is_repeat_contact'] = df['days_since_prev_resolution'].between(0.0, 30.0)
    df['repeat_contact_cost_inr'] = np.where(df['is_repeat_contact'], df['channel'].map(CHANNEL_COST_INR), 0.0)

    # 7. Transfers handling: Freshdesk had no transfers counter (blank, not zero)
    df['transfers_recorded'] = df['transfers'].fillna(0).astype(int)

    return df


if __name__ == '__main__':
    print("Loading and cleaning raw data...")
    t, a, o, c, p = load_raw_data()
    clean_t = clean_tickets(t)
    print(f"Tickets cleaned: {len(clean_t)} rows.")
    print(f"SLA Breaches: {clean_t['is_sla_breach'].sum()} ({clean_t['is_sla_breach'].mean():.2%})")
    print(f"Total SLA Breach Penalty: Rs {clean_t['sla_breach_penalty_inr'].sum():,.2f}")
    print(f"Repeat Contacts (30d): {clean_t['is_repeat_contact'].sum()} ({clean_t['is_repeat_contact'].mean():.2%})")
    print(f"Total Repeat Contact Cost: Rs {clean_t['repeat_contact_cost_inr'].sum():,.2f}")
    print("Verification: Negative resolution hours count =", (clean_t['resolution_hours'] < 0).sum())
