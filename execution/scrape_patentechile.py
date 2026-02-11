#!/usr/bin/env python3
"""
Vehicle plate lookup using Gemini AI with Google Search grounding.
Replaces Selenium-based scraping — works in serverless environments (Vercel).
"""

import os
import json
import re
from google import genai
from google.genai import types


def get_car_info_by_plate(plate: str) -> dict:
    """
    Look up Chilean vehicle information by license plate using Gemini AI.
    
    Args:
        plate: Chilean license plate (e.g., "LXBW68")
    
    Returns:
        Dictionary with car information
    """
    
    plate = plate.upper().strip()
    
    result = {
        "success": False,
        "plate": plate,
        "make": None,
        "model": None,
        "year": None,
        "owner_name": None,
        "owner_rut": None,
        "error": None
    }
    
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('API_KEY')
    
    if not api_key:
        result["error"] = "Google API Key is missing. Set GOOGLE_API_KEY in .env"
        return result
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Busca información del vehículo con patente (placa) "{plate}" en Chile.
    
    PROTOCOLO DE BÚSQUEDA:
    1. Busca en sitios chilenos como patentechile.com, autofact.cl, patentesonline.cl, vehiculo.cl, nuestroauto.cl
    2. Busca la MARCA, MODELO y AÑO del vehículo
    3. Si encuentras información del propietario (nombre y RUT), inclúyela
    
    RESPONDE ÚNICAMENTE con JSON válido (sin markdown, sin texto adicional):
    {{
      "make": "MARCA del vehículo (ej: TOYOTA, HYUNDAI, MAZDA)",
      "model": "MODELO completo del vehículo (ej: COROLLA 1.8 GLI, TUCSON 2.0)",
      "year": "AÑO del vehículo (ej: 2020)",
      "owner_name": "Nombre del propietario si se encontró, null si no",
      "owner_rut": "RUT del propietario si se encontró, null si no"
    }}
    
    Si NO encuentras datos del vehículo, responde:
    {{
      "make": null,
      "model": null,
      "year": null,
      "owner_name": null,
      "owner_rut": null
    }}
    """
    
    try:
        print(f"🔍 Looking up plate {plate} via Gemini AI...")
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        )
        
        text = response.text or "{}"
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', text)
        json_string = json_match.group(0) if json_match else "{}"
        
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON: {e}")
            print(f"   Raw response: {text[:500]}")
            result["error"] = "Error parsing vehicle data response"
            return result
        
        # Map results
        result["make"] = data.get("make")
        result["model"] = data.get("model")
        result["year"] = data.get("year")
        result["owner_name"] = data.get("owner_name")
        result["owner_rut"] = data.get("owner_rut")
        
        if result["make"] and result["model"]:
            result["success"] = True
            print(f"✅ Found: {result['make']} {result['model']} ({result['year']})")
        else:
            result["error"] = "No vehicle data found for this plate"
            print(f"❌ No data found for plate {plate}")
            
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        print(f"❌ Error: {e}")
    
    return result


def main():
    """Test the lookup"""
    import sys
    
    if len(sys.argv) > 1:
        plate = sys.argv[1]
    else:
        plate = "LXBW68"
    
    print(f"\n{'='*60}")
    print(f"🚗 Searching for plate: {plate}")
    print(f"{'='*60}\n")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    info = get_car_info_by_plate(plate)
    
    print(f"\n{'='*60}")
    print("📊 RESULTS:")
    print(f"{'='*60}")
    print(f"✓ Success:    {info['success']}")
    print(f"📋 Plate:      {info['plate']}")
    print(f"🏢 Make:       {info['make']}")
    print(f"🚙 Model:      {info['model']}")
    print(f"📅 Year:       {info['year']}")
    print(f"👤 Owner:      {info['owner_name']}")
    print(f"🆔 RUT:        {info['owner_rut']}")
    
    if info.get('error'):
        print(f"\n❌ Error: {info['error']}")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
