#!/usr/bin/env python3
"""
Grant Cardone Real Estate Deal Analysis Calculator
Based on Cardone's investment criteria and strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime

class CardoneDealAnalyzer:
    def __init__(self):
        self.deals = []
        
    def analyze_property(self, property_data):
        """
        Analyze a property based on Grant Cardone's criteria
        
        Args:
            property_data (dict): Property information including:
                - purchase_price: Purchase price
                - down_payment: Down payment amount
                - monthly_rent: Total monthly rent
                - monthly_expenses: Total monthly expenses
                - units: Number of units
                - market_growth: Annual market growth rate
                - value_add_potential: Potential value increase from improvements
        """
        
        # Calculate key metrics
        loan_amount = property_data['purchase_price'] - property_data['down_payment']
        monthly_mortgage = self._calculate_mortgage(loan_amount, 6.5, 25)  # 6.5% rate, 25 years
        monthly_cash_flow = property_data['monthly_rent'] - property_data['monthly_expenses'] - monthly_mortgage
        
        # Cardone's key metrics
        cap_rate = (property_data['monthly_rent'] * 12 - property_data['monthly_expenses'] * 12) / property_data['purchase_price']
        cash_on_cash = (monthly_cash_flow * 12) / property_data['down_payment']
        price_per_unit = property_data['purchase_price'] / property_data['units']
        
        # Score the deal (0-100)
        score = self._calculate_deal_score(property_data, cap_rate, cash_on_cash, price_per_unit)
        
        analysis = {
            'property_id': len(self.deals) + 1,
            'purchase_price': property_data['purchase_price'],
            'down_payment': property_data['down_payment'],
            'loan_amount': loan_amount,
            'monthly_rent': property_data['monthly_rent'],
            'monthly_expenses': property_data['monthly_expenses'],
            'monthly_mortgage': monthly_mortgage,
            'monthly_cash_flow': monthly_cash_flow,
            'annual_cash_flow': monthly_cash_flow * 12,
            'cap_rate': cap_rate,
            'cash_on_cash_return': cash_on_cash,
            'price_per_unit': price_per_unit,
            'units': property_data['units'],
            'market_growth': property_data['market_growth'],
            'value_add_potential': property_data['value_add_potential'],
            'deal_score': score,
            'recommendation': self._get_recommendation(score),
            'analysis_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.deals.append(analysis)
        return analysis
    
    def _calculate_mortgage(self, principal, rate, years):
        """Calculate monthly mortgage payment"""
        monthly_rate = rate / 100 / 12
        num_payments = years * 12
        if monthly_rate == 0:
            return principal / num_payments
        return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    def _calculate_deal_score(self, property_data, cap_rate, cash_on_cash, price_per_unit):
        """Calculate deal score based on Cardone's criteria"""
        score = 0
        
        # Cap Rate (30 points)
        if cap_rate >= 0.08:
            score += 30
        elif cap_rate >= 0.07:
            score += 25
        elif cap_rate >= 0.06:
            score += 20
        elif cap_rate >= 0.05:
            score += 10
        
        # Cash on Cash Return (25 points)
        if cash_on_cash >= 0.12:
            score += 25
        elif cash_on_cash >= 0.10:
            score += 20
        elif cash_on_cash >= 0.08:
            score += 15
        elif cash_on_cash >= 0.06:
            score += 10
        
        # Price per Unit (20 points)
        if price_per_unit <= 50000:
            score += 20
        elif price_per_unit <= 75000:
            score += 15
        elif price_per_unit <= 100000:
            score += 10
        elif price_per_unit <= 150000:
            score += 5
        
        # Market Growth (15 points)
        if property_data['market_growth'] >= 0.03:
            score += 15
        elif property_data['market_growth'] >= 0.02:
            score += 10
        elif property_data['market_growth'] >= 0.01:
            score += 5
        
        # Value Add Potential (10 points)
        if property_data['value_add_potential'] >= 0.15:
            score += 10
        elif property_data['value_add_potential'] >= 0.10:
            score += 7
        elif property_data['value_add_potential'] >= 0.05:
            score += 5
        
        return score
    
    def _get_recommendation(self, score):
        """Get recommendation based on score"""
        if score >= 80:
            return "STRONG BUY"
        elif score >= 70:
            return "BUY"
        elif score >= 60:
            return "CONSIDER"
        elif score >= 50:
            return "HOLD"
        else:
            return "PASS"
    
    def get_portfolio_summary(self):
        """Get summary of all analyzed deals"""
        if not self.deals:
            return "No deals analyzed yet."
        
        df = pd.DataFrame(self.deals)
        
        summary = {
            'total_deals': len(self.deals),
            'total_investment': df['down_payment'].sum(),
            'total_portfolio_value': df['purchase_price'].sum(),
            'total_monthly_cash_flow': df['monthly_cash_flow'].sum(),
            'total_annual_cash_flow': df['annual_cash_flow'].sum(),
            'average_cap_rate': df['cap_rate'].mean(),
            'average_cash_on_cash': df['cash_on_cash_return'].mean(),
            'total_units': df['units'].sum(),
            'average_deal_score': df['deal_score'].mean(),
            'recommended_deals': len(df[df['deal_score'] >= 70])
        }
        
        return summary
    
    def export_to_csv(self, filename='deal_analysis.csv'):
        """Export deals to CSV file"""
        if self.deals:
            df = pd.DataFrame(self.deals)
            df.to_csv(filename, index=False)
            print(f"Deals exported to {filename}")
        else:
            print("No deals to export")

