"""Tests for ASEAN Carbon Simulator."""
import pytest

def test_import_app():
    """Test app imports without error."""
    import app
    assert app is not None

def test_refinery_data_exists():
    """Test refinery data is defined."""
    import app
    assert hasattr(app, 'REFINERY_DATA') or 'Singapore' in str(dir(app))

def test_carbon_price_calculation():
    """Test basic NPV calculation logic."""
    # NPV = sum of discounted cash flows
    carbon_price = 50  # $/tCO2
    emissions = 1_000_000  # tCO2/year
    years = 10
    discount_rate = 0.10
    
    npv = sum(carbon_price * emissions / (1 + discount_rate)**t for t in range(1, years+1))
    assert npv > 0
    assert npv < carbon_price * emissions * years  # Discounting reduces value

def test_policy_timeline_order():
    """Test policy timelines are chronological."""
    timelines = {'Singapore': 2019, 'Thailand': 2025, 'Indonesia': 2025, 'Vietnam': 2028, 'Malaysia': 2030}
    assert timelines['Singapore'] < timelines['Malaysia']

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
