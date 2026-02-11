#!/usr/bin/env python3
"""
Vehicle Lookup from SGPRT Excel files.
Loads all .xlsx files at import time into an in-memory dictionary for instant plate lookups.
"""

import os
import sys
import json
import time
import openpyxl

# Directory where the xlsx files live (same as project root)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# In-memory vehicle database: { "LXBW68": { "make": "MAZDA", "model": "CX-5", "year": 2018 }, ... }
_vehicle_db = {}
_loaded = False


def _load_excel_files():
    """Load all SGPRT .xlsx files into memory at startup."""
    global _vehicle_db, _loaded
    if _loaded:
        return

    xlsx_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx') and f.startswith('SGPRT')]
    
    if not xlsx_files:
        print("⚠️  No SGPRT xlsx files found in project root. Vehicle lookup will return empty results.", file=sys.stderr)
        _loaded = True
        return

    start = time.time()
    total = 0

    for filename in sorted(xlsx_files):
        filepath = os.path.join(DATA_DIR, filename)
        print(f"📂 Loading {filename}...", file=sys.stderr, end=" ")
        
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active
        
        count = 0
        for row in ws.iter_rows(min_row=2, max_col=8, values_only=True):
            # Columns: COD_PRT, PPU, COD_VEHICULO, COD_COMBUSTIBLE, COD_SERVICIO, MARCA, MODELO, ANO_FABRICACION
            if len(row) >= 8 and row[1]:
                plate = str(row[1]).upper().strip()
                if plate and plate not in _vehicle_db:
                    _vehicle_db[plate] = {
                        "make": str(row[5]).strip() if row[5] else None,
                        "model": str(row[6]).strip() if row[6] else None,
                        "year": str(int(row[7])) if row[7] else None,
                    }
                    count += 1
        
        wb.close()
        total += count
        print(f"✅ {count:,} unique plates", file=sys.stderr)

    elapsed = time.time() - start
    _loaded = True
    print(f"🚗 Vehicle database loaded: {len(_vehicle_db):,} unique plates from {len(xlsx_files)} files ({elapsed:.1f}s)", file=sys.stderr)


def get_car_info_by_plate(plate):
    """
    Look up vehicle info by plate number.
    Returns dict with same signature as the old scraper for compatibility.
    """
    # Ensure data is loaded
    if not _loaded:
        _load_excel_files()

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

    vehicle = _vehicle_db.get(plate)

    if vehicle:
        result["success"] = True
        result["make"] = vehicle["make"]
        result["model"] = vehicle["model"]
        result["year"] = vehicle["year"]
    else:
        result["error"] = f"Patente {plate} no encontrada en la base de datos"

    return result


# Load data at import time so it's ready when the server starts
_load_excel_files()


if __name__ == "__main__":
    test_plate = sys.argv[1] if len(sys.argv) > 1 else "VLTJ50"
    result = get_car_info_by_plate(test_plate)
    print(json.dumps(result, indent=2, ensure_ascii=False))
