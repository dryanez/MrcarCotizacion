-- Add columns for scheduling appointments
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS appointment_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS lead_type TEXT DEFAULT 'valuation';

-- Create an index on appointment_date for faster lookups (optional but good)
CREATE INDEX IF NOT EXISTS idx_leads_appointment_date ON leads(appointment_date);
