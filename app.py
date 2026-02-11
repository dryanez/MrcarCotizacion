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
# Load .env file
load_dotenv()

# Add execution folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

# Scraper imports
from vehicle_lookup import get_car_info_by_plate
from gemini_valuation import get_vehicle_valuation
from pricing_engine import PricingEngine

# Initialize standard clients
from supabase import create_client, Client
import resend

try:
    url: str = os.environ.get("SUPABASE_URL", "")
    key: str = os.environ.get("SUPABASE_KEY", "")
    supabase: Client = create_client(url, key) if url and key and "your" not in url else None
except Exception as e:
    print(f"Warning: Supabase not initialized: {e}")
    supabase = None

try:
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
except Exception as e:
    print(f"Warning: Resend not initialized: {e}")

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



def _generate_email_html(lead_data, title="¡Gracias por confiar en Nosotros!"):
    """Generate consistent HTML email for both user and admin"""
    try:
        pricing = lead_data.get('pricing', {}) or {}
        car_data = lead_data.get('carData', {}) or {}
        
        # Safe currency formatting helper
        def format_currency(value):
            try:
                if value is None: return "0"
                return f"{int(value):,}"
            except (ValueError, TypeError):
                return str(value)

        market_price = format_currency(pricing.get('market_price', 0))
        immediate_offer = format_currency(pricing.get('immediate_offer', 0))
        consignment_liquidation = format_currency(pricing.get('consignment_liquidation', 0))
        
        return f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #667eea; text-align: center;">{title}</h2>
        <p>Estimado(a) <strong>{lead_data.get('firstName')} {lead_data.get('lastName')}</strong>,</p>
        <p>Hemos recibido los detalles de la cotización:</p>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px; border: 1px solid #eee;">
            <tr style="background-color: #f8f9fa;"><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Nombre:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('firstName')} {lead_data.get('lastName')}</td></tr>
            <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Teléfono:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('phone')}</td></tr>
            <tr style="background-color: #f8f9fa;"><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Email:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('email')}</td></tr>
            <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Región:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('region')}</td></tr>
            <tr style="background-color: #f8f9fa;"><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Comuna:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('commune')}</td></tr>
            <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Patente:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('plate', '').upper()}</td></tr>
            <tr style="background-color: #f8f9fa;"><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Marca:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{car_data.get('make')}</td></tr>
            <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Modelo:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{car_data.get('model')}</td></tr>
            <tr style="background-color: #f8f9fa;"><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Versión:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('version', 'No especificado')}</td></tr>
            <tr><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Año:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{car_data.get('year')}</td></tr>
            <tr style="background-color: #f8f9fa;"><td style="padding: 10px; font-weight: bold; border-bottom: 1px solid #eee;">Kilometraje:</td><td style="padding: 10px; border-bottom: 1px solid #eee;">{lead_data.get('mileage')} km</td></tr>
        </table>

        <div style="background: #f7fafc; padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid #e2e8f0;">
            <h3 style="color: #2d3748; margin-top: 0; text-align: center;">Resumen de Valoración</h3>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #cbd5e0; padding: 8px 0;">
                <span>Valor de Mercado:</span>
                <strong>${market_price}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #cbd5e0; padding: 8px 0;">
                <span>Oferta Inmediata:</span>
                <strong>${immediate_offer}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                <span>Consignación:</span>
                <strong>${consignment_liquidation}</strong>
            </div>
        </div>

        <p style="margin-top: 30px; text-align: center; color: #718096; font-size: 14px;">
            © 2026 Mr. Car - Todos los derechos reservados.
        </p>
    </div>
    """
    except Exception as e:
        print(f"❌ Error generating email HTML: {e}")
        return f"<pre>Error generating HTML: {e}</pre>"


@app.route('/api/submit-lead', methods=['POST'])
def submit_lead():
    """
    Submit lead data:
    1. Save to Supabase
    2. Send email to User
    3. Send email to Admin
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        print("📝 Received lead data:", data)

        # 1. Save to Supabase
        if supabase:
            try:
                # Prepare data for insertion (match your DB schema)
                lead_entry = {
                    "first_name": data.get('firstName'),
                    "last_name": data.get('lastName'),
                    "email": data.get('email'),
                    "phone": data.get('phone'),
                    "region": data.get('region'),
                    "commune": data.get('commune'),
                    "plate": data.get('plate'),
                    "make": data.get('carData', {}).get('make'),
                    "model": data.get('carData', {}).get('model'),
                    "year": data.get('carData', {}).get('year'),
                    "version": data.get('version'),
                    "mileage": data.get('mileage'),
                    "market_price": data.get('pricing', {}).get('market_price'),
                    "immediate_offer": data.get('pricing', {}).get('immediate_offer'),
                    "consignment_price": data.get('pricing', {}).get('consignment_liquidation')
                }
                supabase.table('leads').insert(lead_entry).execute()
                print("✅ Lead saved to Supabase")
            except Exception as db_err:
                print(f"❌ Error saving to Supabase: {db_err}")
                # Don't fail the request if DB fails, still try to email
        
        # 2. Send Emails (if Resend is configured)
        resend_key = os.environ.get("RESEND_API_KEY")
        if resend_key and "your" not in resend_key:
            try:
                # Email to User
                user_html = _generate_email_html(data)

                # FORCE TEST EMAIL: Always send to mrcarfy@gmail.com in dev mode
                # because Resend only allows sending to verified email without a domain.
                verified_email = "mrcarfy@gmail.com"
                
                resend.Emails.send({
                    "from": "Mr. Car <onboarding@resend.dev>",
                    "to": verified_email,  # Override user email for testing
                    "subject": f"[TESTING] 🚗 Cotización para {data.get('email')} - {data.get('carData', {}).get('make')}",
                    "html": user_html
                })
                print(f"✅ Email sent to TEST address: {verified_email} (intended for {data.get('email')})")

                # Email to Admin (Reuse the same HTML but with a different title)
                admin_html = _generate_email_html(data, title="🔔 Nuevo Lead Recibido")
                
                admin_email = os.environ.get("ADMIN_EMAIL", verified_email)
                resend.Emails.send({
                    "from": "Mr. Car System <onboarding@resend.dev>",
                    "to": admin_email,
                    "subject": f"🔔 Nuevo Lead: {data.get('firstName')} {data.get('lastName')} - {data.get('carData', {}).get('model')}",
                    "html": admin_html
                })
                print(f"✅ Email sent to admin: {admin_email}")

            except Exception as email_err:
                print(f"❌ Error sending email: {email_err}")
        else:
            print("⚠️ Resend API Key missing or invalid. Skipping email sending.")

        return jsonify({"success": True})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


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
    print("   - POST /api/submit-lead")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8080)
