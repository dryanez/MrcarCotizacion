-- Drop the policies if they already exist to avoid errors
DROP POLICY IF EXISTS "Allow public inserts" ON leads;
DROP POLICY IF EXISTS "Allow auth users to view" ON leads;

-- Enable RLS on the table (if not already enabled)
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (for the public form)
CREATE POLICY "Allow public inserts" 
ON leads 
FOR INSERT 
TO anon 
WITH CHECK (true);

-- Allow authenticated users (like admin) to view leads
CREATE POLICY "Allow auth users to view" 
ON leads 
FOR SELECT 
TO authenticated 
USING (true);

-- Ensure anon role has permission to insert
GRANT INSERT ON leads TO anon;
