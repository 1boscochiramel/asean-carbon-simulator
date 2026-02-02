"""
ASEAN Carbon Integration Simulator
Based on: "Carbon Pricing Integration for ASEAN's Petroleum Refining Sector"
Author: Bosco Chiramel

Session 1: Core App + Country Dashboard + Carbon Liability Calculator
Session 2: Integration Pathway + Malaysia Decision Analyzer + Investment Calculator
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="ASEAN Carbon Integration Simulator",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-green: #00A86B;
        --secondary-blue: #1E3A5F;
        --accent-orange: #FF6B35;
        --light-bg: #F8FAFC;
        --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1E3A5F 0%, #2D5A87 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #B8D4E8;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-green);
        margin-bottom: 1rem;
    }
    
    .metric-card.warning {
        border-left-color: var(--accent-orange);
    }
    
    .metric-card.info {
        border-left-color: var(--secondary-blue);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A5F;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Country flag badges */
    .country-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-sg { background: #EF4444; color: white; }
    .badge-th { background: #3B82F6; color: white; }
    .badge-id { background: #EF4444; color: white; }
    .badge-my { background: #FCD34D; color: #1E3A5F; }
    .badge-vn { background: #EF4444; color: white; }
    
    /* Data table styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #F8FAFC;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #F1F5F9;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1E3A5F;
        color: white;
    }
    
    /* Key insight boxes */
    .insight-box {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #F59E0B;
        margin: 1rem 0;
    }
    
    .insight-box h4 {
        color: #92400E;
        margin-bottom: 0.5rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #94A3B8;
        padding: 2rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA DEFINITIONS (From Paper)
# ============================================================================

# Country-level data
COUNTRY_DATA = {
    'Singapore': {
        'flag': '🇸🇬',
        'refineries': 3,
        'capacity_kbpd': 1512,  # thousand barrels per day
        'govt_ownership': 0.13,
        'carbon_price_2024': 59,
        'carbon_price_2030': 75,
        'ets_status': 'Operational',
        'ets_launch_year': 2019,
        'coverage_pct': 80,
        'total_liability_b': 5.2,
        'govt_exposure_b': 0.9,
        'avg_refinery_age': 45
    },
    'Thailand': {
        'flag': '🇹🇭',
        'refineries': 6,
        'capacity_kbpd': 1240,
        'govt_ownership': 0.36,
        'carbon_price_2024': 35,
        'carbon_price_2030': 50,
        'ets_status': 'Development',
        'ets_launch_year': 2025,
        'coverage_pct': 60,
        'total_liability_b': 4.1,
        'govt_exposure_b': 1.9,
        'avg_refinery_age': 38
    },
    'Indonesia': {
        'flag': '🇮🇩',
        'refineries': 8,
        'capacity_kbpd': 1050,
        'govt_ownership': 1.00,
        'carbon_price_2024': 25,
        'carbon_price_2030': 35,
        'ets_status': 'Operational',
        'ets_launch_year': 2023,
        'coverage_pct': 50,
        'total_liability_b': 7.1,
        'govt_exposure_b': 7.1,
        'avg_refinery_age': 52
    },
    'Malaysia': {
        'flag': '🇲🇾',
        'refineries': 5,
        'capacity_kbpd': 612,
        'govt_ownership': 0.80,
        'carbon_price_2024': 0,  # Voluntary only
        'carbon_price_2030': 15,  # Projected
        'ets_status': 'Voluntary',
        'ets_launch_year': 2030,  # Projected
        'coverage_pct': 30,
        'total_liability_b': 2.7,
        'govt_exposure_b': 2.7,
        'avg_refinery_age': 33
    },
    'Vietnam': {
        'flag': '🇻🇳',
        'refineries': 3,
        'capacity_kbpd': 346,
        'govt_ownership': 0.71,
        'carbon_price_2024': 20,
        'carbon_price_2030': 40,
        'ets_status': 'Development',
        'ets_launch_year': 2028,
        'coverage_pct': 45,
        'total_liability_b': 1.2,
        'govt_exposure_b': 0.8,
        'avg_refinery_age': 10
    }
}

# Refinery-level data
REFINERY_DATA = [
    # Singapore
    {'country': 'Singapore', 'name': 'ExxonMobil Jurong', 'capacity_kbpd': 592, 'owner': 'ExxonMobil', 'govt_owned': False, 'age_years': 55, 'complexity': 'High'},
    {'country': 'Singapore', 'name': 'Shell Pulau Bukom', 'capacity_kbpd': 500, 'owner': 'Shell', 'govt_owned': False, 'age_years': 62, 'complexity': 'High'},
    {'country': 'Singapore', 'name': 'SRC Jurong Island', 'capacity_kbpd': 420, 'owner': 'SPC/PetroChina', 'govt_owned': True, 'age_years': 18, 'complexity': 'High'},
    
    # Thailand
    {'country': 'Thailand', 'name': 'Thai Oil Sriracha', 'capacity_kbpd': 275, 'owner': 'PTT Group', 'govt_owned': True, 'age_years': 58, 'complexity': 'High'},
    {'country': 'Thailand', 'name': 'IRPC Rayong', 'capacity_kbpd': 215, 'owner': 'PTT Group', 'govt_owned': True, 'age_years': 42, 'complexity': 'Medium'},
    {'country': 'Thailand', 'name': 'Star Petroleum Map Ta Phut', 'capacity_kbpd': 165, 'owner': 'Chevron/PTT', 'govt_owned': True, 'age_years': 28, 'complexity': 'High'},
    {'country': 'Thailand', 'name': 'ESSO Sriracha', 'capacity_kbpd': 174, 'owner': 'ExxonMobil', 'govt_owned': False, 'age_years': 55, 'complexity': 'Medium'},
    {'country': 'Thailand', 'name': 'Bangchak Bangkok', 'capacity_kbpd': 120, 'owner': 'Bangchak', 'govt_owned': False, 'age_years': 40, 'complexity': 'Medium'},
    {'country': 'Thailand', 'name': 'PTT GC Rayong', 'capacity_kbpd': 291, 'owner': 'PTT Group', 'govt_owned': True, 'age_years': 12, 'complexity': 'High'},
    
    # Indonesia
    {'country': 'Indonesia', 'name': 'Pertamina Cilacap', 'capacity_kbpd': 348, 'owner': 'Pertamina', 'govt_owned': True, 'age_years': 48, 'complexity': 'High'},
    {'country': 'Indonesia', 'name': 'Pertamina Balikpapan', 'capacity_kbpd': 260, 'owner': 'Pertamina', 'govt_owned': True, 'age_years': 102, 'complexity': 'Medium'},
    {'country': 'Indonesia', 'name': 'Pertamina Dumai', 'capacity_kbpd': 170, 'owner': 'Pertamina', 'govt_owned': True, 'age_years': 52, 'complexity': 'Medium'},
    {'country': 'Indonesia', 'name': 'Pertamina Balongan', 'capacity_kbpd': 125, 'owner': 'Pertamina', 'govt_owned': True, 'age_years': 30, 'complexity': 'High'},
    {'country': 'Indonesia', 'name': 'Pertamina Plaju', 'capacity_kbpd': 118, 'owner': 'Pertamina', 'govt_owned': True, 'age_years': 89, 'complexity': 'Low'},
    {'country': 'Indonesia', 'name': 'Pertamina Kasim', 'capacity_kbpd': 10, 'owner': 'Pertamina', 'govt_owned': True, 'age_years': 25, 'complexity': 'Low'},
    {'country': 'Indonesia', 'name': 'Trans Pacific Tuban', 'capacity_kbpd': 100, 'owner': 'TPPI', 'govt_owned': True, 'age_years': 18, 'complexity': 'Medium'},
    {'country': 'Indonesia', 'name': 'Pertamina Sungai Pakning', 'capacity_kbpd': 50, 'owner': 'Pertamina', 'govt_owned': True, 'age_years': 55, 'complexity': 'Low'},
    
    # Malaysia
    {'country': 'Malaysia', 'name': 'Petronas RAPID Pengerang', 'capacity_kbpd': 300, 'owner': 'Petronas', 'govt_owned': True, 'age_years': 5, 'complexity': 'High'},
    {'country': 'Malaysia', 'name': 'Petronas Melaka I', 'capacity_kbpd': 100, 'owner': 'Petronas', 'govt_owned': True, 'age_years': 30, 'complexity': 'Medium'},
    {'country': 'Malaysia', 'name': 'Petronas Melaka II', 'capacity_kbpd': 100, 'owner': 'Petronas', 'govt_owned': True, 'age_years': 25, 'complexity': 'Medium'},
    {'country': 'Malaysia', 'name': 'Petronas Kertih', 'capacity_kbpd': 47, 'owner': 'Petronas', 'govt_owned': True, 'age_years': 40, 'complexity': 'Low'},
    {'country': 'Malaysia', 'name': 'Hengyuan Port Dickson', 'capacity_kbpd': 156, 'owner': 'Hengyuan', 'govt_owned': False, 'age_years': 60, 'complexity': 'Medium'},
    
    # Vietnam
    {'country': 'Vietnam', 'name': 'Nghi Son', 'capacity_kbpd': 200, 'owner': 'NSRP JV', 'govt_owned': True, 'age_years': 6, 'complexity': 'High'},
    {'country': 'Vietnam', 'name': 'Dung Quat', 'capacity_kbpd': 130, 'owner': 'Binh Son', 'govt_owned': True, 'age_years': 15, 'complexity': 'Medium'},
    {'country': 'Vietnam', 'name': 'Long Son (planned)', 'capacity_kbpd': 200, 'owner': 'SCG/PVN', 'govt_owned': True, 'age_years': 0, 'complexity': 'High'},
]

# Integration pathway milestones
INTEGRATION_MILESTONES = [
    {'phase': 'Phase 1', 'year': 2025, 'milestone': 'ASEAN Carbon Coordination Body Launch', 'status': 'Pending', 'quarter': 'Q2'},
    {'phase': 'Phase 1', 'year': 2025, 'milestone': 'Malaysia Policy Decision Deadline', 'status': 'Critical', 'quarter': 'Q3'},
    {'phase': 'Phase 1', 'year': 2027, 'milestone': 'MRV Standards Harmonization Complete', 'status': 'Pending', 'quarter': 'Q4'},
    {'phase': 'Phase 1', 'year': 2028, 'milestone': 'Singapore-Thailand Bilateral Linkage', 'status': 'Pending', 'quarter': 'Q1'},
    {'phase': 'Phase 2', 'year': 2030, 'milestone': 'All Countries Mandatory Pricing', 'status': 'Pending', 'quarter': 'Q1'},
    {'phase': 'Phase 2', 'year': 2030, 'milestone': 'Informal $20/t Price Floor', 'status': 'Pending', 'quarter': 'Q2'},
    {'phase': 'Phase 2', 'year': 2032, 'milestone': 'Indonesia Joins Linkage', 'status': 'Pending', 'quarter': 'Q1'},
    {'phase': 'Phase 2', 'year': 2032, 'milestone': 'Malaysia Integration (if committed)', 'status': 'Conditional', 'quarter': 'Q3'},
    {'phase': 'Phase 2', 'year': 2035, 'milestone': '$40/t Price Floor Binding', 'status': 'Pending', 'quarter': 'Q1'},
    {'phase': 'Phase 3', 'year': 2035, 'milestone': 'Vietnam Tier 1 Graduation', 'status': 'Pending', 'quarter': 'Q2'},
    {'phase': 'Phase 3', 'year': 2040, 'milestone': 'Price Spread Narrows to 1.5×', 'status': 'Pending', 'quarter': 'Q1'},
    {'phase': 'Phase 3', 'year': 2045, 'milestone': 'Single ASEAN Carbon Market ($70-95/t)', 'status': 'Pending', 'quarter': 'Q1'},
]

# Investment requirements (from paper - $229M total)
INVESTMENT_REQUIREMENTS = [
    {'component': 'MRV Infrastructure', 'amount_m': 85, 'timeline': '2025-2028', 'description': 'Monitoring, reporting, verification systems across 5 countries'},
    {'component': 'Registry Systems', 'amount_m': 45, 'timeline': '2025-2027', 'description': 'National carbon registries and linkage infrastructure'},
    {'component': 'Capacity Building', 'amount_m': 35, 'timeline': '2025-2030', 'description': 'Training programs for regulators and industry'},
    {'component': 'Market Infrastructure', 'amount_m': 40, 'timeline': '2027-2030', 'description': 'Trading platforms and settlement systems'},
    {'component': 'Coordination Body', 'amount_m': 24, 'timeline': '2025-2030', 'description': 'ASEAN Carbon Pricing Coordination Body operations'},
]

# Funding sources
FUNDING_SOURCES = [
    {'source': 'JETP Expansion', 'amount_m': 80, 'percentage': 35, 'status': 'Proposed'},
    {'source': 'National Budgets', 'amount_m': 90, 'percentage': 39, 'status': 'Required'},
    {'source': 'Carbon Auction Revenues', 'amount_m': 29, 'percentage': 13, 'status': 'Projected'},
    {'source': 'Industry Contributions', 'amount_m': 15, 'percentage': 7, 'status': 'Negotiating'},
    {'source': 'International Climate Finance', 'amount_m': 15, 'percentage': 7, 'status': 'Available'},
]

# Malaysia scenario comparison
MALAYSIA_SCENARIOS = {
    'commitment': {
        'name': 'Early Commitment (Q3 2025)',
        'implementation_cost': 185,  # $M
        'ets_launch': 2028,
        'integration_year': 2032,
        'technology_gap': 0,
        'stranded_asset_risk': 'Low',
        'cbam_exposure': 'None',
        'total_cost': 185,
        'benefits': [
            '3-year implementation window',
            'Regional technology cooperation access',
            'Investment confidence restored',
            'JETP funding eligibility',
            'First-mover advantage in green refining'
        ],
        'risks': [
            'Short-term competitiveness pressure',
            'Fiscal adjustment required',
            'Industry transition costs'
        ]
    },
    'delay': {
        'name': 'Delayed Action (Post-2027)',
        'implementation_cost': 250,  # Higher due to catch-up
        'ets_launch': 2032,
        'integration_year': 2038,
        'technology_gap': 7,  # years behind
        'stranded_asset_risk': 'High',
        'cbam_exposure': '$500M-1.5B annually',
        'total_cost': 3500,  # $2-5B range midpoint
        'benefits': [
            'Short-term cost avoidance',
            'More time for preparation'
        ],
        'risks': [
            'Excluded from regional integration',
            'Technology gap widens 5-10 years',
            'CBAM charges from ASEAN neighbors post-2035',
            'Lost investment opportunities',
            'Stranded asset risk for Petronas',
            'Reputational damage'
        ]
    }
}

# Technology cooperation opportunities
TECH_COOPERATION = [
    {
        'name': 'CCS Infrastructure Sharing',
        'investment_feasibility': 50,
        'investment_pilots': 500,
        'investment_commercial': 7500,
        'timeline_feasibility': '2026-2028',
        'timeline_pilots': '2028-2032',
        'timeline_commercial': '2032-2040',
        'cost_reduction': '30-50%',
        'lead_countries': ['Indonesia', 'Malaysia'],
        'description': 'Cross-border CO2 transport and storage in depleted oil/gas fields'
    },
    {
        'name': 'Green Hydrogen Corridors',
        'investment_feasibility': 30,
        'investment_pilots': 200,
        'investment_commercial': 3000,
        'timeline_feasibility': '2026-2028',
        'timeline_pilots': '2028-2032',
        'timeline_commercial': '2035-2040',
        'cost_reduction': '25-40%',
        'lead_countries': ['Vietnam', 'Thailand'],
        'description': 'Regional hydrogen production leveraging renewable resources'
    },
    {
        'name': 'Regional Transition Fund',
        'investment_feasibility': 10,
        'investment_pilots': 0,
        'investment_commercial': 4000,
        'timeline_feasibility': '2025-2026',
        'timeline_pilots': 'N/A',
        'timeline_commercial': '2028-2035',
        'cost_reduction': 'Enabling',
        'lead_countries': ['All ASEAN-5'],
        'description': '$3-5B fund pooling JETP, auction revenues, MDB financing',
        'allocation': {'Malaysia': 30, 'Indonesia': 30, 'Vietnam': 25, 'Thailand': 10, 'Singapore': 5}
    }
]

# Risk assessment matrix
RISK_MATRIX = [
    {'risk': 'Political Turnover', 'probability': 40, 'impact': 'High', 'mitigation': 'ASEAN-level agreements, private sector engagement'},
    {'risk': 'Economic Crisis', 'probability': 20, 'impact': 'Medium', 'mitigation': 'Flexible price floors, counter-cyclical support'},
    {'risk': 'Malaysia Non-cooperation', 'probability': 30, 'impact': 'High', 'mitigation': 'JETP support offers, eventual CBAM pressure'},
    {'risk': 'Technology Delays', 'probability': 25, 'impact': 'Medium', 'mitigation': 'Multiple technology pathways, regional cooperation'},
    {'risk': 'Carbon Price Volatility', 'probability': 35, 'impact': 'Medium', 'mitigation': 'Price corridors, market stability reserves'},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_carbon_liability(country, carbon_price, years=25, discount_rate=0.05):
    """Calculate NPV of carbon liability for a country's refinery sector."""
    data = COUNTRY_DATA[country]
    
    # Emissions intensity: ~0.14 tCO2/barrel (from paper)
    emissions_intensity = 0.14
    
    # Daily emissions (tonnes)
    daily_emissions = data['capacity_kbpd'] * 1000 * emissions_intensity
    
    # Annual emissions
    annual_emissions = daily_emissions * 365 / 1_000_000  # Million tonnes
    
    # Calculate NPV of liability
    npv = 0
    for year in range(years):
        # Price escalation assumption
        price = carbon_price * (1.03 ** year)  # 3% annual increase
        annual_cost = annual_emissions * price * 1_000_000  # Convert to dollars
        npv += annual_cost / ((1 + discount_rate) ** year)
    
    return npv / 1_000_000_000  # Return in billions


