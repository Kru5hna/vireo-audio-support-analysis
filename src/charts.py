"""
src/charts.py
Generates aesthetic, publication-ready visualization charts:
1. monthly_by_category.png: Monthly volume by true AI category (Jan 2025 - Jun 2026).
2. monthly_by_team.png: Routing demand (assigned queue) vs actual resolution workload.
3. headcount_workload_analysis.png: Multi-metric comparison testing Priya's hiring rule.
4. financial_leakage_and_savings.png: Waterfall of avoidable costs and rupee savings.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

CHARTS_DIR = os.path.join("outputs", "charts")

def generate_all_charts(input_csv="outputs/tickets_categorised.csv"):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    df = pd.read_csv(input_csv)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['year_month'] = df['created_at'].dt.to_period('M').astype(str)

    # Core 18-month filter (Jan 2025 - Jun 2026)
    core = df[df['year_month'] >= '2025-01'].copy()
    print(f"Loaded {len(core)} core tickets for chart generation.")

    # -------------------------------------------------------------
    # Chart 1: Monthly Tickets by Predicted Category
    # -------------------------------------------------------------
    print("Generating Chart 1: monthly_by_category.png...")
    cat_monthly = pd.crosstab(core['year_month'], core['predicted_category'])
    
    # Sort categories by total volume
    sorted_cats = cat_monthly.sum().sort_values(ascending=False).index
    cat_monthly = cat_monthly[sorted_cats]

    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    palette = sns.color_palette("tab10", len(sorted_cats))
    
    cat_monthly.plot(kind='bar', stacked=True, ax=ax, color=palette, width=0.75, edgecolor='white', linewidth=0.5)
    ax.set_title("Vireo Audio: Monthly Support Ticket Volume by AI-Predicted Category (Jan 2025 – Jun 2026)", 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Month", fontsize=11, fontweight='bold')
    ax.set_ylabel("Number of Tickets", fontsize=11, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(title="True Category", bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
    plt.tight_layout()
    chart1_path = os.path.join(CHARTS_DIR, "monthly_by_category.png")
    plt.savefig(chart1_path)
    plt.close()
    print(f"Saved: {chart1_path}")

    # -------------------------------------------------------------
    # Chart 2: Monthly Demand vs True Workload (Assigned vs Resolving)
    # -------------------------------------------------------------
    print("Generating Chart 2: monthly_by_team.png...")
    assigned_monthly = pd.crosstab(core['year_month'], core['assigned_team'])
    resolving_monthly = pd.crosstab(core['year_month'], core['resolving_team'])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), sharey=True, dpi=300)
    
    # Focus comparison on Billing vs Logistics
    teams_to_show = ['Billing', 'Logistics', 'Chat Frontline', 'Email Frontline', 'Returns Desk']
    team_colors = {
        'Billing': '#E63946',
        'Logistics': '#1D3557',
        'Chat Frontline': '#457B9D',
        'Email Frontline': '#A8DADC',
        'Returns Desk': '#F4A261'
    }

    for t in teams_to_show:
        if t in assigned_monthly.columns:
            ax1.plot(assigned_monthly.index, assigned_monthly[t], marker='o', label=t, color=team_colors.get(t, '#888'), linewidth=2)
        if t in resolving_monthly.columns:
            ax2.plot(resolving_monthly.index, resolving_monthly[t], marker='s', label=t, color=team_colors.get(t, '#888'), linewidth=2)

    ax1.set_title("What Priya Saw: Intake Queue Routing (assigned_team)\n[Billing Appears Largest at 22%]", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Month", fontsize=10, fontweight='bold')
    ax1.set_ylabel("Monthly Ticket Volume", fontsize=10, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2.set_title("The Reality: Actual Resolving Team (resolving_team)\n[Logistics Actually Resolves the Most Work!]", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Month", fontsize=10, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(title="Team", bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout()
    chart2_path = os.path.join(CHARTS_DIR, "monthly_by_team.png")
    plt.savefig(chart2_path)
    plt.close()
    print(f"Saved: {chart2_path}")

    # -------------------------------------------------------------
    # Chart 3: Headcount & Workload Analysis (Testing Priya's Rule)
    # -------------------------------------------------------------
    print("Generating Chart 3: headcount_workload_analysis.png...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), dpi=300)

    # Panel A: Tickets Resolved per Agent
    team_agents = {'Chat Frontline': 15, 'Email Frontline': 7, 'Escalations & Warranty': 6, 
                   'Logistics': 5, 'Voice Frontline': 4, 'Billing': 4, 'Returns Desk': 3}
    resolved_counts = core['resolving_team'].value_counts()
    per_agent = {t: resolved_counts.get(t, 0) / count for t, count in team_agents.items()}
    per_agent_s = pd.Series(per_agent).sort_values(ascending=False)

    colors_a = ['#E63946' if t == 'Logistics' else ('#F4A261' if t == 'Billing' else '#457B9D') for t in per_agent_s.index]
    axes[0, 0].bar(per_agent_s.index, per_agent_s.values, color=colors_a, edgecolor='black', alpha=0.85)
    axes[0, 0].set_title("A. Tickets Handled Per Agent (Operational Load)", fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel("Tickets / Agent (18 Months)", fontsize=10)
    axes[0, 0].tick_params(axis='x', rotation=35)
    for i, v in enumerate(per_agent_s.values):
        axes[0, 0].text(i, v + 8, f"{v:.0f}", ha='center', fontweight='bold', fontsize=9)

    # Panel B: Median Resolution Time (Hours)
    res_time = core.groupby('resolving_team')['resolution_hours'].median().sort_values(ascending=False)
    colors_b = ['#1D3557' if t in ['Escalations & Warranty', 'Returns Desk', 'Logistics'] else '#A8DADC' for t in res_time.index]
    axes[0, 1].bar(res_time.index, res_time.values, color=colors_b, edgecolor='black', alpha=0.85)
    axes[0, 1].set_title("B. Median Resolution Time (Hours)\n[Logistics takes 25h vs Billing takes 0.7h]", fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel("Median Hours to Resolution", fontsize=10)
    axes[0, 1].tick_params(axis='x', rotation=35)
    for i, v in enumerate(res_time.values):
        axes[0, 1].text(i, v + 2, f"{v:.1f}h", ha='center', fontweight='bold', fontsize=9)

    # Panel C: SLA Breach Rate by Assigned Queue
    breach_rate = (core.groupby('assigned_team')['is_sla_breach'].mean() * 100).sort_values(ascending=False)
    colors_c = ['#E63946' if t == 'Billing' else '#457B9D' for t in breach_rate.index]
    axes[1, 0].bar(breach_rate.index, breach_rate.values, color=colors_c, edgecolor='black', alpha=0.85)
    axes[1, 0].axhline(core['is_sla_breach'].mean() * 100, color='red', linestyle='--', label=f"Company Avg ({core['is_sla_breach'].mean()*100:.1f}%)")
    axes[1, 0].set_title("C. SLA First-Response Breach Rate (%)\n[Billing has the Worst Breach Rate at 20.5%]", fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel("% Tickets Breaching SLA", fontsize=10)
    axes[1, 0].tick_params(axis='x', rotation=35)
    axes[1, 0].legend()
    for i, v in enumerate(breach_rate.values):
        axes[1, 0].text(i, v + 0.5, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=9)

    # Panel D: The Routing Leak (Where Billing Tickets Actually Went)
    billing_assigned = core[core['assigned_team'] == 'Billing']
    billing_dest = billing_assigned['resolving_team'].value_counts()
    colors_d = ['#457B9D' if t == 'Billing' else '#E63946' for t in billing_dest.index]
    axes[1, 1].pie(billing_dest.values, labels=billing_dest.index, autopct='%1.1f%%', colors=colors_d, 
                   startangle=140, explode=[0.05 if t == 'Logistics' else 0 for t in billing_dest.index])
    axes[1, 1].set_title("D. Billing Intake Queue Breakdown\n[31.4% of Billing Tickets Were Transferred to Logistics!]", fontsize=11, fontweight='bold')

    plt.tight_layout()
    chart3_path = os.path.join(CHARTS_DIR, "headcount_workload_analysis.png")
    plt.savefig(chart3_path)
    plt.close()
    print(f"Saved: {chart3_path}")

    # -------------------------------------------------------------
    # Chart 4: Financial Leakage & Quarterly Savings
    # -------------------------------------------------------------
    print("Generating Chart 4: financial_leakage_and_savings.png...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    savings_categories = [
        "Internal Transfers Avoided\n(Billing -> Logistics @ Rs 305)",
        "SLA Penalties Saved\n(Rs 350 store credit)",
        "Double-Dip Leakage Stopped\n(Refund + Replacement policy fix)",
        "TOTAL QUARTERLY\nPROCESS SAVINGS",
        "Avoided Wrong Hires\n(2 Agents in Billing)"
    ]
    quarterly_amounts = [
        32127,    # Transfers
        27825,    # SLA Penalties
        75596,    # Double dip
        135548,   # Total quarterly process savings
        225000    # Avoided hire (9L/year / 4 quarters = 2.25L/quarter)
    ]
    
    bar_colors = ['#457B9D', '#457B9D', '#457B9D', '#2A9D8F', '#E76F51']
    bars = ax.bar(savings_categories, quarterly_amounts, color=bar_colors, edgecolor='black', width=0.6)
    ax.set_title("Vireo Audio: Quarterly Financial Savings Opportunity (in INR)", fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel("Savings per Quarter (Rs)", fontsize=11, fontweight='bold')
    
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 3500, f"Rs {h:,.0f}", ha='center', va='bottom', fontweight='bold', fontsize=10)

    ax.set_ylim(0, 260000)
    plt.tight_layout()
    chart4_path = os.path.join(CHARTS_DIR, "financial_leakage_and_savings.png")
    plt.savefig(chart4_path)
    plt.close()
    print(f"Saved: {chart4_path}")


if __name__ == '__main__':
    generate_all_charts()
