#!/usr/bin/env python3
"""
Vehicle Lookup from Supabase Postgres.
Fast, cloud-hosted, and deployable vehicle plate lookups.
"""

import os
import sys
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client (cached)
_supabase_client = None

def get_supabase_client():
    """Get or create Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url and key and "your" not in url:
            _supabase_client = create_client(url, key)
    return _supabase_client


def get_car_info_by_plate(plate):
    """
    Look up vehicle info by plate number using Supabase Postgres.
    Returns dict with same signature as the old scraper for compatibility.
    """
    plate = plate.upper().strip()

    result = {
        "success": False,
        "plate": plate,
        "make": None,
        "model": None,
        "year": None,
        "owner": None,
        "rut": None,
        "error": None
    }

    supabase = get_supabase_client()
    
    if not supabase:
        result["error"] = "Supabase not configured. Check SUPABASE_URL and SUPABASE_KEY in .env"
        return result

    try:
        response = supabase.table("vehicles").select("make, model, year").eq("plate", plate).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            vehicle = response.data[0]
            result["success"] = True
            result["make"] = vehicle.get("make")
            result["model"] = vehicle.get("model")
            result["year"] = str(vehicle.get("year")) if vehicle.get("year") else None
        else:
            result["error"] = f"Patente {plate} no encontrada en la base de datos"
    
    except Exception as e:
        result["error"] = f"Database error: {str(e)}"
    
    return result


if __name__ == "__main__":
    test_plate = sys.argv[1] if len(sys.argv) > 1 else "VLTJ50"
    result = get_car_info_by_plate(test_plate)
    print(json.dumps(result, indent=2, ensure_ascii=False))