def get_divergence_metrics():
    """Calculate policy divergence metrics."""
    prices = [d['carbon_price_2024'] for d in COUNTRY_DATA.values() if d['carbon_price_2024'] > 0]
    years = [d['ets_launch_year'] for d in COUNTRY_DATA.values()]
    
    return {
        'timeline_spread': max(years) - min(years),
        'price_spread': max(prices) / min(prices) if min(prices) > 0 else float('inf'),
        'max_price': max(prices),
        'min_price': min([p for p in prices if p > 0])
    }


def create_country_comparison_df():
    """Create DataFrame for country comparison."""
    rows = []
    for country, data in COUNTRY_DATA.items():
        rows.append({
            'Country': f"{data['flag']} {country}",
            'Refineries': data['refineries'],
            'Capacity (kbpd)': data['capacity_kbpd'],
            'Govt Ownership': f"{data['govt_ownership']*100:.0f}%",
            'Carbon Price ($/t)': f"${data['carbon_price_2024']}" if data['carbon_price_2024'] > 0 else "Voluntary",
            'ETS Status': data['ets_status'],
            'Launch Year': data['ets_launch_year'],
            'Total Liability ($B)': f"${data['total_liability_b']:.1f}B",
            'Govt Exposure ($B)': f"${data['govt_exposure_b']:.1f}B"
        })
    return pd.DataFrame(rows)


