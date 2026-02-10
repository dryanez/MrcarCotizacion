#!/usr/bin/env python3
"""
Flask API backend for Mr. Car application
Serves vehicle data and Gemini AI-powered market pricing to frontend
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add execution folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

from scrape_patentechile import get_car_info_by_plate
from gemini_valuation import get_vehicle_valuation
from pricing_engine import PricingEngine

# Determine base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask with standard static folder
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (images, css, js, etc.)"""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)


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
    """Get market price estimation using Gemini AI with complete pricing breakdown"""
    try:
        make = request.args.get('make')
        model = request.args.get('model')
        year = request.args.get('year')
        mileage = request.args.get('mileage', '0')
        region = request.args.get('region', 'Santiago')
        
        if not all([make, model, year]):
            return jsonify({
                "success": False,
                "error": "Missing required parameters: make, model, year"
            }), 400
        
        # Get valuation from Gemini AI
        valuation = get_vehicle_valuation(
            year=year,
            make=make,
            model=model,
            mileage=mileage,
            region=region
        )
        
        gemini_data = valuation["data"]
        sources = valuation["sources"]
        
        avg_price = gemini_data.get("avgPrice", 0)
        
        if not avg_price or avg_price <= 0:
            return jsonify({
                "success": False,
                "error": "Gemini could not determine market price"
            }), 500
        
        # Calculate complete pricing using pricing engine
        pricing_engine = PricingEngine()
        pricing = pricing_engine.calculate_pricing(avg_price)
        
        # Build response
        response = {
            "success": True,
            "vehicle": {
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage
            },
            "market_data": {
                "price": avg_price,
                "min_price": gemini_data.get("minPrice"),
                "max_price": gemini_data.get("maxPrice"),
                "confidence": gemini_data.get("confidenceScore", 0),
                "analysis": gemini_data.get("marketAnalysis", ""),
                "estimated": False
            },
            "pricing": {
                "market_price": pricing['market_price'],
                "immediate_offer": pricing['immediate_offer'],
                "consignment_liquidation": pricing['consignment_liquidation'],
                "consignment_type": pricing['consignment_type']
            },
            "sources": sources,
            "listings": gemini_data.get("foundListings", [])
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
    print("   - GET /api/market-price?make=X&model=Y&year=Z&mileage=M")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8080)
