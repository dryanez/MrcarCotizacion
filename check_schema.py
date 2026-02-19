
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Missing SUPABASE_URL or SUPABASE_KEY")
    exit(1)

supabase = create_client(url, key)

try:
    # Try to insert a dummy record with the new columns to see if it fails
    # This is a bit hacky but a quick way to check if columns exist without direct schema access
    # We'll use a transaction that we expect to fail or we'll just check the error message
    
    # Actually, a better way is to just select a single row and print its keys
    response = supabase.table('leads').select("*").limit(1).execute()
    
    if response.data:
        print("Existing columns:", response.data[0].keys())
    else:
        print("Table is empty, cannot infer schema from data. Attempting to insert dummy with new columns...")
        try:
            # Try to insert with a column we hope exists or we want to check
            # We'll just try to select 'appointment_date' specifically
            response = supabase.table('leads').select("appointment_date").limit(1).execute()
            print("Column 'appointment_date' EXISTS.")
        except Exception as e:
             print(f"Column 'appointment_date' likely DOES NOT EXIST. Error: {e}")

except Exception as e:
    print(f"Error checking schema: {e}")
