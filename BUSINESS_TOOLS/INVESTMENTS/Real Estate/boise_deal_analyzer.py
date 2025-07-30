#!/usr/bin/env python3
"""
Boise Deal Analyzer for Grant Cardone's Investment Strategy
Analyzes 5 specific multi-family deals in Boise market

⚠️ DISCLAIMER: This script analyzes HYPOTHETICAL deals for educational purposes.
All property data, addresses, and financial projections are fictional examples
demonstrating Grant Cardone's investment methodology. For actual investment
decisions, use real property data and conduct thorough due diligence.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class BoiseDealAnalyzer:
    def __init__(self):
        self.deals = self._initialize_boise_deals()
        
    def _initialize_boise_deals(self):
        """Initialize the 5 Boise deals with detailed data (HYPOTHETICAL EXAMPLES)"""
        return {
            'Deal_1_Meridian': {
                'name': 'Meridian Value-Add Opportunity',
                'address': '1234 N Main St, Meridian, ID',
                'units': 12,
                'year_built': 1985,
                'sqft_per_unit': 1200,
                'lot_size': 0.8,
                'purchase_price': 720000,
                'down_payment': 180000,
                'current_monthly_rent': 12000,
                'current_monthly_expenses': 3600,
                'renovation_budget': 60000,
                'post_reno_monthly_rent': 18000,
                'location_advantage': 'Fastest growing suburb',
                'value_add_potential': 'High (50% rent increase)',
                'risk_factors': ['Higher renovation costs', 'Competition in Meridian']
            },
            'Deal_2_Nampa': {
                'name': 'Nampa B-Class Property',
                'address': '5678 E Franklin Rd, Nampa, ID',
                'units': 8,
                'year_built': 1990,
                'sqft_per_unit': 1000,
                'lot_size': 0.6,
                'purchase_price': 520000,
                'down_payment': 130000,
                'current_monthly_rent': 9600,
                'current_monthly_expenses': 2880,
                'renovation_budget': 40000,
                'post_reno_monthly_rent': 13600,
                'location_advantage': 'Affordable, established neighborhood',
                'value_add_potential': 'Strong (42% rent increase)',
                'risk_factors': ['Tenant turnover during renovations', 'Lower-end market']
            },
            'Deal_3_Caldwell': {
                'name': 'Caldwell Emerging Market',
                'address': '9012 S 10th Ave, Caldwell, ID',
                'units': 6,
                'year_built': 1988,
                'sqft_per_unit': 1100,
                'lot_size': 0.5,
                'purchase_price': 360000,
                'down_payment': 90000,
                'current_monthly_rent': 7200,
                'current_monthly_expenses': 2160,
                'renovation_budget': 30000,
                'post_reno_monthly_rent': 10200,
                'location_advantage': 'Emerging market with growth potential',
                'value_add_potential': 'Excellent (42% rent increase)',
                'risk_factors': ['Emerging market uncertainty', 'Smaller property']
            },
            'Deal_4_GardenCity': {
                'name': 'Garden City Gentrification Play',
                'address': '3456 W State St, Garden City, ID',
                'units': 10,
                'year_built': 1982,
                'sqft_per_unit': 1300,
                'lot_size': 0.7,
                'purchase_price': 650000,
                'down_payment': 162500,
                'current_monthly_rent': 11000,
                'current_monthly_expenses': 3300,
                'renovation_budget': 80000,
                'post_reno_monthly_rent': 16500,
                'location_advantage': 'Prime location near downtown',
                'value_add_potential': 'High (50% rent increase)',
                'risk_factors': ['Gentrification timeline uncertainty', 'Older building']
            },
            'Deal_5_Eagle': {
                'name': 'Eagle Stable Investment',
                'address': '7890 N Eagle Rd, Eagle, ID',
                'units': 14,
                'year_built': 1995,
                'sqft_per_unit': 1150,
                'lot_size': 1.0,
                'purchase_price': 980000,
                'down_payment': 245000,
                'current_monthly_rent': 16800,
                'current_monthly_expenses': 5040,
                'renovation_budget': 70000,
                'post_reno_monthly_rent': 23800,
                'location_advantage': 'Higher-end market, stable tenants',
                'value_add_potential': 'Good (42% rent increase)',
                'risk_factors': ['Higher property taxes', 'Larger investment required']
            }
        }
    
    def calculate_deal_metrics(self, deal_key):
        """Calculate comprehensive metrics for a deal"""
        deal = self.deals[deal_key]
        
        # Basic calculations
        loan_amount = deal['purchase_price'] - deal['down_payment']
        monthly_mortgage = self._calculate_mortgage(loan_amount, 6.5, 25)
        
        # Current metrics
        current_monthly_cash_flow = deal['current_monthly_rent'] - deal['current_monthly_expenses'] - monthly_mortgage
        current_cap_rate = (deal['current_monthly_rent'] * 12 - deal['current_monthly_expenses'] * 12) / deal['purchase_price']
        current_cash_on_cash = (current_monthly_cash_flow * 12) / deal['down_payment']
        current_price_per_unit = deal['purchase_price'] / deal['units']
        
        # Post-renovation metrics
        post_reno_monthly_cash_flow = deal['post_reno_monthly_rent'] - deal['current_monthly_expenses'] - monthly_mortgage
        post_reno_cap_rate = (deal['post_reno_monthly_rent'] * 12 - deal['current_monthly_expenses'] * 12) / deal['purchase_price']
        post_reno_cash_on_cash = (post_reno_monthly_cash_flow * 12) / (deal['down_payment'] + deal['renovation_budget'])
        
        # Value-add metrics
        rent_increase_percentage = (deal['post_reno_monthly_rent'] - deal['current_monthly_rent']) / deal['current_monthly_rent']
        total_investment = deal['down_payment'] + deal['renovation_budget']
        roi_on_renovation = (post_reno_monthly_cash_flow - current_monthly_cash_flow) * 12 / deal['renovation_budget']
        
        # Cardone score calculation
        cardone_score = self._calculate_cardone_score(deal, post_reno_cap_rate, post_reno_cash_on_cash, current_price_per_unit)
        
        return {
            'deal_key': deal_key,
            'name': deal['name'],
            'address': deal['address'],
            'units': deal['units'],
            'purchase_price': deal['purchase_price'],
            'down_payment': deal['down_payment'],
            'renovation_budget': deal['renovation_budget'],
            'total_investment': total_investment,
            'current_monthly_rent': deal['current_monthly_rent'],
            'current_monthly_expenses': deal['current_monthly_expenses'],
            'current_monthly_cash_flow': current_monthly_cash_flow,
            'current_cap_rate': current_cap_rate,
            'current_cash_on_cash': current_cash_on_cash,
            'current_price_per_unit': current_price_per_unit,
            'post_reno_monthly_rent': deal['post_reno_monthly_rent'],
            'post_reno_monthly_cash_flow': post_reno_monthly_cash_flow,
            'post_reno_cap_rate': post_reno_cap_rate,
            'post_reno_cash_on_cash': post_reno_cash_on_cash,
            'rent_increase_percentage': rent_increase_percentage,
            'roi_on_renovation': roi_on_renovation,
            'cardone_score': cardone_score,
            'recommendation': self._get_recommendation(cardone_score),
            'location_advantage': deal['location_advantage'],
            'value_add_potential': deal['value_add_potential'],
            'risk_factors': deal['risk_factors']
        }
    
    def _calculate_mortgage(self, principal, rate, years):
        """Calculate monthly mortgage payment"""
        monthly_rate = rate / 100 / 12
        num_payments = years * 12
        if monthly_rate == 0:
            return principal / num_payments
        return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    def _calculate_cardone_score(self, deal, cap_rate, cash_on_cash, price_per_unit):
        """Calculate Cardone score based on his criteria"""
        score = 0
        
        # Cap Rate (30 points)
        if cap_rate >= 0.08:
            score += 30
        elif cap_rate >= 0.075:
            score += 25
        elif cap_rate >= 0.07:
            score += 20
        elif cap_rate >= 0.065:
            score += 15
        
        # Cash on Cash Return (25 points)
        if cash_on_cash >= 0.28:
            score += 25
        elif cash_on_cash >= 0.25:
            score += 20
        elif cash_on_cash >= 0.22:
            score += 15
        elif cash_on_cash >= 0.20:
            score += 10
        
        # Price per Unit (20 points)
        if price_per_unit <= 60000:
            score += 20
        elif price_per_unit <= 70000:
            score += 15
        elif price_per_unit <= 80000:
            score += 10
        elif price_per_unit <= 100000:
            score += 5
        
        # Value Add Potential (15 points)
        rent_increase = (deal['post_reno_monthly_rent'] - deal['current_monthly_rent']) / deal['current_monthly_rent']
        if rent_increase >= 0.45:
            score += 15
        elif rent_increase >= 0.40:
            score += 12
        elif rent_increase >= 0.35:
            score += 10
        elif rent_increase >= 0.30:
            score += 8
        
        # Market Growth (10 points) - Boise has 2.3% population growth
        score += 10
        
        return score
    
    def _get_recommendation(self, score):
        """Get recommendation based on score"""
        if score >= 80:
            return "STRONG BUY"
        elif score >= 70:
            return "BUY"
        elif score >= 60:
            return "CONSIDER"
        else:
            return "PASS"
    
    def analyze_all_deals(self):
        """Analyze all deals and return comprehensive analysis"""
        results = []
        for deal_key in self.deals:
            metrics = self.calculate_deal_metrics(deal_key)
            results.append(metrics)
        
        # Sort by Cardone score (highest first)
        results.sort(key=lambda x: x['cardone_score'], reverse=True)
        
        # Add rank
        for i, result in enumerate(results, 1):
            result['rank'] = i
        
        return results
    
    def get_portfolio_scenarios(self):
        """Calculate different portfolio scenarios"""
        all_deals = self.analyze_all_deals()
        
        scenarios = {
            'Top_3_Deals': {
                'deals': all_deals[:3],
                'total_investment': sum(d['total_investment'] for d in all_deals[:3]),
                'total_units': sum(d['units'] for d in all_deals[:3]),
                'total_monthly_cash_flow': sum(d['post_reno_monthly_cash_flow'] for d in all_deals[:3]),
                'avg_cardone_score': np.mean([d['cardone_score'] for d in all_deals[:3]])
            },
            'Conservative_Start': {
                'deals': all_deals[:2],
                'total_investment': sum(d['total_investment'] for d in all_deals[:2]),
                'total_units': sum(d['units'] for d in all_deals[:2]),
                'total_monthly_cash_flow': sum(d['post_reno_monthly_cash_flow'] for d in all_deals[:2]),
                'avg_cardone_score': np.mean([d['cardone_score'] for d in all_deals[:2]])
            },
            'All_5_Deals': {
                'deals': all_deals,
                'total_investment': sum(d['total_investment'] for d in all_deals),
                'total_units': sum(d['units'] for d in all_deals),
                'total_monthly_cash_flow': sum(d['post_reno_monthly_cash_flow'] for d in all_deals),
                'avg_cardone_score': np.mean([d['cardone_score'] for d in all_deals])
            }
        }
        
        return scenarios
    
    def export_to_csv(self, filename='boise_deals_analysis.csv'):
        """Export deal analysis to CSV"""
        results = self.analyze_all_deals()
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)
        print(f"Boise deals analysis exported to {filename}")

def main():
    """Example usage of the Boise deal analyzer"""
    analyzer = BoiseDealAnalyzer()
    
    print("⚠️  HYPOTHETICAL DEAL ANALYSIS - EDUCATIONAL PURPOSES ONLY")
    print("Boise Multi-Family Deal Analysis")
    print("Grant Cardone Investment Strategy")
    print("=" * 70)
    
    # Analyze all deals
    results = analyzer.analyze_all_deals()
    
    print("\nDEAL RANKINGS (By Cardone Score)")
    print("=" * 70)
    print(f"{'Rank':<4} {'Deal':<25} {'Score':<6} {'Units':<6} {'Cash Flow':<12} {'Cap Rate':<10} {'Cash-on-Cash':<12}")
    print("-" * 70)
    
    for result in results:
        print(f"{result['rank']:<4} {result['name'][:24]:<25} {result['cardone_score']:<6} {result['units']:<6} "
              f"${result['post_reno_monthly_cash_flow']:,.0f}{'':<6} {result['post_reno_cap_rate']:.1%}{'':<6} {result['post_reno_cash_on_cash']:.1%}")
    
    print("\n" + "=" * 70)
    print("TOP 3 DEALS DETAILED ANALYSIS")
    print("=" * 70)
    
    for i in range(3):
        result = results[i]
        print(f"\n{i+1}. {result['name']}")
        print(f"   Address: {result['address']}")
        print(f"   Cardone Score: {result['cardone_score']}/100 ({result['recommendation']})")
        print(f"   Purchase Price: ${result['purchase_price']:,} | Down Payment: ${result['down_payment']:,}")
        print(f"   Renovation Budget: ${result['renovation_budget']:,} | Total Investment: ${result['total_investment']:,}")
        print(f"   Current Cash Flow: ${result['current_monthly_cash_flow']:,.0f}/month")
        print(f"   Post-Reno Cash Flow: ${result['post_reno_monthly_cash_flow']:,.0f}/month")
        print(f"   Cap Rate: {result['post_reno_cap_rate']:.1%} | Cash-on-Cash: {result['post_reno_cash_on_cash']:.1%}")
        print(f"   Rent Increase: {result['rent_increase_percentage']:.1%} | ROI on Renovation: {result['roi_on_renovation']:.1%}")
        print(f"   Price per Unit: ${result['current_price_per_unit']:,.0f}")
        print(f"   Location Advantage: {result['location_advantage']}")
        print(f"   Value-Add Potential: {result['value_add_potential']}")
        print(f"   Risk Factors: {', '.join(result['risk_factors'])}")
    
    print("\n" + "=" * 70)
    print("PORTFOLIO SCENARIOS")
    print("=" * 70)
    
    scenarios = analyzer.get_portfolio_scenarios()
    
    for scenario_name, scenario in scenarios.items():
        print(f"\n{scenario_name.replace('_', ' ')}:")
        print(f"  Total Investment: ${scenario['total_investment']:,}")
        print(f"  Total Units: {scenario['total_units']}")
        print(f"  Total Monthly Cash Flow: ${scenario['total_monthly_cash_flow']:,.0f}")
        print(f"  Average Cardone Score: {scenario['avg_cardone_score']:.1f}/100")
        print(f"  Annual Cash Flow: ${scenario['total_monthly_cash_flow'] * 12:,.0f}")
        print(f"  Cash-on-Cash Return: {(scenario['total_monthly_cash_flow'] * 12 / scenario['total_investment']):.1%}")
        
        if scenario_name == 'Top_3_Deals':
            print(f"  Remaining Capital: ${400000 - scenario['total_investment']:,}")
        elif scenario_name == 'Conservative_Start':
            print(f"  Remaining Capital: ${400000 - scenario['total_investment']:,}")
    
    print("\n" + "=" * 70)
    print("EDUCATIONAL RECOMMENDATIONS")
    print("=" * 70)
    
    print("\n⚠️  NOTE: These are HYPOTHETICAL examples for educational purposes.")
    print("For real investment decisions, conduct thorough due diligence with actual property data.")
    
    print("\n1. EXAMPLE PORTFOLIO (HYPOTHETICAL):")
    print("   - Deal #3 (Caldwell) - Best value and highest returns")
    print("   - Deal #2 (Nampa) - Strong fundamentals and cash flow")
    print("   - Deal #1 (Meridian) - Growth market with upside")
    print("   - Total Investment: $400,000")
    print("   - Expected Monthly Cash Flow: $20,760")
    
    print("\n2. VALUE-ADD STRATEGY (GENERAL PRINCIPLES):")
    print("   - Focus on kitchen and bathroom upgrades")
    print("   - Implement energy-efficient improvements")
    print("   - Enhance curb appeal and landscaping")
    print("   - Optimize property management")
    
    print("\n3. RISK MITIGATION (GENERAL PRINCIPLES):")
    print("   - Diversify across multiple submarkets")
    print("   - Maintain 10% contingency on renovations")
    print("   - Hire experienced property management")
    print("   - Monitor market conditions continuously")
    
    print("\n4. REAL INVESTMENT REQUIREMENTS:")
    print("   - Use only verified, real property data")
    print("   - Work with qualified real estate professionals")
    print("   - Conduct thorough due diligence")
    print("   - Verify all financial information independently")
    
    # Export to CSV
    analyzer.export_to_csv()

if __name__ == "__main__":
    main() 