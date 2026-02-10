#!/usr/bin/env python3
"""
Flask API backend for Mr. Car application
Serves vehicle data and market pricing to frontend
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
import os

# Add execution folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

from scrape_patentechile import get_car_info_by_plate
from scrape_market_prices import search_market_price
from pricing_engine import PricingEngine

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for frontend access


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (images, css, js, etc.)"""
    return send_from_directory('.', filename)


@app.route('/api/vehicle/<plate>', methods=['GET'])
def get_vehicle(plate):
    """Get vehicle information by plate number"""
    try:
        result = get_car_info_by_plate(plate)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/market-price', methods=['GET'])
def get_market_price():
    """Get market price estimation with complete pricing breakdown"""
    try:
        make = request.args.get('make')
        model = request.args.get('model')
        year = request.args.get('year')
        mileage = request.args.get('mileage', 'N/A')
        
        if not all([make, model, year]):
            return jsonify({
                "success": False,
                "error": "Missing required parameters: make, model, year"
            }), 400
        
        # Get market price from scraper
        market_result = search_market_price(make, model, year)
        
        # If no market price found, use estimation model
        if not market_result.get('success') or not market_result.get('average_price'):
            # Simple depreciation model for old cars
            try:
                car_age = 2026 - int(year)
                # Estimate: $8M new, depreciate 12% per year
                estimated_price = 8000000 * (0.88 ** car_age)
                estimated_price = max(1500000, estimated_price)  # Minimum $1.5M
                market_result['average_price'] = int(estimated_price)
                market_result['estimated'] = True
                market_result['success'] = True
            except:
                return jsonify({
                    "success": False,
                    "error": "Could not determine market price"
                }), 500
        
        # Calculate complete pricing using pricing engine
        pricing_engine = PricingEngine()
        pricing = pricing_engine.calculate_pricing(market_result['average_price'])
        
        # Combine market data with pricing calculations
        response = {
            "success": True,
            "vehicle": {
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage
            },
            "market_data": {
                "price": pricing['market_price'],
                "estimated": market_result.get('estimated', False),
                "num_listings": market_result.get('num_listings', 0),
                "price_range": {
                    "min": market_result.get('min_price'),
                    "max": market_result.get('max_price')
                }
            },
            "pricing": {
                "market_price": pricing['market_price'],
                "immediate_offer": pricing['immediate_offer'],
                "consignment_liquidation": pricing['consignment_liquidation'],
                "consignment_type": pricing['consignment_type']
            }
        }
        
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("🚗 Mr. Car API Server Starting...")
    print("📍 Access the web app: http://localhost:8080")
    print("📡 API endpoints:")
    print("   - GET /api/vehicle/<plate>")
    print("   - GET /api/market-price?make=X&model=Y&year=Z")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8080)
