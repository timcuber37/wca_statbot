"""Authentication service using Supabase."""
import logging
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY

logger = logging.getLogger(__name__)

_supabase = None
_supabase_admin = None


def get_supabase():
    """Get or create the Supabase client (anon, no user context)."""
    global _supabase
    if _supabase is None and SUPABASE_URL and SUPABASE_ANON_KEY:
        _supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase


def get_supabase_admin():
    """Get or create the Supabase admin client using the service role key."""
    global _supabase_admin
    if _supabase_admin is None and SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        _supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_admin


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


def find_or_create_wca_user(email, full_name, wca_id, avatar_url=None):
    """Find or create a Supabase user account for a WCA-authenticated user."""
    admin = get_supabase_admin()
    if not admin:
        logger.error("Supabase admin client unavailable — SUPABASE_SERVICE_ROLE_KEY not set")
        return None

    metadata = {
        'full_name': full_name,
        'wca_id': str(wca_id),
        'avatar_url': avatar_url or '',
        'provider': 'wca',
    }

    # Try to create the user first; if the email already exists we'll find them below.
    try:
        result = admin.auth.admin.create_user({
            'email': email,
            'email_confirm': True,
            'user_metadata': metadata,
        })
        logger.info(f"Created new Supabase user for WCA ID {wca_id}")
        return result.user
    except Exception as create_err:
        logger.info(f"User creation returned: {create_err} — searching for existing user")

    # Walk through paginated user list to find by email.
    try:
        page = 1
        while True:
            users = admin.auth.admin.list_users(page=page, per_page=50)
            if not users:
                break
            for user in users:
                if getattr(user, 'email', None) == email:
                    return user
            if len(users) < 50:
                break
            page += 1
    except Exception as e:
        logger.error(f"Error searching for existing WCA user: {e}")

    return None


def generate_wca_login_link(email, redirect_to):
    """Generate a Supabase magic-link that signs the user in and redirects to the app."""
    admin = get_supabase_admin()
    if not admin:
        return None
    try:
        result = admin.auth.admin.generate_link({
            'type': 'magiclink',
            'email': email,
            'redirect_to': redirect_to,
        })
        return result.properties.action_link
    except Exception as e:
        logger.error(f"Error generating WCA login link: {e}")
        return None
