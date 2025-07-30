#!/usr/bin/env python3
"""
Market Analyzer for Grant Cardone's Real Estate Investment Strategy
Analyzes and compares 10 favorable markets based on Cardone's criteria
"""

import pandas as pd
import numpy as np
from datetime import datetime

class MarketAnalyzer:
    def __init__(self):
        self.markets = self._initialize_markets()
        
    def _initialize_markets(self):
        """Initialize market data based on research"""
        return {
            'Nashville': {
                'state': 'TN',
                'metro_population': 2100000,
                'population_growth': 0.018,
                'job_growth': 0.023,
                'income_growth': 0.042,
                'cap_rate_min': 0.065,
                'cap_rate_max': 0.075,
                'price_per_unit_min': 65000,
                'price_per_unit_max': 85000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Very Friendly',
                'new_construction': 'Limited',
                'key_industries': ['Healthcare', 'Music', 'Tech'],
                'target_areas': ['Antioch', 'Madison', 'Donelson'],
                'risk_factors': ['Rising property taxes'],
                'advantages': ['No state income tax', 'Landlord-friendly', 'Strong healthcare']
            },
            'Austin': {
                'state': 'TX',
                'metro_population': 2400000,
                'population_growth': 0.021,
                'job_growth': 0.032,
                'income_growth': 0.051,
                'cap_rate_min': 0.060,
                'cap_rate_max': 0.070,
                'price_per_unit_min': 75000,
                'price_per_unit_max': 95000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Friendly',
                'new_construction': 'Increasing',
                'key_industries': ['Tech', 'Education', 'Healthcare'],
                'target_areas': ['Round Rock', 'Pflugerville', 'Cedar Park'],
                'risk_factors': ['Potential oversupply'],
                'advantages': ['No state income tax', 'Strong tech sector', 'University presence']
            },
            'Phoenix': {
                'state': 'AZ',
                'metro_population': 4900000,
                'population_growth': 0.019,
                'job_growth': 0.028,
                'income_growth': 0.038,
                'cap_rate_min': 0.068,
                'cap_rate_max': 0.078,
                'price_per_unit_min': 55000,
                'price_per_unit_max': 75000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Friendly',
                'new_construction': 'Moderate',
                'key_industries': ['Healthcare', 'Financial Services', 'Tech'],
                'target_areas': ['Mesa', 'Chandler', 'Glendale'],
                'risk_factors': ['Water scarcity'],
                'advantages': ['Favorable taxes', 'Landlord-friendly', 'Affordable cost of living']
            },
            'Tampa': {
                'state': 'FL',
                'metro_population': 3200000,
                'population_growth': 0.017,
                'job_growth': 0.021,
                'income_growth': 0.035,
                'cap_rate_min': 0.062,
                'cap_rate_max': 0.072,
                'price_per_unit_min': 60000,
                'price_per_unit_max': 80000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Friendly',
                'new_construction': 'Limited',
                'key_industries': ['Tourism', 'Healthcare', 'Financial Services'],
                'target_areas': ['Brandon', 'Riverview', 'New Port Richey'],
                'risk_factors': ['Hurricane risk', 'Insurance costs'],
                'advantages': ['No state income tax', 'Strong tourism', 'Port hub']
            },
            'Charlotte': {
                'state': 'NC',
                'metro_population': 2700000,
                'population_growth': 0.016,
                'job_growth': 0.025,
                'income_growth': 0.040,
                'cap_rate_min': 0.065,
                'cap_rate_max': 0.075,
                'price_per_unit_min': 70000,
                'price_per_unit_max': 90000,
                'tax_environment': 'Moderate',
                'landlord_laws': 'Friendly',
                'new_construction': 'Moderate',
                'key_industries': ['Banking', 'Healthcare', 'Tech'],
                'target_areas': ['Concord', 'Matthews', 'Mint Hill'],
                'risk_factors': ['Competition from large banks'],
                'advantages': ['Major banking center', 'Strong healthcare', 'Good infrastructure']
            },
            'Raleigh': {
                'state': 'NC',
                'metro_population': 1400000,
                'population_growth': 0.020,
                'job_growth': 0.027,
                'income_growth': 0.045,
                'cap_rate_min': 0.060,
                'cap_rate_max': 0.070,
                'price_per_unit_min': 80000,
                'price_per_unit_max': 100000,
                'tax_environment': 'Moderate',
                'landlord_laws': 'Friendly',
                'new_construction': 'Controlled',
                'key_industries': ['Tech', 'Education', 'Healthcare'],
                'target_areas': ['Cary', 'Apex', 'Holly Springs'],
                'risk_factors': ['Higher property prices'],
                'advantages': ['Research Triangle Park', 'Strong education', 'High-quality workforce']
            },
            'Salt Lake City': {
                'state': 'UT',
                'metro_population': 1300000,
                'population_growth': 0.015,
                'job_growth': 0.029,
                'income_growth': 0.048,
                'cap_rate_min': 0.068,
                'cap_rate_max': 0.078,
                'price_per_unit_min': 65000,
                'price_per_unit_max': 85000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Friendly',
                'new_construction': 'Limited',
                'key_industries': ['Tech', 'Healthcare', 'Outdoor Recreation'],
                'target_areas': ['West Valley City', 'Murray', 'Sandy'],
                'risk_factors': ['Limited land availability'],
                'advantages': ['Growing tech sector', 'Favorable business climate', 'Outdoor appeal']
            },
            'Boise': {
                'state': 'ID',
                'metro_population': 764000,
                'population_growth': 0.023,
                'job_growth': 0.026,
                'income_growth': 0.052,
                'cap_rate_min': 0.070,
                'cap_rate_max': 0.080,
                'price_per_unit_min': 50000,
                'price_per_unit_max': 70000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Very Friendly',
                'new_construction': 'Limited',
                'key_industries': ['Tech', 'Healthcare', 'Agriculture'],
                'target_areas': ['Meridian', 'Nampa', 'Caldwell'],
                'risk_factors': ['Limited supply'],
                'advantages': ['Favorable taxes', 'Affordable cost of living', 'Landlord-friendly']
            },
            'Fort Worth': {
                'state': 'TX',
                'metro_population': 1000000,
                'population_growth': 0.019,
                'job_growth': 0.024,
                'income_growth': 0.039,
                'cap_rate_min': 0.065,
                'cap_rate_max': 0.075,
                'price_per_unit_min': 60000,
                'price_per_unit_max': 80000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Friendly',
                'new_construction': 'Moderate',
                'key_industries': ['Manufacturing', 'Logistics', 'Healthcare'],
                'target_areas': ['Arlington', 'Mansfield', 'Burleson'],
                'risk_factors': ['Economic dependence on manufacturing'],
                'advantages': ['No state income tax', 'Good infrastructure', 'Favorable landlord laws']
            },
            'Las Vegas': {
                'state': 'NV',
                'metro_population': 2300000,
                'population_growth': 0.014,
                'job_growth': 0.022,
                'income_growth': 0.036,
                'cap_rate_min': 0.070,
                'cap_rate_max': 0.080,
                'price_per_unit_min': 55000,
                'price_per_unit_max': 75000,
                'tax_environment': 'Favorable',
                'landlord_laws': 'Friendly',
                'new_construction': 'Limited',
                'key_industries': ['Tourism', 'Entertainment', 'Tech'],
                'target_areas': ['Henderson', 'North Las Vegas', 'Summerlin'],
                'risk_factors': ['Economic dependence on tourism'],
                'advantages': ['No state income tax', 'Affordable housing', 'Landlord-friendly']
            }
        }
    
    def calculate_market_score(self, market_name):
        """Calculate overall market score based on Cardone's criteria"""
        market = self.markets[market_name]
        
        score = 0
        
        # Population Growth (25 points)
        if market['population_growth'] >= 0.02:
            score += 25
        elif market['population_growth'] >= 0.015:
            score += 20
        elif market['population_growth'] >= 0.01:
            score += 15
        elif market['population_growth'] >= 0.005:
            score += 10
        
        # Job Growth (25 points)
        if market['job_growth'] >= 0.025:
            score += 25
        elif market['job_growth'] >= 0.02:
            score += 20
        elif market['job_growth'] >= 0.015:
            score += 15
        elif market['job_growth'] >= 0.01:
            score += 10
        
        # Cap Rate (20 points)
        avg_cap_rate = (market['cap_rate_min'] + market['cap_rate_max']) / 2
        if avg_cap_rate >= 0.075:
            score += 20
        elif avg_cap_rate >= 0.07:
            score += 17
        elif avg_cap_rate >= 0.065:
            score += 15
        elif avg_cap_rate >= 0.06:
            score += 10
        
        # Tax Environment (15 points)
        if market['tax_environment'] == 'Favorable':
            score += 15
        elif market['tax_environment'] == 'Moderate':
            score += 10
        else:
            score += 5
        
        # Landlord Laws (15 points)
        if market['landlord_laws'] == 'Very Friendly':
            score += 15
        elif market['landlord_laws'] == 'Friendly':
            score += 12
        else:
            score += 8
        
        return score
    
    def get_market_ranking(self):
        """Get ranked list of markets by score"""
        rankings = []
        
        for market_name in self.markets:
            score = self.calculate_market_score(market_name)
            market_data = self.markets[market_name]
            
            rankings.append({
                'market': market_name,
                'state': market_data['state'],
                'score': score,
                'population_growth': market_data['population_growth'],
                'job_growth': market_data['job_growth'],
                'avg_cap_rate': (market_data['cap_rate_min'] + market_data['cap_rate_max']) / 2,
                'price_per_unit_range': f"${market_data['price_per_unit_min']:,}-${market_data['price_per_unit_max']:,}",
                'tax_environment': market_data['tax_environment'],
                'landlord_laws': market_data['landlord_laws'],
                'tier': self._get_tier(score)
            })
        
        # Sort by score (highest first)
        rankings.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rank
        for i, ranking in enumerate(rankings, 1):
            ranking['rank'] = i
        
        return rankings
    
    def _get_tier(self, score):
        """Determine market tier based on score"""
        if score >= 85:
            return "Tier 1 (Highest Priority)"
        elif score >= 75:
            return "Tier 2 (Strong Contenders)"
        else:
            return "Tier 3 (Good Opportunities)"
    
    def get_market_details(self, market_name):
        """Get detailed information about a specific market"""
        if market_name not in self.markets:
            return None
        
        market = self.markets[market_name]
        score = self.calculate_market_score(market_name)
        
        return {
            'market': market_name,
            'state': market['state'],
            'score': score,
            'tier': self._get_tier(score),
            'metro_population': f"{market['metro_population']:,}",
            'population_growth': f"{market['population_growth']:.1%}",
            'job_growth': f"{market['job_growth']:.1%}",
            'income_growth': f"{market['income_growth']:.1%}",
            'cap_rate_range': f"{market['cap_rate_min']:.1%}-{market['cap_rate_max']:.1%}",
            'price_per_unit_range': f"${market['price_per_unit_min']:,}-${market['price_per_unit_max']:,}",
            'tax_environment': market['tax_environment'],
            'landlord_laws': market['landlord_laws'],
            'new_construction': market['new_construction'],
            'key_industries': ', '.join(market['key_industries']),
            'target_areas': ', '.join(market['target_areas']),
            'risk_factors': ', '.join(market['risk_factors']),
            'advantages': ', '.join(market['advantages'])
        }
    
    def export_to_csv(self, filename='market_analysis.csv'):
        """Export market analysis to CSV"""
        rankings = self.get_market_ranking()
        df = pd.DataFrame(rankings)
        df.to_csv(filename, index=False)
        print(f"Market analysis exported to {filename}")