def main():
    """Example usage of the deal analyzer"""
    analyzer = CardoneDealAnalyzer()
    
    # Example properties based on Cardone's criteria
    example_properties = [
        {
            'purchase_price': 800000,
            'down_payment': 200000,
            'monthly_rent': 8000,
            'monthly_expenses': 2000,
            'units': 10,
            'market_growth': 0.025,
            'value_add_potential': 0.12
        },
        {
            'purchase_price': 600000,
            'down_payment': 150000,
            'monthly_rent': 6500,
            'monthly_expenses': 1800,
            'units': 8,
            'market_growth': 0.03,
            'value_add_potential': 0.15
        },
        {
            'purchase_price': 1200000,
            'down_payment': 250000,
            'monthly_rent': 12000,
            'monthly_expenses': 3000,
            'units': 14,
            'market_growth': 0.02,
            'value_add_potential': 0.10
        }
    ]
    
    print("Grant Cardone Real Estate Deal Analysis")
    print("=" * 50)
    
    for i, prop in enumerate(example_properties, 1):
        print(f"\nAnalyzing Property #{i}:")
        analysis = analyzer.analyze_property(prop)
        
        print(f"Purchase Price: ${analysis['purchase_price']:,}")
        print(f"Down Payment: ${analysis['down_payment']:,}")
        print(f"Monthly Cash Flow: ${analysis['monthly_cash_flow']:,.2f}")
        print(f"Cap Rate: {analysis['cap_rate']:.2%}")
        print(f"Cash on Cash Return: {analysis['cash_on_cash_return']:.2%}")
        print(f"Price per Unit: ${analysis['price_per_unit']:,.0f}")
        print(f"Deal Score: {analysis['deal_score']}/100")
        print(f"Recommendation: {analysis['recommendation']}")
    
    print("\n" + "=" * 50)
    print("PORTFOLIO SUMMARY")
    print("=" * 50)
    
    summary = analyzer.get_portfolio_summary()
    print(f"Total Deals Analyzed: {summary['total_deals']}")
    print(f"Total Investment: ${summary['total_investment']:,}")
    print(f"Total Portfolio Value: ${summary['total_portfolio_value']:,}")
    print(f"Total Monthly Cash Flow: ${summary['total_monthly_cash_flow']:,.2f}")
    print(f"Total Annual Cash Flow: ${summary['total_annual_cash_flow']:,}")
    print(f"Average Cap Rate: {summary['average_cap_rate']:.2%}")
    print(f"Average Cash on Cash Return: {summary['average_cash_on_cash']:.2%}")
    print(f"Total Units: {summary['total_units']}")
    print(f"Average Deal Score: {summary['average_deal_score']:.1f}/100")
    print(f"Recommended Deals: {summary['recommended_deals']}")
    
    # Export to CSV
    analyzer.export_to_csv()

if __name__ == "__main__":
    main() 