"""
src/attribute_teams.py
Enriches tickets with agents (resolving team/shift/site), orders (with fallback join),
customers, and products. Computes misrouting, transfer dynamics, and double-dipping leakage.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from src.load_and_clean import load_raw_data, clean_tickets

def attribute_and_enrich(tickets_df, agents_df, orders_df, customers_df, products_df):
    """
    Enriches tickets with:
    1. Agent attribution: resolving team, site, shift, tier.
    2. Fallback order matching (customer_id + product_sku).
    3. Customer profile (city, state, Care+ status).
    4. Product details (family, cost, retail price).
    5. Flags for misrouted tickets and double-dipping violations.
    """
    df = tickets_df.copy()

    # --- 1. Agent Attribution ---
    # agents.csv schema: agent_id, name, site, team, shift, tier, from_date, to_date
    agents_clean = agents_df.rename(columns={
        'name': 'resolving_agent_name',
        'team': 'resolving_team',
        'site': 'agent_site',
        'shift': 'agent_shift',
        'tier': 'agent_tier'
    })
    
    df = df.merge(agents_clean[['agent_id', 'resolving_agent_name', 'resolving_team', 'agent_site', 'agent_shift', 'agent_tier']],
                  on='agent_id', how='left')

    # Flag misrouted tickets where intake queue != resolving team
    df['is_misrouted'] = df['assigned_team'] != df['resolving_team']
    df['routing_hand_off'] = df['assigned_team'] + " -> " + df['resolving_team']

    # --- 2. Order Attribution (with intelligent fallback) ---
    orders_clean = orders_df.rename(columns={
        'channel': 'order_channel',
        'qty': 'order_qty'
    })
    
    # Direct match where order_id exists
    direct_mask = df['order_id'].notnull()
    direct_matched = df[direct_mask].merge(
        orders_clean[['order_id', 'order_date', 'order_channel', 'order_qty', 'order_value_inr', 'lot_code']],
        on='order_id', how='left'
    )
    direct_matched['order_matched_via'] = 'direct'

    # Fallback match where order_id is missing: join on customer_id + product_sku
    fallback_candidates = df[~direct_mask].copy()
    if len(fallback_candidates) > 0:
        orders_clean['order_date_dt'] = pd.to_datetime(orders_clean['order_date'])
        
        fb_merged = fallback_candidates.merge(
            orders_clean[['order_id', 'customer_id', 'sku', 'order_date', 'order_date_dt', 'order_channel', 'order_qty', 'order_value_inr', 'lot_code']],
            left_on=['customer_id', 'product_sku'],
            right_on=['customer_id', 'sku'],
            how='left'
        )
        
        # Pick the order closest to ticket creation
        fb_merged['date_diff_abs'] = (fb_merged['created_at'] - fb_merged['order_date_dt']).abs()
        fb_sorted = fb_merged.sort_values(['ticket_id', 'date_diff_abs'])
        fb_dedup = fb_sorted.drop_duplicates(subset=['ticket_id']).copy()
        
        # Drop redundant columns
        fb_dedup['order_id'] = fb_dedup['order_id_y']
        fb_dedup = fb_dedup.drop(columns=['order_id_x', 'order_id_y', 'sku', 'order_date_dt', 'date_diff_abs'], errors='ignore')
        fb_dedup['order_matched_via'] = 'fallback_sku'
        
        # Recombine
        df = pd.concat([direct_matched, fb_dedup], ignore_index=True)
    else:
        df = direct_matched

    # --- 3. Customer Enrichment ---
    customers_clean = customers_df.rename(columns={
        'name': 'customer_name',
        'city': 'customer_city',
        'state': 'customer_state',
        'care_plus': 'customer_care_plus'
    })
    df = df.merge(customers_clean[['customer_id', 'customer_name', 'customer_city', 'customer_state', 'customer_care_plus']],
                  on='customer_id', how='left')

    # --- 4. Product Enrichment ---
    products_clean = products_df.rename(columns={
        'family': 'product_family',
        'sku': 'prod_sku'
    })
    df = df.merge(products_clean[['prod_sku', 'product_name', 'product_family', 'unit_cost_inr', 'retail_price_inr', 'warranty_months']],
                  left_on='product_sku', right_on='prod_sku', how='left')
    df = df.drop(columns=['prod_sku'], errors='ignore')

    # --- 5. Double-Dipping Audit (Refund + Replacement on same order) ---
    order_refunds = set(df[df['refund_amount_inr'] > 0]['order_id'].dropna())
    order_repls = set(df[df['replacement_issued'] == 'Y']['order_id'].dropna())
    double_dip_orders = order_refunds.intersection(order_repls)
    df['is_double_dipped_order'] = df['order_id'].isin(double_dip_orders)

    return df


if __name__ == '__main__':
    os.makedirs('outputs', exist_ok=True)
    print("Executing Phase 1: Team Attribution and Full Data Enrichment...")
    t, a, o, c, p = load_raw_data()
    clean_t = clean_tickets(t)
    enriched = attribute_and_enrich(clean_t, a, o, c, p)

    output_path = os.path.join('outputs', 'tickets_enriched.csv')
    enriched.to_csv(output_path, index=False)
    print(f"Enriched dataset successfully created at: {output_path} ({len(enriched)} rows, {len(enriched.columns)} columns)")

    # Print Key Metrics
    print("\n" + "="*50)
    print("TEAM ATTRIBUTION & MISROUTING SUMMARY")
    print("="*50)
    print("Unmatched Agents:", enriched['resolving_team'].isnull().sum())
    print("Unmatched Customers:", enriched['customer_name'].isnull().sum())
    print("Unmatched Products:", enriched['product_name'].isnull().sum())
    print("Unmatched Orders (Direct + Fallback):", enriched['order_id'].isnull().sum())
    print(f"Direct Order Matches: {(enriched['order_matched_via'] == 'direct').sum()}")
    print(f"Fallback Order Matches: {(enriched['order_matched_via'] == 'fallback_sku').sum()}")

    print("\n--- Assigned Queue (Bot Routing) vs Resolving Team ---")
    ct = pd.crosstab(enriched['assigned_team'], enriched['resolving_team'], margins=True)
    print(ct)

    print("\n--- Key Misrouting Bottlenecks ---")
    misrouted = enriched[enriched['is_misrouted']]
    print(f"Total Misrouted Tickets: {len(misrouted)} ({len(misrouted)/len(enriched):.2%})")
    print("Top 5 Misrouting Handoffs:")
    print(misrouted['routing_hand_off'].value_counts().head(5))

    print("\n--- Double-Dipping Policy Violation ---")
    dd_orders = enriched[enriched['is_double_dipped_order']]['order_id'].nunique()
    dd_refund_total = enriched[enriched['is_double_dipped_order']]['refund_amount_inr'].sum()
    print(f"Unique Orders with both Refund & Replacement: {dd_orders}")
    print(f"Total Unrecovered Leakage: Rs {dd_refund_total:,.2f}")
