"""Saved queries service using Supabase."""
import json
import logging
from typing import List, Dict, Any, Optional
from services.auth import get_supabase_with_token

logger = logging.getLogger(__name__)


def save_query(access_token: str, user_id: str, question: str, sql_query: str,
               results: List[Dict[str, Any]]) -> Optional[Dict]:
    """Save a query with a snapshot of the first 5 results."""
    client = get_supabase_with_token(access_token)
    if not client:
        return None

    preview = results[:5] if results else []
    # Convert any non-serializable values to strings
    clean_preview = []
    for row in preview:
        clean_row = {}
        for k, v in row.items():
            try:
                json.dumps(v)
                clean_row[k] = v
            except (TypeError, ValueError):
                clean_row[k] = str(v)
        clean_preview.append(clean_row)

    try:
        response = client.table('saved_queries').insert({
            'user_id': user_id,
            'question': question,
            'sql_query': sql_query,
            'result_count': len(results),
            'result_preview': clean_preview
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Failed to save query: {e}")
        return None


def get_saved_queries(access_token: str, user_id: str) -> List[Dict]:
    """Get all saved queries for a user, newest first."""
    client = get_supabase_with_token(access_token)
    if not client:
        return []

    try:
        response = (client.table('saved_queries')
                    .select('*')
                    .eq('user_id', user_id)
                    .order('created_at', desc=True)
                    .execute())
        return response.data or []
    except Exception as e:
        logger.error(f"Failed to get saved queries: {e}")
        return []


def delete_saved_query(access_token: str, user_id: str, query_id: str) -> bool:
    """Delete a saved query (only if it belongs to the user)."""
    client = get_supabase_with_token(access_token)
    if not client:
        return False

    try:
        client.table('saved_queries').delete().eq(
            'id', query_id).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to delete saved query: {e}")
        return False
