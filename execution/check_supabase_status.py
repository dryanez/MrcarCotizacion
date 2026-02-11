#!/usr/bin/env python3
"""
Check Supabase migration status.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def check_status():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return
    
    print(f"🔗 Connecting to: {url}")
    supabase = create_client(url, key)
    
    try:
        # Check if table exists and count records
        response = supabase.table("vehicles").select("*", count="exact").limit(1).execute()
        
        count = response.count
        print(f"\n✅ Table 'vehicles' exists!")
        print(f"📊 Total records: {count:,}")
        
        # Sample a record
        if response.data:
            sample = response.data[0]
            print(f"\n📝 Sample record:")
            print(f"   Plate: {sample.get('plate')}")
            print(f"   Make: {sample.get('make')}")
            print(f"   Model: {sample.get('model')}")
            print(f"   Year: {sample.get('year')}")
        
        print(f"\n🎯 Expected total: 5,300,000")
        if count < 5300000:
            percentage = (count / 5300000) * 100
            print(f"📈 Migration progress: {percentage:.1f}%")
            print(f"⚠️  Still need to upload {5300000 - count:,} records")
        else:
            print("✅ Migration complete!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 This might mean the table doesn't exist yet.")
        print("   Run the SQL in create_vehicles_table.sql first!")

if __name__ == "__main__":
    check_status()
