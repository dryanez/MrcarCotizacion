#!/usr/bin/env python3
"""
Build a SQLite database from all SGPRT Excel files.
Processes all xlsx files, deduplicates by plate (PPU), keeps latest data.
"""

import os
import sys
import time
import sqlite3
import openpyxl
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'carpeta sin título')
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vehicles.db')

# Map month names to numbers for sorting
MONTH_MAP = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
}

def extract_date_key(filename):
    """Extract a sortable date key from filename like SGPRT_RB_oct-2025.xlsx"""
    # Match patterns like 'ene-2026' or 'dic-2025'
    match = re.search(r'[_-](ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[_-](\d{4})', filename.lower())
    if match:
        month = MONTH_MAP.get(match.group(1), 0)
        year = int(match.group(2))
        return year * 100 + month
    return 0

def build_database():
    """Build SQLite database from all Excel files."""
    
    if not os.path.isdir(DATA_DIR):
        print(f"❌ Data directory not found: {DATA_DIR}")
        sys.exit(1)
    
    # Find all xlsx files
    xlsx_files = sorted(
        [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx') and f.startswith('SGPRT')],
        key=extract_date_key  # Process oldest first, so newest overwrites
    )
    
    print(f"Found {len(xlsx_files)} Excel files to process")
    print(f"Processing oldest → newest (latest data wins)\n")
    
    # Create/reset database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE vehicles (
            plate TEXT PRIMARY KEY,
            make TEXT,
            model TEXT,
            year INTEGER,
            vehicle_type_code INTEGER,
            fuel_code INTEGER,
            service_code INTEGER,
            region_code TEXT,
            source_file TEXT
        )
    ''')
    
    # Create index on plate for fast lookups
    cursor.execute('CREATE INDEX idx_plate ON vehicles(plate)')
    
    total_rows = 0
    total_inserted = 0
    total_updated = 0
    start_time = time.time()
    
    for i, filename in enumerate(xlsx_files):
        filepath = os.path.join(DATA_DIR, filename)
        file_start = time.time()
        date_key = extract_date_key(filename)
        
        print(f"[{i+1}/{len(xlsx_files)}] Processing {filename}...", end=" ", flush=True)
        
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active
        
        rows_in_file = 0
        inserted = 0
        updated = 0
        
        batch = []
        
        for row in ws.iter_rows(min_row=2, max_col=8, values_only=True):
            if len(row) < 8 or not row[1]:
                continue
            
            rows_in_file += 1
            plate = str(row[1]).upper().strip()
            if not plate:
                continue
            
            record = (
                plate,
                str(row[5]).strip() if row[5] else None,  # MARCA
                str(row[6]).strip() if row[6] else None,  # MODELO
                int(row[7]) if row[7] else None,           # ANO_FABRICACION
                int(row[2]) if row[2] else None,           # COD_VEHICULO
                int(row[3]) if row[3] else None,           # COD_COMBUSTIBLE
                int(row[4]) if row[4] else None,           # COD_SERVICIO
                str(row[0]).strip() if row[0] else None,   # COD_PRT (region)
                filename
            )
            batch.append(record)
            
            if len(batch) >= 10000:
                cursor.executemany('''
                    INSERT OR REPLACE INTO vehicles 
                    (plate, make, model, year, vehicle_type_code, fuel_code, service_code, region_code, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch)
                batch = []
        
        # Insert remaining batch
        if batch:
            cursor.executemany('''
                INSERT OR REPLACE INTO vehicles 
                (plate, make, model, year, vehicle_type_code, fuel_code, service_code, region_code, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch)
        
        conn.commit()
        wb.close()
        
        elapsed = time.time() - file_start
        total_rows += rows_in_file
        print(f"✅ {rows_in_file:,} rows ({elapsed:.1f}s)")
    
    # Get final stats
    cursor.execute('SELECT COUNT(*) FROM vehicles')
    unique_plates = cursor.fetchone()[0]
    
    # Get DB file size
    conn.close()
    db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    
    total_elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"✅ DATABASE BUILT SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"📊 Total rows processed: {total_rows:,}")
    print(f"🚗 Unique plates: {unique_plates:,}")
    print(f"📁 Database size: {db_size_mb:.1f} MB")
    print(f"📍 Database path: {DB_PATH}")
    print(f"⏱️  Total time: {total_elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    build_database()