def get_malaysia_countdown():
    """Calculate days until Malaysia Q3 2025 deadline."""
    deadline = datetime(2025, 9, 30)  # End of Q3 2025
    today = datetime.now()
    delta = deadline - today
    return max(0, delta.days)


def calculate_integration_roi():
    """Calculate ROI metrics for integration investment."""
    total_investment = sum(i['amount_m'] for i in INVESTMENT_REQUIREMENTS)
    
    # Benefits from paper
    annual_operational_savings = 18  # $M/year
    annual_market_efficiency = 50   # $M/year
    climate_benefits_npv = 200      # $M NPV
    liability_managed = 20300       # $M (total regional liability)
    
    # 10-year benefit calculation
    years = 10
    total_benefits = (annual_operational_savings + annual_market_efficiency) * years + climate_benefits_npv
    
    return {
        'total_investment': total_investment,
        'total_benefits': total_benefits,
        'benefit_cost_ratio': total_benefits / total_investment,
        'annual_savings': annual_operational_savings + annual_market_efficiency,
        'payback_years': total_investment / (annual_operational_savings + annual_market_efficiency)
    }


def get_phase_progress(current_year=2025):
    """Calculate progress through integration phases."""
    phases = {
        'Phase 1': {'start': 2025, 'end': 2028, 'name': 'Foundation'},
        'Phase 2': {'start': 2028, 'end': 2035, 'name': 'Convergence'},
        'Phase 3': {'start': 2035, 'end': 2045, 'name': 'Full Integration'}
    }
    
    results = []
    for phase, info in phases.items():
        if current_year < info['start']:
            progress = 0
            status = 'Not Started'
        elif current_year >= info['end']:
            progress = 100
            status = 'Complete'
        else:
            progress = ((current_year - info['start']) / (info['end'] - info['start'])) * 100
            status = 'In Progress'
        
        results.append({
            'phase': phase,
            'name': info['name'],
            'start': info['start'],
            'end': info['end'],
            'progress': progress,
            'status': status
        })
    
    return results


