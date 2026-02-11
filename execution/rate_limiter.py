import os
import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class RateLimiter:
    def __init__(self, limit=1000):
        self.limit = limit
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("⚠️ SUPABASE_URL or SUPABASE_KEY missing. Rate limiting disabled.")
            self.supabase = None
        else:
            self.supabase: Client = create_client(self.url, self.key)

    def check_and_increment(self):
        """
        Check daily usage and increment if under limit.
        Raises specific exception if limit exceeded.
        """
        if not self.supabase:
            return True

        today = datetime.date.today().isoformat()
        
        try:
            # 1. Get current count for today
            response = self.supabase.table("api_usage").select("*").eq("date", today).execute()
            
            current_count = 0
            
            if not response.data:
                # Create row for today
                print(f"🆕 Starting new daily usage counter for {today}")
                self.supabase.table("api_usage").insert({"date": today, "count": 1}).execute()
                return True
            else:
                current_count = response.data[0]["count"]
            
            # 2. Check limit
            if current_count >= self.limit:
                print(f"🚫 Daily limit reached! ({current_count}/{self.limit})")
                raise Exception(f"Daily API limit of {self.limit} reached. Try again tomorrow.")
            
            # 3. Increment
            # Note: This is not atomic without a stored procedure, but fine for soft limits
            new_count = current_count + 1
            self.supabase.table("api_usage").update({"count": new_count}).eq("date", today).execute()
            print(f"📊 Daily usage: {new_count}/{self.limit}")
            
            return True
            
        except Exception as e:
            if "Daily API limit" in str(e):
                raise e
            print(f"⚠️ Rate limiter error (failing open): {e}")
            # Fail open: allow request if DB error, to not block app due to infra issues
            return True