def main():
    """Example usage of the market analyzer"""
    analyzer = MarketAnalyzer()
    
    print("Grant Cardone Market Analysis")
    print("=" * 60)
    
    # Get market rankings
    rankings = analyzer.get_market_ranking()
    
    print("\nMARKET RANKINGS (Based on Cardone's Criteria)")
    print("=" * 60)
    print(f"{'Rank':<4} {'Market':<15} {'State':<3} {'Score':<6} {'Tier':<25}")
    print("-" * 60)
    
    for ranking in rankings:
        print(f"{ranking['rank']:<4} {ranking['market']:<15} {ranking['state']:<3} {ranking['score']:<6} {ranking['tier']:<25}")
    
    print("\n" + "=" * 60)
    print("TOP 3 MARKETS DETAILED ANALYSIS")
    print("=" * 60)
    
    for i in range(3):
        market_name = rankings[i]['market']
        details = analyzer.get_market_details(market_name)
        
        print(f"\n{i+1}. {details['market']}, {details['state']}")
        print(f"   Score: {details['score']}/100 ({details['tier']})")
        print(f"   Population: {details['metro_population']} | Growth: {details['population_growth']}")
        print(f"   Job Growth: {details['job_growth']} | Income Growth: {details['income_growth']}")
        print(f"   Cap Rate: {details['cap_rate_range']} | Price/Unit: {details['price_per_unit_range']}")
        print(f"   Tax Environment: {details['tax_environment']} | Landlord Laws: {details['landlord_laws']}")
        print(f"   Key Industries: {details['key_industries']}")
        print(f"   Target Areas: {details['target_areas']}")
        print(f"   Advantages: {details['advantages']}")
        print(f"   Risk Factors: {details['risk_factors']}")
    
    print("\n" + "=" * 60)
    print("INVESTMENT RECOMMENDATIONS")
    print("=" * 60)
    
    tier1_markets = [r for r in rankings if r['tier'] == "Tier 1 (Highest Priority)"]
    tier2_markets = [r for r in rankings if r['tier'] == "Tier 2 (Strong Contenders)"]
    
    print(f"\nTier 1 Markets ({len(tier1_markets)}):")
    for market in tier1_markets:
        print(f"  • {market['market']}, {market['state']} (Score: {market['score']})")
    
    print(f"\nTier 2 Markets ({len(tier2_markets)}):")
    for market in tier2_markets:
        print(f"  • {market['market']}, {market['state']} (Score: {market['score']})")
    
    print(f"\nImplementation Strategy:")
    print(f"  1. Start with Tier 1 markets for initial investments")
    print(f"  2. Expand to Tier 2 markets for diversification")
    print(f"  3. Focus on value-add opportunities in all markets")
    print(f"  4. Build strong local teams in each target market")
    
    # Export to CSV
    analyzer.export_to_csv()

if __name__ == "__main__":
    main() 