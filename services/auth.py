"""Authentication service using Supabase."""
import logging
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_ANON_KEY

logger = logging.getLogger(__name__)

_supabase = None


def get_supabase():
    """Get or create the Supabase client (anon, no user context)."""
    global _supabase
    if _supabase is None and SUPABASE_URL and SUPABASE_ANON_KEY:
        _supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase


def get_supabase_with_token(access_token):
    """Create a Supabase client authenticated as a specific user.

    This is needed for RLS policies that check auth.uid().
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.postgrest.auth(access_token)
    return client


def get_user_from_token(access_token):
    """Verify a Supabase access token and return the user."""
    client = get_supabase()
    if not client:
        return None
    try:
        response = client.auth.get_user(access_token)
        return response.user
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None
