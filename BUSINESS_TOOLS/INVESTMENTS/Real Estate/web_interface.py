#!/usr/bin/env python3
"""
Web Interface for Real Estate Deal Finder
Flask-based web application for finding qualifying properties
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import json
import os
from datetime import datetime
import pandas as pd
from real_estate_scraper import DealAnalyzer, Property
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global analyzer instance
analyzer = None

def get_analyzer():
    """Get or create analyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = DealAnalyzer()
    return analyzer

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_deals():
    """API endpoint to search for deals"""
    try:
        data = request.get_json()
        location = data.get('location', 'Boise, ID')
        min_price = data.get('min_price', 0)
        max_price = data.get('max_price', 1000000)
        min_units = data.get('min_units', 5)
        max_units = data.get('max_units', 50)
        min_cap_rate = data.get('min_cap_rate', 6.5)
        min_cash_on_cash = data.get('min_cash_on_cash', 8.0)
        
        # Update filter criteria
        analyzer = get_analyzer()
        analyzer.filter.criteria.update({
            'min_cap_rate': min_cap_rate / 100,
            'min_cash_on_cash': min_cash_on_cash / 100,
            'min_units': min_units,
            'max_units': max_units
        })
        
        # Run search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        qualifying_deals = loop.run_until_complete(analyzer.find_qualifying_deals(location))
        loop.close()
        
        # Convert to JSON-serializable format
        deals_data = []
        for deal in qualifying_deals:
            metrics = deal.calculate_metrics()
            deals_data.append({
                'address': deal.address,
                'source': deal.source,
                'price': deal.price,
                'units': deal.units,
                'year_built': deal.year_built,
                'price_per_unit': metrics['price_per_unit'],
                'down_payment': metrics['down_payment'],
                'monthly_gross_income': metrics['monthly_gross_income'],
                'monthly_net_income': metrics['monthly_net_income'],
                'monthly_cash_flow': metrics['monthly_cash_flow'],
                'annual_cash_flow': metrics['annual_cash_flow'],
                'cap_rate': metrics['cap_rate'],
                'cash_on_cash_return': metrics['cash_on_cash_return'],
                'cardone_score': deal.calculate_cardone_score(),
                'recommendation': deal.get_recommendation(),
                'url': deal.url,
                'listing_date': deal.listing_date
            })
        
        return jsonify({
            'success': True,
            'deals': deals_data,
            'total_count': len(deals_data),
            'search_criteria': {
                'location': location,
                'min_price': min_price,
                'max_price': max_price,
                'min_units': min_units,
                'max_units': max_units,
                'min_cap_rate': min_cap_rate,
                'min_cash_on_cash': min_cash_on_cash
            }
        })
        
    except Exception as e:
        logger.error(f"Error in search_deals: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export', methods=['POST'])
def export_deals():
    """Export deals to CSV"""
    try:
        data = request.get_json()
        deals_data = data.get('deals', [])
        
        if not deals_data:
            return jsonify({'success': False, 'error': 'No deals to export'})
        
        # Create DataFrame
        df = pd.DataFrame(deals_data)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qualifying_deals_{timestamp}.csv"
        
        # Save to file
        df.to_csv(filename, index=False)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'Exported {len(deals_data)} deals to {filename}'
        })
        
    except Exception as e:
        logger.error(f"Error in export_deals: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download exported file"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 