def simulate_price_convergence(scenario='baseline'):
    """Simulate carbon price convergence under different scenarios."""
    years = list(range(2024, 2051))
    
    # Base trajectories from paper
    trajectories = {
        'Singapore': {'2024': 59, '2030': 75, '2045': 95},
        'Thailand': {'2024': 35, '2030': 50, '2045': 85},
        'Indonesia': {'2024': 25, '2030': 35, '2045': 75},
        'Malaysia': {'2024': 0, '2030': 15, '2045': 70},
        'Vietnam': {'2024': 20, '2030': 40, '2045': 80}
    }
    
    if scenario == 'accelerated':
        # Faster convergence
        for country in trajectories:
            trajectories[country]['2030'] *= 1.2
            trajectories[country]['2045'] *= 1.1
    elif scenario == 'delayed':
        # Slower convergence
        for country in trajectories:
            trajectories[country]['2030'] *= 0.8
            trajectories[country]['2045'] *= 0.9
    
    results = []
    for year in years:
        row = {'year': year}
        for country, prices in trajectories.items():
            if year <= 2024:
                row[country] = prices['2024']
            elif year <= 2030:
                # Linear interpolation to 2030
                progress = (year - 2024) / 6
                row[country] = prices['2024'] + (prices['2030'] - prices['2024']) * progress
            elif year <= 2045:
                # Linear interpolation to 2045
                progress = (year - 2030) / 15
                row[country] = prices['2030'] + (prices['2045'] - prices['2030']) * progress
            else:
                row[country] = prices['2045']
        
        # Calculate spread
        active_prices = [v for k, v in row.items() if k != 'year' and v > 0]
        row['spread'] = max(active_prices) / min(active_prices) if min(active_prices) > 0 else 0
        results.append(row)
    
    return pd.DataFrame(results)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌏 ASEAN Carbon Integration Simulator</h1>
        <p>Analyzing $20.3B Carbon Liability Across 25 Refineries in 5 Countries</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/ASEAN_Emblem.svg/200px-ASEAN_Emblem.svg.png", width=100)
        st.markdown("### 📊 Simulation Parameters")
        
        # Carbon price scenarios
        st.markdown("#### Carbon Price Scenario")
        price_scenario = st.selectbox(
            "Select Scenario",
            ["Current Policy", "Accelerated Transition", "Delayed Action", "Custom"],
            help="Choose a carbon price trajectory scenario"
        )
        
        if price_scenario == "Custom":
            custom_price_2030 = st.slider("2030 Average Price ($/tCO2e)", 20, 100, 50)
            custom_price_2050 = st.slider("2050 Average Price ($/tCO2e)", 50, 200, 95)
        
        st.markdown("#### Discount Rate")
        discount_rate = st.slider("NPV Discount Rate (%)", 3.0, 10.0, 5.0, 0.5) / 100
        
        st.markdown("#### Analysis Period")
        analysis_years = st.slider("Years (2025 onwards)", 10, 30, 25)
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("""
        Based on research by **Bosco Chiramel**
        
        *"Carbon Pricing Integration for ASEAN's Petroleum Refining Sector"*
        
        Key findings:
        - $20.3B total regional liability
        - $8.4B government exposure
        - 11-year policy timeline gap
        - 4× carbon price differential
        """)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Regional Overview",
        "💰 Carbon Liability Calculator",
        "📈 Policy Divergence",
        "🏭 Refinery Analysis",
        "🛤️ Integration Pathway",
        "🇲🇾 Malaysia Decision",
        "💵 Investment Analysis"
    ])
    
    # ========================================================================
    # TAB 1: REGIONAL OVERVIEW
    # ========================================================================
    with tab1:
        st.markdown("## Regional Overview: ASEAN-5 Refining Sector")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Total Refineries</div>
                <div class="metric-value">25</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card info">
                <div class="metric-label">Combined Capacity</div>
                <div class="metric-value">4.76M bpd</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card warning">
                <div class="metric-label">Total Carbon Liability</div>
                <div class="metric-value">$20.3B</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card warning">
                <div class="metric-label">Govt Fiscal Exposure</div>
                <div class="metric-value">$8.4B</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Country comparison chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Refining Capacity by Country")
            
            capacity_data = pd.DataFrame([
                {'Country': f"{d['flag']} {c}", 'Capacity': d['capacity_kbpd']}
                for c, d in COUNTRY_DATA.items()
            ])
            
            fig = px.bar(
                capacity_data,
                x='Country',
                y='Capacity',
                color='Country',
                color_discrete_sequence=['#EF4444', '#3B82F6', '#EF4444', '#FCD34D', '#EF4444']
            )
            fig.update_layout(
                showlegend=False,
                yaxis_title="Capacity (kbpd)",
                xaxis_title="",
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Government Ownership vs Carbon Price")
            
            ownership_data = pd.DataFrame([
                {
                    'Country': c,
                    'Ownership': d['govt_ownership'] * 100,
                    'Carbon Price': d['carbon_price_2024'],
                    'Liability': d['total_liability_b']
                }
                for c, d in COUNTRY_DATA.items()
            ])
            
            fig = px.scatter(
                ownership_data,
                x='Ownership',
                y='Carbon Price',
                size='Liability',
                color='Country',
                text='Country',
                color_discrete_map={
                    'Singapore': '#EF4444',
                    'Thailand': '#3B82F6',
                    'Indonesia': '#22C55E',
                    'Malaysia': '#FCD34D',
                    'Vietnam': '#8B5CF6'
                }
            )
            fig.update_traces(textposition='top center')
            fig.update_layout(
                xaxis_title="Government Ownership (%)",
                yaxis_title="Carbon Price ($/tCO2e)",
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            # Add trendline annotation
            fig.add_annotation(
                x=75, y=50,
                text="↙ Inverse Relationship",
                showarrow=False,
                font=dict(size=12, color='#64748B')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Key insight box
        st.markdown("""
        <div class="insight-box">
            <h4>🔍 Key Finding: The Ownership-Policy Paradox</h4>
            <p>A striking inverse relationship exists between state ownership and carbon pricing stringency. 
            Singapore (13% govt ownership) maintains $59/tCO2e, while Indonesia (100% state-owned) 
            implements only $25/tCO2e. This challenges the assumption that government ownership 
            facilitates climate policy implementation.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Country comparison table
        st.markdown("### Country Comparison Table")
        df = create_country_comparison_df()
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 2: CARBON LIABILITY CALCULATOR
    # ========================================================================
    with tab2:
        st.markdown("## Carbon Liability Calculator")
        st.markdown("*Calculate NPV of carbon compliance costs under different scenarios*")
        
        # Calculator inputs
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Select Country")
            selected_country = st.selectbox(
                "Country",
                list(COUNTRY_DATA.keys()),
                format_func=lambda x: f"{COUNTRY_DATA[x]['flag']} {x}"
            )
            
            country_data = COUNTRY_DATA[selected_country]
            
            st.markdown("### Adjust Parameters")
            
            base_carbon_price = st.number_input(
                "Base Carbon Price ($/tCO2e)",
                min_value=0,
                max_value=200,
                value=country_data['carbon_price_2024'] if country_data['carbon_price_2024'] > 0 else 25
            )
            
            price_escalation = st.slider(
                "Annual Price Escalation (%)",
                0.0, 10.0, 3.0, 0.5
            )
            
            coverage = st.slider(
                "Sector Coverage (%)",
                0, 100, country_data['coverage_pct']
            )
        
        with col2:
            # Calculate liability
            emissions_intensity = 0.14  # tCO2/barrel
            daily_emissions = country_data['capacity_kbpd'] * 1000 * emissions_intensity
            annual_emissions_mt = daily_emissions * 365 / 1_000_000
            
            # NPV calculation
            npv_liability = 0
            yearly_data = []
            
            for year in range(analysis_years):
                price = base_carbon_price * ((1 + price_escalation/100) ** year)
                covered_emissions = annual_emissions_mt * (coverage / 100)
                annual_cost = covered_emissions * price * 1_000_000  # Dollars
                discounted_cost = annual_cost / ((1 + discount_rate) ** year)
                npv_liability += discounted_cost
                
                yearly_data.append({
                    'Year': 2025 + year,
                    'Carbon Price': price,
                    'Annual Cost ($M)': annual_cost / 1_000_000,
                    'Discounted Cost ($M)': discounted_cost / 1_000_000
                })
            
            npv_liability_b = npv_liability / 1_000_000_000
            govt_exposure_b = npv_liability_b * country_data['govt_ownership']
            
            # Display results
            st.markdown("### 📊 Liability Analysis Results")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                st.metric(
                    "Total Carbon Liability",
                    f"${npv_liability_b:.2f}B",
                    delta=f"{((npv_liability_b/country_data['total_liability_b'])-1)*100:+.1f}% vs baseline" if country_data['total_liability_b'] > 0 else None
                )
            
            with res_col2:
                st.metric(
                    "Government Exposure",
                    f"${govt_exposure_b:.2f}B",
                    delta=f"{country_data['govt_ownership']*100:.0f}% ownership"
                )
            
            with res_col3:
                st.metric(
                    "Annual Emissions",
                    f"{annual_emissions_mt:.1f} Mt CO2",
                    delta=f"{coverage}% covered"
                )
            
            # Liability projection chart
            yearly_df = pd.DataFrame(yearly_data)
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(
                    x=yearly_df['Year'],
                    y=yearly_df['Discounted Cost ($M)'],
                    name='Discounted Cost',
                    marker_color='#3B82F6'
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=yearly_df['Year'],
                    y=yearly_df['Carbon Price'],
                    name='Carbon Price',
                    line=dict(color='#EF4444', width=3)
                ),
                secondary_y=True
            )
            
            fig.update_layout(
                title=f"Carbon Liability Projection: {selected_country}",
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_yaxes(title_text="Discounted Cost ($M)", secondary_y=False)
            fig.update_yaxes(title_text="Carbon Price ($/tCO2e)", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Regional comparison
        st.markdown("### Regional Liability Comparison (Current Settings)")
        
        comparison_data = []
        for country, data in COUNTRY_DATA.items():
            price = data['carbon_price_2024'] if data['carbon_price_2024'] > 0 else 15
            liability = calculate_carbon_liability(country, price, analysis_years, discount_rate)
            comparison_data.append({
                'Country': f"{data['flag']} {country}",
                'Liability ($B)': liability,
                'Govt Exposure ($B)': liability * data['govt_ownership']
            })
        
        comp_df = pd.DataFrame(comparison_data)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=comp_df['Country'],
            y=comp_df['Liability ($B)'],
            name='Total Liability',
            marker_color='#3B82F6'
        ))
        fig.add_trace(go.Bar(
            x=comp_df['Country'],
            y=comp_df['Govt Exposure ($B)'],
            name='Govt Exposure',
            marker_color='#EF4444'
        ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            yaxis_title="Liability ($B)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # TAB 3: POLICY DIVERGENCE
    # ========================================================================
    with tab3:
        st.markdown("## Policy Divergence Analysis")
        st.markdown("*Quantifying the fragmentation across ASEAN carbon pricing regimes*")
        
        divergence = get_divergence_metrics()
        
        # Divergence metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card warning">
                <div class="metric-label">Timeline Spread</div>
                <div class="metric-value">11 years</div>
                <p style="color: #64748B; font-size: 0.85rem;">Singapore (2019) → Malaysia (2030)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card warning">
                <div class="metric-label">Price Spread</div>
                <div class="metric-value">4×</div>
                <p style="color: #64748B; font-size: 0.85rem;">$15/t (MY) → $59/t (SG)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card warning">
                <div class="metric-label">Coverage Spread</div>
                <div class="metric-value">50 pp</div>
                <p style="color: #64748B; font-size: 0.85rem;">30% (MY) → 80% (SG)</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Timeline visualization
        st.markdown("### ETS Implementation Timeline")
        
        timeline_data = pd.DataFrame([
            {'Country': f"{d['flag']} {c}", 'Year': d['ets_launch_year'], 'Status': d['ets_status']}
            for c, d in COUNTRY_DATA.items()
        ])
        
        fig = px.scatter(
            timeline_data,
            x='Year',
            y='Country',
            color='Status',
            size=[50]*5,
            color_discrete_map={
                'Operational': '#22C55E',
                'Development': '#F59E0B',
                'Voluntary': '#EF4444'
            }
        )
        
        # Add connecting line
        fig.add_shape(
            type="line",
            x0=2019, x1=2030,
            y0=0.5, y1=0.5,
            line=dict(color="#CBD5E1", width=2, dash="dash"),
            layer="below"
        )
        
        fig.update_layout(
            height=300,
            xaxis=dict(range=[2017, 2032], dtick=2),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_traces(marker=dict(size=25, line=dict(width=2, color='white')))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Carbon price comparison
        st.markdown("### Carbon Price Trajectory Comparison")
        
        # Generate price trajectories
        years = list(range(2024, 2051))
        trajectories = {}
        
        for country, data in COUNTRY_DATA.items():
            base = data['carbon_price_2024'] if data['carbon_price_2024'] > 0 else 15
            target_2030 = data['carbon_price_2030']
            
            prices = []
            for year in years:
                if year <= 2030:
                    # Linear interpolation to 2030
                    progress = (year - 2024) / 6
                    price = base + (target_2030 - base) * progress
                else:
                    # Continue at 3% growth after 2030
                    price = target_2030 * (1.03 ** (year - 2030))
                prices.append(price)
            
            trajectories[country] = prices
        
        fig = go.Figure()
        colors = {'Singapore': '#EF4444', 'Thailand': '#3B82F6', 'Indonesia': '#22C55E', 
                  'Malaysia': '#FCD34D', 'Vietnam': '#8B5CF6'}
        
        for country, prices in trajectories.items():
            fig.add_trace(go.Scatter(
                x=years,
                y=prices,
                name=f"{COUNTRY_DATA[country]['flag']} {country}",
                line=dict(color=colors[country], width=3),
                mode='lines'
            ))
        
        # Add target band
        fig.add_hrect(y0=70, y1=95, fillcolor="#22C55E", opacity=0.1, 
                      line_width=0, annotation_text="2045 Target Band: $70-95/t",
                      annotation_position="top right")
        
        fig.update_layout(
            height=450,
            xaxis_title="Year",
            yaxis_title="Carbon Price ($/tCO2e)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Competitiveness impact
        st.markdown("### Competitiveness Impact Analysis")
        
        st.markdown("""
        The 4× price differential translates to significant cost disparities:
        """)
        
        impact_col1, impact_col2 = st.columns(2)
        
        with impact_col1:
            # Cost per barrel comparison
            cost_data = []
            for country, data in COUNTRY_DATA.items():
                price = data['carbon_price_2024'] if data['carbon_price_2024'] > 0 else 15
                cost_per_bbl = 0.14 * price  # emissions intensity × price
                cost_data.append({
                    'Country': f"{data['flag']} {country}",
                    'Carbon Cost ($/bbl)': cost_per_bbl,
                    'Margin Impact (%)': (cost_per_bbl / 6) * 100  # Assuming $6/bbl typical margin
                })
            
            cost_df = pd.DataFrame(cost_data)
            
            fig = px.bar(
                cost_df,
                x='Country',
                y='Carbon Cost ($/bbl)',
                color='Carbon Cost ($/bbl)',
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(
                title="Carbon Cost per Barrel",
                height=350,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with impact_col2:
            fig = px.bar(
                cost_df,
                x='Country',
                y='Margin Impact (%)',
                color='Margin Impact (%)',
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(
                title="Impact on Refining Margins",
                height=350,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # TAB 4: REFINERY ANALYSIS
    # ========================================================================
    with tab4:
        st.markdown("## Facility-Level Risk Assessment")
        st.markdown("*Analyzing transition readiness across 25 ASEAN refineries*")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            country_filter = st.multiselect(
                "Filter by Country",
                list(COUNTRY_DATA.keys()),
                default=list(COUNTRY_DATA.keys())
            )
        with col2:
            complexity_filter = st.multiselect(
                "Filter by Complexity",
                ['High', 'Medium', 'Low'],
                default=['High', 'Medium', 'Low']
            )
        
        # Filter data
        filtered_refineries = [
            r for r in REFINERY_DATA 
            if r['country'] in country_filter and r['complexity'] in complexity_filter
        ]
        
        refinery_df = pd.DataFrame(filtered_refineries)
        
        # Age distribution chart
        st.markdown("### Refinery Age Distribution")
        
        fig = px.scatter(
            refinery_df,
            x='age_years',
            y='capacity_kbpd',
            color='country',
            size='capacity_kbpd',
            hover_name='name',
            color_discrete_map={
                'Singapore': '#EF4444',
                'Thailand': '#3B82F6',
                'Indonesia': '#22C55E',
                'Malaysia': '#FCD34D',
                'Vietnam': '#8B5CF6'
            }
        )
        
        # Add risk zones
        fig.add_vrect(x0=50, x1=110, fillcolor="#EF4444", opacity=0.1,
                      annotation_text="High Stranding Risk", annotation_position="top left")
        fig.add_vrect(x0=30, x1=50, fillcolor="#F59E0B", opacity=0.1,
                      annotation_text="Moderate Risk", annotation_position="top left")
        fig.add_vrect(x0=0, x1=30, fillcolor="#22C55E", opacity=0.1,
                      annotation_text="Transition Ready", annotation_position="top left")
        
        fig.update_layout(
            height=500,
            xaxis_title="Facility Age (Years)",
            yaxis_title="Capacity (kbpd)",
            legend_title="Country",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Refinery table
        st.markdown("### Refinery Details")
        
        display_df = refinery_df.copy()
        display_df['Flag'] = display_df['country'].map(lambda x: COUNTRY_DATA[x]['flag'])
        display_df['Country'] = display_df.apply(lambda r: f"{r['Flag']} {r['country']}", axis=1)
        display_df['Risk Level'] = display_df['age_years'].apply(
            lambda x: '🔴 High' if x > 50 else ('🟡 Medium' if x > 30 else '🟢 Low')
        )
        
        st.dataframe(
            display_df[['Country', 'name', 'capacity_kbpd', 'owner', 'age_years', 'complexity', 'Risk Level']].rename(
                columns={
                    'name': 'Refinery',
                    'capacity_kbpd': 'Capacity (kbpd)',
                    'owner': 'Owner',
                    'age_years': 'Age (years)',
                    'complexity': 'Complexity',
                }
            ),
            use_container_width=True,
            hide_index=True
        )
        
        # Country summary
        st.markdown("### Country Fleet Summary")
        
        summary_data = []
        for country in country_filter:
            country_refs = [r for r in filtered_refineries if r['country'] == country]
            if country_refs:
                ages = [r['age_years'] for r in country_refs]
                summary_data.append({
                    'Country': f"{COUNTRY_DATA[country]['flag']} {country}",
                    'Refineries': len(country_refs),
                    'Avg Age': f"{np.mean(ages):.0f} years",
                    'Oldest': f"{max(ages)} years",
                    'Newest': f"{min(ages)} years",
                    'High Risk': len([a for a in ages if a > 50]),
                    'Transition Ready': len([a for a in ages if a < 30])
                })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 5: INTEGRATION PATHWAY
    # ========================================================================
    with tab5:
        st.markdown("## 🛤️ Regional Integration Pathway (2025-2045)")
        st.markdown("*Three-phase roadmap to unified ASEAN carbon market*")
        
        # Phase overview
        phases = get_phase_progress()
        
        col1, col2, col3 = st.columns(3)
        phase_colors = {'Phase 1': '#3B82F6', 'Phase 2': '#F59E0B', 'Phase 3': '#22C55E'}
        
        for i, (col, phase) in enumerate(zip([col1, col2, col3], phases)):
            with col:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; 
                     border-top: 4px solid {phase_colors[phase['phase']]}; 
                     box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <h3 style="margin: 0; color: {phase_colors[phase['phase']]};">{phase['phase']}</h3>
                    <p style="font-size: 1.1rem; font-weight: 600; color: #1E3A5F; margin: 8px 0;">{phase['name']}</p>
                    <p style="color: #64748B; margin: 4px 0;">{phase['start']} - {phase['end']}</p>
                    <div style="background: #F1F5F9; border-radius: 8px; height: 8px; margin-top: 12px;">
                        <div style="background: {phase_colors[phase['phase']]}; width: {phase['progress']}%; 
                             height: 100%; border-radius: 8px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interactive timeline
        st.markdown("### 📅 Milestone Timeline")
        
        # Scenario selector
        scenario = st.radio(
            "Select Scenario",
            ["Baseline (Malaysia Commits Q3 2025)", "Delayed (Malaysia Commits 2027+)"],
            horizontal=True
        )
        
        # Filter milestones based on scenario
        milestones_df = pd.DataFrame(INTEGRATION_MILESTONES)
        
        if "Delayed" in scenario:
            # Adjust milestones for delay scenario
            milestones_df.loc[milestones_df['milestone'].str.contains('Malaysia'), 'year'] += 5
        
        # Create Gantt-like timeline
        fig = go.Figure()
        
        phase_y = {'Phase 1': 3, 'Phase 2': 2, 'Phase 3': 1}
        status_colors = {'Pending': '#3B82F6', 'Critical': '#EF4444', 'Conditional': '#F59E0B', 'Complete': '#22C55E'}
        
        for _, row in milestones_df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['year']],
                y=[phase_y[row['phase']]],
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=status_colors.get(row['status'], '#94A3B8'),
                    line=dict(width=2, color='white')
                ),
                text=[row['quarter']],
                textposition='top center',
                name=row['milestone'],
                hovertemplate=f"<b>{row['milestone']}</b><br>Year: {row['year']}<br>Status: {row['status']}<extra></extra>"
            ))
        
        fig.update_layout(
            height=350,
            xaxis=dict(
                title="Year",
                range=[2024, 2047],
                dtick=5,
                gridcolor='#E2E8F0'
            ),
            yaxis=dict(
                tickvals=[1, 2, 3],
                ticktext=['Phase 3: Integration', 'Phase 2: Convergence', 'Phase 1: Foundation'],
                gridcolor='#E2E8F0'
            ),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Add phase backgrounds
        fig.add_vrect(x0=2025, x1=2028, fillcolor="#3B82F6", opacity=0.05, layer="below")
        fig.add_vrect(x0=2028, x1=2035, fillcolor="#F59E0B", opacity=0.05, layer="below")
        fig.add_vrect(x0=2035, x1=2045, fillcolor="#22C55E", opacity=0.05, layer="below")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Milestone details table
        st.markdown("### 📋 Milestone Details")
        
        display_milestones = milestones_df.copy()
        display_milestones['Status Icon'] = display_milestones['status'].map({
            'Pending': '🔵', 'Critical': '🔴', 'Conditional': '🟡', 'Complete': '🟢'
        })
        display_milestones['Display'] = display_milestones['Status Icon'] + ' ' + display_milestones['status']
        
        st.dataframe(
            display_milestones[['phase', 'year', 'quarter', 'milestone', 'Display']].rename(columns={
                'phase': 'Phase',
                'year': 'Year',
                'quarter': 'Quarter',
                'milestone': 'Milestone',
                'Display': 'Status'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Price convergence simulation
        st.markdown("### 📉 Price Convergence Simulation")
        
        conv_scenario = st.selectbox(
            "Convergence Scenario",
            ["baseline", "accelerated", "delayed"],
            format_func=lambda x: x.title()
        )
        
        convergence_df = simulate_price_convergence(conv_scenario)
        
        fig = go.Figure()
        colors = {'Singapore': '#EF4444', 'Thailand': '#3B82F6', 'Indonesia': '#22C55E', 
                  'Malaysia': '#F59E0B', 'Vietnam': '#8B5CF6'}
        
        for country in colors.keys():
            fig.add_trace(go.Scatter(
                x=convergence_df['year'],
                y=convergence_df[country],
                name=f"{COUNTRY_DATA[country]['flag']} {country}",
                line=dict(color=colors[country], width=3),
                mode='lines'
            ))
        
        # Target band
        fig.add_hrect(y0=70, y1=95, fillcolor="#22C55E", opacity=0.1,
                      annotation_text="2045 Target: $70-95/t", annotation_position="top right")
        
        fig.update_layout(
            height=400,
            xaxis_title="Year",
            yaxis_title="Carbon Price ($/tCO2e)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Spread reduction chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=convergence_df['year'],
                y=convergence_df['spread'],
                fill='tozeroy',
                line=dict(color='#EF4444', width=2),
                fillcolor='rgba(239, 68, 68, 0.2)'
            ))
            fig.add_hline(y=1.5, line_dash="dash", line_color="#22C55E",
                         annotation_text="Target: 1.5×")
            fig.update_layout(
                title="Price Spread Reduction",
                height=300,
                xaxis_title="Year",
                yaxis_title="Price Spread (×)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Key metrics
            final_spread = convergence_df[convergence_df['year'] == 2045]['spread'].values[0]
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 24px; 
                 box-shadow: 0 2px 8px rgba(0,0,0,0.08); height: 268px;">
                <h4 style="color: #1E3A5F; margin-bottom: 16px;">Integration Metrics ({conv_scenario.title()})</h4>
                <div style="display: grid; gap: 12px;">
                    <div style="padding: 12px; background: #F1F5F9; border-radius: 8px;">
                        <span style="color: #64748B;">2024 Price Spread</span>
                        <span style="float: right; font-weight: 600; color: #EF4444;">4.0×</span>
                    </div>
                    <div style="padding: 12px; background: #F1F5F9; border-radius: 8px;">
                        <span style="color: #64748B;">2030 Price Spread</span>
                        <span style="float: right; font-weight: 600; color: #F59E0B;">2.5×</span>
                    </div>
                    <div style="padding: 12px; background: #F1F5F9; border-radius: 8px;">
                        <span style="color: #64748B;">2045 Price Spread</span>
                        <span style="float: right; font-weight: 600; color: #22C55E;">{final_spread:.1f}×</span>
                    </div>
                    <div style="padding: 12px; background: #DCFCE7; border-radius: 8px;">
                        <span style="color: #166534;">Convergence Achieved</span>
                        <span style="float: right; font-weight: 600; color: #166534;">✓</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 6: MALAYSIA DECISION ANALYZER
    # ========================================================================
    with tab6:
        st.markdown("## 🇲🇾 Malaysia Decision Analyzer")
        st.markdown("*The critical swing factor for regional integration success*")
        
        # Countdown timer
        days_remaining = get_malaysia_countdown()
        
        if days_remaining > 0:
            urgency_color = "#22C55E" if days_remaining > 180 else ("#F59E0B" if days_remaining > 90 else "#EF4444")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E3A5F 0%, #2D5A87 100%); 
                 border-radius: 12px; padding: 32px; text-align: center; margin-bottom: 24px;">
                <p style="color: #B8D4E8; font-size: 14px; margin: 0;">DAYS UNTIL Q3 2025 DEADLINE</p>
                <h1 style="color: {urgency_color}; font-size: 72px; margin: 8px 0; font-weight: 700;">{days_remaining}</h1>
                <p style="color: white; font-size: 16px; margin: 0;">Malaysia Policy Decision Deadline: September 30, 2025</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Scenario comparison
        st.markdown("### 📊 Scenario Comparison: Commitment vs. Delay")
        
        commit = MALAYSIA_SCENARIOS['commitment']
        delay = MALAYSIA_SCENARIOS['delay']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%); 
                 border-radius: 12px; padding: 24px; border: 2px solid #22C55E;">
                <h3 style="color: #166534; margin: 0 0 16px 0;">✅ {commit['name']}</h3>
                <div style="display: grid; gap: 12px;">
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">Implementation Cost</span>
                        <span style="float: right; font-weight: 700; color: #166534;">${commit['implementation_cost']}M</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">ETS Launch</span>
                        <span style="float: right; font-weight: 600;">{commit['ets_launch']}</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">Integration Year</span>
                        <span style="float: right; font-weight: 600;">{commit['integration_year']}</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">Technology Gap</span>
                        <span style="float: right; font-weight: 600; color: #22C55E;">{commit['technology_gap']} years</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">CBAM Exposure</span>
                        <span style="float: right; font-weight: 600; color: #22C55E;">{commit['cbam_exposure']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%); 
                 border-radius: 12px; padding: 24px; border: 2px solid #EF4444;">
                <h3 style="color: #991B1B; margin: 0 0 16px 0;">❌ {delay['name']}</h3>
                <div style="display: grid; gap: 12px;">
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">Total Cost (incl. losses)</span>
                        <span style="float: right; font-weight: 700; color: #EF4444;">${delay['total_cost']/1000:.1f}B</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">ETS Launch</span>
                        <span style="float: right; font-weight: 600;">{delay['ets_launch']}</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">Integration Year</span>
                        <span style="float: right; font-weight: 600;">{delay['integration_year']}</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">Technology Gap</span>
                        <span style="float: right; font-weight: 600; color: #EF4444;">{delay['technology_gap']} years</span>
                    </div>
                    <div style="background: white; padding: 12px; border-radius: 8px;">
                        <span style="color: #64748B;">CBAM Exposure</span>
                        <span style="float: right; font-weight: 600; color: #EF4444;">{delay['cbam_exposure']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Cost comparison chart
        st.markdown("### 💰 Cost-Benefit Analysis")
        
        cost_comparison = pd.DataFrame([
            {'Scenario': 'Commitment', 'Cost Type': 'Implementation', 'Amount': commit['implementation_cost']},
            {'Scenario': 'Commitment', 'Cost Type': 'Opportunity Cost', 'Amount': 0},
            {'Scenario': 'Delay', 'Cost Type': 'Implementation', 'Amount': delay['implementation_cost']},
            {'Scenario': 'Delay', 'Cost Type': 'Opportunity Cost', 'Amount': delay['total_cost'] - delay['implementation_cost']},
        ])
        
        fig = px.bar(
            cost_comparison,
            x='Scenario',
            y='Amount',
            color='Cost Type',
            barmode='stack',
            color_discrete_map={'Implementation': '#3B82F6', 'Opportunity Cost': '#EF4444'}
        )
        fig.update_layout(
            height=400,
            yaxis_title="Cost ($M)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Benefits and risks
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Benefits of Early Commitment")
            for benefit in commit['benefits']:
                st.markdown(f"- {benefit}")
        
        with col2:
            st.markdown("### ⚠️ Risks of Delay")
            for risk in delay['risks']:
                st.markdown(f"- {risk}")
        
        # Key insight
        st.markdown("""
        <div class="insight-box">
            <h4>🔍 Key Finding: Asymmetric Cost Structure</h4>
            <p>The cost asymmetry is dramatic: <strong>$185M implementation cost vs $2-5B delay cost</strong>. 
            This 10-20× difference makes early commitment strongly preferable from a pure economic standpoint. 
            Malaysia's youngest refinery fleet (average 33 years) and Petronas's substantial financial resources 
            position the country well for transition if policy commitment materializes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Malaysia-specific data
        st.markdown("### 🏭 Malaysia Refinery Position")
        
        malaysia_refs = [r for r in REFINERY_DATA if r['country'] == 'Malaysia']
        malaysia_df = pd.DataFrame(malaysia_refs)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                malaysia_df,
                x='name',
                y='capacity_kbpd',
                color='age_years',
                color_continuous_scale='RdYlGn_r',
                labels={'age_years': 'Age (years)', 'capacity_kbpd': 'Capacity (kbpd)', 'name': 'Refinery'}
            )
            fig.update_layout(
                title="Malaysia Refineries: Capacity & Age",
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            avg_age = malaysia_df['age_years'].mean()
            total_cap = malaysia_df['capacity_kbpd'].sum()
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 24px; 
                 box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <h4 style="color: #1E3A5F;">Fleet Summary</h4>
                <p><strong>Refineries:</strong> {len(malaysia_refs)}</p>
                <p><strong>Total Capacity:</strong> {total_cap} kbpd</p>
                <p><strong>Avg Age:</strong> {avg_age:.0f} years</p>
                <p><strong>Newest:</strong> RAPID (5 yrs)</p>
                <p><strong>Oldest:</strong> Port Dickson (60 yrs)</p>
                <hr style="margin: 16px 0;">
                <p style="color: #22C55E; font-weight: 600;">✓ Youngest fleet in ASEAN-5</p>
                <p style="color: #22C55E; font-weight: 600;">✓ High modernization potential</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ========================================================================
    # TAB 7: INVESTMENT ANALYSIS
    # ========================================================================
    with tab7:
        st.markdown("## 💵 Investment Requirements Analysis")
        st.markdown("*$229M investment for 3:1 benefit-cost ratio*")
        
        # ROI metrics
        roi = calculate_integration_roi()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Investment", f"${roi['total_investment']}M", help="2025-2030 total")
        with col2:
            st.metric("10-Year Benefits", f"${roi['total_benefits']:.0f}M")
        with col3:
            st.metric("Benefit-Cost Ratio", f"{roi['benefit_cost_ratio']:.1f}:1")
        with col4:
            st.metric("Payback Period", f"{roi['payback_years']:.1f} years")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Investment breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Investment by Component")
            
            inv_df = pd.DataFrame(INVESTMENT_REQUIREMENTS)
            
            fig = px.pie(
                inv_df,
                values='amount_m',
                names='component',
                color_discrete_sequence=['#3B82F6', '#22C55E', '#F59E0B', '#8B5CF6', '#EF4444']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Funding Sources")
            
            fund_df = pd.DataFrame(FUNDING_SOURCES)
            
            fig = px.bar(
                fund_df,
                x='amount_m',
                y='source',
                orientation='h',
                color='status',
                color_discrete_map={
                    'Proposed': '#3B82F6',
                    'Required': '#F59E0B',
                    'Projected': '#22C55E',
                    'Negotiating': '#8B5CF6',
                    'Available': '#10B981'
                }
            )
            fig.update_layout(
                height=400,
                xaxis_title="Amount ($M)",
                yaxis_title="",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed investment table
        st.markdown("### 📋 Investment Details")
        
        inv_display = inv_df.copy()
        inv_display['Amount'] = inv_display['amount_m'].apply(lambda x: f"${x}M")
        inv_display['Share'] = inv_display['amount_m'].apply(lambda x: f"{x/roi['total_investment']*100:.0f}%")
        
        st.dataframe(
            inv_display[['component', 'Amount', 'Share', 'timeline', 'description']].rename(columns={
                'component': 'Component',
                'timeline': 'Timeline',
                'description': 'Description'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Technology cooperation
        st.markdown("### 🔧 Technology Cooperation Opportunities")
        
        tech_col1, tech_col2 = st.columns(2)
        
        for i, tech in enumerate(TECH_COOPERATION):
            col = tech_col1 if i % 2 == 0 else tech_col2
            with col:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; 
                     box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 16px;
                     border-left: 4px solid #3B82F6;">
                    <h4 style="color: #1E3A5F; margin: 0 0 8px 0;">{tech['name']}</h4>
                    <p style="color: #64748B; font-size: 14px; margin: 0 0 12px 0;">{tech['description']}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                        <div><strong>Cost Reduction:</strong> {tech['cost_reduction']}</div>
                        <div><strong>Lead:</strong> {', '.join(tech['lead_countries'][:2])}</div>
                        <div><strong>Feasibility:</strong> ${tech['investment_feasibility']}M</div>
                        <div><strong>Commercial:</strong> ${tech['investment_commercial']}M</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Risk matrix
        st.markdown("### ⚠️ Risk Assessment Matrix")
        
        risk_df = pd.DataFrame(RISK_MATRIX)
        
        fig = px.scatter(
            risk_df,
            x='probability',
            y=risk_df['impact'].map({'Low': 1, 'Medium': 2, 'High': 3}),
            size=[40]*len(risk_df),
            color='risk',
            text='risk',
            color_discrete_sequence=['#EF4444', '#F59E0B', '#3B82F6', '#22C55E', '#8B5CF6']
        )
        fig.update_traces(textposition='top center')
        fig.update_layout(
            height=400,
            xaxis=dict(title="Probability (%)", range=[0, 50]),
            yaxis=dict(title="Impact", tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Add risk zones
        fig.add_shape(type="rect", x0=30, x1=50, y0=2.5, y1=3.5,
                      fillcolor="#EF4444", opacity=0.1, line_width=0)
        fig.add_annotation(x=40, y=3.2, text="High Risk Zone", showarrow=False,
                          font=dict(color="#991B1B", size=10))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk mitigation table
        st.markdown("### 🛡️ Risk Mitigation Strategies")
        st.dataframe(
            risk_df[['risk', 'probability', 'impact', 'mitigation']].rename(columns={
                'risk': 'Risk',
                'probability': 'Probability (%)',
                'impact': 'Impact',
                'mitigation': 'Mitigation Strategy'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>ASEAN Carbon Integration Simulator v2.0 | Based on research by Bosco Chiramel</p>
        <p>Data sources: National petroleum statistics, IEA, World Bank Carbon Pricing Dashboard</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
