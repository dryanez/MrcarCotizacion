#!/usr/bin/env python3
"""
Upload vehicle data from SQLite to Supabase Postgres.
One-time migration script.
"""

import os
import sys
import sqlite3
import time
from supabase import create_client, Client

# Load environment
from dotenv import load_dotenv
load_dotenv()

SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vehicles.db')

def upload_to_supabase():
    """Upload all vehicle data to Supabase."""
    
    # Initialize Supabase
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key or "your" in url:
        print("❌ SUPABASE_URL and SUPABASE_KEY must be set in .env")
        sys.exit(1)
    
    supabase: Client = create_client(url, key)
    
    # Connect to SQLite
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite database not found: {SQLITE_DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total_count = cursor.fetchone()[0]
    print(f"📊 Total vehicles in SQLite: {total_count:,}")
    
    # Create table in Supabase (if needed)
    print("\n🔧 Creating Postgres table (if not exists)...")
    # Note: You'll need to create this table via Supabase dashboard or SQL editor:
    # CREATE TABLE vehicles (
    #     plate TEXT PRIMARY KEY,
    #     make TEXT,
    #     model TEXT,
    #     year INTEGER,
    #     vehicle_type_code INTEGER,
    #     fuel_code INTEGER,
    #     service_code INTEGER,
    #     region_code TEXT,
    #     source_file TEXT
    # );
    # CREATE INDEX idx_plate ON vehicles(plate);
    
    print("\n⚠️  IMPORTANT: Make sure you've created the 'vehicles' table in Supabase!")
    print("Run this SQL in Supabase SQL Editor:")
    print("""
CREATE TABLE IF NOT EXISTS vehicles (
    plate TEXT PRIMARY KEY,
    make TEXT,
    model TEXT,
    year INTEGER,
    vehicle_type_code INTEGER,
    fuel_code INTEGER,
    service_code INTEGER,
    region_code TEXT,
    source_file TEXT
);
CREATE INDEX IF NOT EXISTS idx_plate ON vehicles(plate);
""")
    
    response = input("\nHave you created the table? (yes/no): ").strip()
    if response.lower() != 'yes':
        print("❌ Please create the table first, then run this script again.")
        sys.exit(1)
    
    # Upload in batches
    # We are resuming from ~3,175,523
    START_OFFSET = 3175000  # Conservative rounded down number
    
    print(f"\n📤 Uploading records to Supabase...")
    print(f"🔄 RESUMING from offset {START_OFFSET:,}")
    print(f"📊 Total to upload: {total_count - START_OFFSET:,}")
    
    batch_size = 1000
    uploaded = START_OFFSET
    start_time = time.time()
    
    # Use LIMIT -1 OFFSET <offset> to skip processed rows
    # We rely on the fact that SQLite default order (rowid) is stable for a read-only DB
    cursor.execute(f"SELECT plate, make, model, year, vehicle_type_code, fuel_code, service_code, region_code, source_file FROM vehicles LIMIT -1 OFFSET {START_OFFSET}")
    
    batch = []
    rows_processed = 0
    
    for row in cursor:
        batch.append({
            "plate": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3],
            "vehicle_type_code": row[4],
            "fuel_code": row[5],
            "service_code": row[6],
            "region_code": row[7],
            "source_file": row[8]
        })
        
        if len(batch) >= batch_size:
            try:
                supabase.table("vehicles").upsert(batch).execute()
                uploaded += len(batch)
                rows_processed += len(batch)
                
                if rows_processed % 10000 == 0:
                    elapsed = time.time() - start_time
                    rate = rows_processed / elapsed
                    remaining = (total_count - uploaded) / rate if rate > 0 else 0
                    print(f"✅ {uploaded:,} / {total_count:,} ({uploaded/total_count*100:.1f}%) | {rate:.0f} rows/sec | ETA: {remaining/60:.1f} min")
                
                batch = []
            except Exception as e:
                print(f"❌ Error uploading batch: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
                # If it fails, we lose this batch in this simple script, 
                # but upsert is idempotent so re-running is safeish.
                # Ideally we'd retry the same batch.
                try:
                    supabase.table("vehicles").upsert(batch).execute()
                    print("✅ Retry successful")
                    uploaded += len(batch)
                    batch = []
                except Exception as retry_e:
                     print(f"❌ Retry failed: {retry_e}. Skipping batch.")
                     batch = []
                continue
    
    # Upload remaining batch
    if batch:
        supabase.table("vehicles").upsert(batch).execute()
        uploaded += len(batch)
    
    conn.close()
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"✅ UPLOAD COMPLETE")
    print(f"{'='*60}")
    print(f"📊 Total uploaded (session): {rows_processed:,}")
    print(f"📊 Total in DB (estimated): {uploaded:,}")
    print(f"⏱️  Time taken: {elapsed/60:.1f} minutes")
    print(f"🚀 Average rate: {rows_processed/elapsed:.0f} rows/sec")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    upload_to_supabase()
