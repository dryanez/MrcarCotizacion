-- Run this SQL in Supabase SQL Editor to create the vehicles table

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

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow read access (adjust as needed)
CREATE POLICY "Allow public read access" ON vehicles
    FOR SELECT
    USING (true);

-- Allow inserts and updates for migration (Enable RLS again after migration if needed)
-- Ideally use service_role key for migration, but for now we open it up
CREATE POLICY "Allow anon insert" ON vehicles FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update" ON vehicles FOR UPDATE USING (true);

-- OR just disable RLS temporarily:
-- ALTER TABLE vehicles DISABLE ROW LEVEL SECURITY;
