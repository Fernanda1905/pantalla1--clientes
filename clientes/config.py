from __future__ import annotations

import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def get_supabase() -> Client:
   
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
           
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)
