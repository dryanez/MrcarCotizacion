-- Add address column for scheduling appointments
ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS address TEXT;
