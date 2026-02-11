#!/usr/bin/env python3
"""
Vehicle Lookup from SQLite database.
Fast, efficient, and deployable vehicle plate lookups.
"""

import os
import sys
import json
import sqlite3

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vehicles.db')

def get_car_info_by_plate(plate):
    """
    Look up vehicle info by plate number using SQLite database.
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

    if not os.path.exists(DB_PATH):
        result["error"] = f"Vehicle database not found. Run build_vehicle_db.py first."
        return result

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT make, model, year 
            FROM vehicles 
            WHERE plate = ? 
            LIMIT 1
        ''', (plate,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result["success"] = True
            result["make"] = row[0]
            result["model"] = row[1]
            result["year"] = str(row[2]) if row[2] else None
        else:
            result["error"] = f"Patente {plate} no encontrada en la base de datos"
    
    except Exception as e:
        result["error"] = f"Database error: {str(e)}"
    
    return result


if __name__ == "__main__":
    test_plate = sys.argv[1] if len(sys.argv) > 1 else "VLTJ50"
    result = get_car_info_by_plate(test_plate)
    print(json.dumps(result, indent=2, ensure_ascii=False))
