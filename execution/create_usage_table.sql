-- Create a table to track API usage per day
create table if not exists public.api_usage (
  date date primary key default current_date,
  count int default 0,
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Init today's counter if not exists (handled by app logic usually, but good for testing)
insert into public.api_usage (date, count)
values (current_date, 0)
on conflict (date) do nothing;

-- Enable RLS
alter table public.api_usage enable row level security;

-- Allow anonymous insert/update for now (since we use the anon key likely)
-- In production, restrict this to service_role or authenticated users
create policy "Allow generic access" on public.api_usage
  for all
  using (true)
  with check (true);
