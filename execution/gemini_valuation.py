#!/usr/bin/env python3
"""
Gemini AI Vehicle Valuation Service
Uses Google Gemini with Google Search grounding to get accurate Chilean market prices.
Replaces all Selenium-based scrapers.
"""

import os
import json
import re
from google import genai
from google.genai import types


def get_vehicle_valuation(year: str, make: str, model: str, trim: str = "",
                          mileage: str = "0", region: str = "Santiago"):
    """
    Get vehicle valuation using Gemini AI with Google Search grounding.
    
    Args:
        year: Vehicle year (e.g., "2018")
        make: Vehicle make (e.g., "MAZDA")
        model: Vehicle model (e.g., "CX-5")
        trim: Vehicle trim (e.g., "GT 2.0")
        mileage: Mileage in km (e.g., "80000")
        region: Region in Chile (e.g., "Santiago")
    
    Returns:
        dict with valuation data and source links
    """
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('API_KEY')
    
    if not api_key:
        raise ValueError("Google API Key is missing. Set GOOGLE_API_KEY in .env")
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Act as a senior vehicle appraiser specializing EXCLUSIVELY in the Chilean automotive market (Chile).

    TARGET VEHICLE: {year} {make} {model} {trim or ''}
    MILEAGE: {mileage} km
    LOCATION: {region}, Chile
    CURRENCY: CLP (Peso Chileno)

    STRICT SEARCH & ANALYSIS PROTOCOL:
    1. SEARCH: You MUST verify prices ONLY on Chilean websites.
       - Primary Sources: chileautos.cl, mercadolibre.cl, yapo.cl, autocosmos.cl, kavak.com/cl, macal.cl, autofact.cl.
       - EXCLUDE: Prices in USD, EUR, or UF (unless converted to CLP).
       - EXCLUDE: Foreign sites (cars.com, etc).

    2. DATA FILTERING:
       - Factor in the MILEAGE ({mileage} km).
       - Analyze at least 3-5 specific listings.

    3. URL EXTRACTION (CRITICAL):
       - You MUST extract the direct URLs of the listings you found.
       - If you find a listing on Chileautos or MercadoLibre, copy the URL into the 'foundListings' array in the JSON.
       - The user needs to click these links to verify the price.

    RETURN JSON ONLY (No markdown):
    {{
      "minPrice": number (integer, CLP),
      "maxPrice": number (integer, CLP),
      "avgPrice": number (integer, CLP),
      "currency": "CLP",
      "marketAnalysis": "string (2-3 sentences explaining availability and price range)",
      "confidenceScore": number (0-100),
      "foundListings": [
         {{ 
           "title": "string (e.g. Chileautos - 2019 Toyota Rav4 - $15.000.000)", 
           "url": "string (The full http link to the listing)",
           "price": "string (The price of this specific listing)"
         }}
      ]
    }}
    """
    
    print(f"\n{'='*60}")
    print(f"🤖 Gemini AI Valuation: {year} {make} {model} {trim}")
    print(f"   Mileage: {mileage} km | Region: {region}")
    print(f"{'='*60}\n")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
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
            raise ValueError("Error al procesar los datos de la cotización.")
        
        # Extract sources from grounding metadata
        system_sources = []
        try:
            candidates = response.candidates
            if candidates and len(candidates) > 0:
                grounding_metadata = candidates[0].grounding_metadata
                if grounding_metadata and grounding_metadata.grounding_chunks:
                    for chunk in grounding_metadata.grounding_chunks:
                        if chunk.web and chunk.web.uri and chunk.web.title:
                            system_sources.append({
                                "title": chunk.web.title,
                                "uri": chunk.web.uri
                            })
        except Exception as e:
            print(f"⚠️ Error extracting grounding metadata: {e}")
        
        # Extract sources from model's foundListings
        model_sources = []
        for listing in data.get("foundListings", []):
            if listing.get("url"):
                model_sources.append({
                    "title": listing.get("title", "Listado Vehículo"),
                    "uri": listing["url"]
                })
        
        # Merge and deduplicate sources (prefer Chilean sites)
        all_sources = system_sources + model_sources
        unique_sources = {}
        for source in all_sources:
            uri = source.get("uri", "")
            if uri and uri not in unique_sources:
                # Filter for Chilean sites
                if any(domain in uri for domain in ['.cl', 'mercadolibre', 'chileautos', 'yapo', 'kavak', 'autofact', 'autocosmos']):
                    unique_sources[uri] = source
        
        sources = list(unique_sources.values())
        
        print(f"✅ Valuation complete!")
        print(f"   💰 Average: ${data.get('avgPrice', 0):,} CLP")
        print(f"   📉 Range: ${data.get('minPrice', 0):,} - ${data.get('maxPrice', 0):,}")
        print(f"   📊 Confidence: {data.get('confidenceScore', 0)}%")
        print(f"   🔗 Sources: {len(sources)}")
        
        return {
            "data": data,
            "sources": sources
        }
        
    except Exception as e:
        print(f"❌ Gemini Valuation Error: {e}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"No se pudo obtener la cotización: {str(e)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python gemini_valuation.py <YEAR> <MAKE> <MODEL> [MILEAGE]")
        sys.exit(1)
    
    year = sys.argv[1]
    make = sys.argv[2]
    model = sys.argv[3]
    mileage = sys.argv[4] if len(sys.argv) > 4 else "50000"
    
    result = get_vehicle_valuation(year, make, model, mileage=mileage)
    print(json.dumps(result, indent=2, ensure_ascii=False))
