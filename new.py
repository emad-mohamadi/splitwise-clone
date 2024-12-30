import os
import json
from supabase import create_client, Client
import pandas as pd

# Set up Supabase client
url = "https://qrdbmqosjdulvsmdvwia.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFyZGJtcW9zamR1bHZzbWR2d2lhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU1NzA2MTUsImV4cCI6MjA1MTE0NjYxNX0.9JMjUwv75YA3NJTnd-j88CPJ540nCuTCh_LB-Cccmrc"
supabase = create_client(url, key)

# Load JSON data
# with open('sample.json') as f:
#     data = json.load(f)

# # Insert JSON data into Supabase table
# response = supabase.table("users").insert(data).execute()
# print(response)


response = supabase.table("users").select("*").execute()
# Convert the data to a pandas DataFrame
data = response.data
df = pd.DataFrame(data)  # Display the DataFrame print(df)

print(data)
