"""Flask web application for WCA StatBot."""
import asyncio
import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

# aiomysql SSL requires SelectorEventLoop on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from config import MAX_QUERY_RESULTS, SUPABASE_URL, SUPABASE_ANON_KEY
from services.nl_to_sql import NLToSQLService
from services.wca_api import WCAService
from services.auth import get_user_from_token
from services import saved_queries

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MAX_QUESTION_LENGTH = 2000

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

nl_to_sql_service = NLToSQLService()
wca_service = WCAService()

# Persistent event loop for async services (avoids "Event loop is closed" errors)
_loop = asyncio.new_event_loop()


def run_async(coro):
    """Run an async coroutine on the persistent event loop."""
    return _loop.run_until_complete(coro)


def get_current_user():
    """Extract user from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        return get_user_from_token(token), token
    return None, None


@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response


# --- Pages ---

@app.route('/')
@limiter.exempt
def index():
    return render_template('index.html',
                           supabase_url=SUPABASE_URL,
                           supabase_anon_key=SUPABASE_ANON_KEY)


@app.route('/about')
@limiter.exempt
def about():
    return render_template('about.html',
                           supabase_url=SUPABASE_URL,
                           supabase_anon_key=SUPABASE_ANON_KEY)


@app.route('/login')
@limiter.exempt
def login():
    return render_template('login.html',
                           supabase_url=SUPABASE_URL,
                           supabase_anon_key=SUPABASE_ANON_KEY)


@app.route('/profile')
@limiter.exempt
def profile():
    return render_template('profile.html',
                           supabase_url=SUPABASE_URL,
                           supabase_anon_key=SUPABASE_ANON_KEY)


# --- API ---

@app.route('/query', methods=['POST'])
@limiter.limit("10 per minute")
def query():
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid request.'}), 400

    question = data.get('question', '')
    if not isinstance(question, str):
        return jsonify({'error': 'Invalid question format.'}), 400

    question = question.strip()

    if not question:
        return jsonify({'error': 'Please enter a question.'}), 400

    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({'error': f'Question too long (max {MAX_QUESTION_LENGTH} characters).'}), 400

    try:
        sql_query = run_async(nl_to_sql_service.translate_to_sql(question))

        if not sql_query:
            return jsonify({'error': 'Could not translate your question to a safe SQL query.'}), 400

        logger.info(f"Generated SQL: {sql_query}")

        results = run_async(wca_service.execute_query(sql_query))
        html_table = wca_service.format_results_html(results, max_results=MAX_QUERY_RESULTS)

        return jsonify({
            'html': html_table,
            'sql': sql_query,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        return jsonify({'error': 'Unable to process your query. Please try again.'}), 500


@app.route('/api/save-query', methods=['POST'])
@limiter.limit("20 per minute")
def save_query():
    user, token = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    question = data.get('question', '')
    sql_query = data.get('sql', '')
    results = data.get('results', [])

    if not question or not sql_query:
        return jsonify({'error': 'Missing question or SQL'}), 400

    saved = saved_queries.save_query(token, user.id, question, sql_query, results)
    if saved:
        return jsonify({'success': True, 'id': saved['id']})
    return jsonify({'error': 'Failed to save query'}), 500


@app.route('/api/saved-queries', methods=['GET'])
@limiter.limit("30 per minute")
def get_saved():
    user, token = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    queries = saved_queries.get_saved_queries(token, user.id)
    return jsonify({'queries': queries})


@app.route('/api/saved-query/<query_id>', methods=['DELETE'])
@limiter.limit("20 per minute")
def delete_query(query_id):
    user, token = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    success = saved_queries.delete_saved_query(token, user.id, query_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to delete query'}), 500


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true', port=5000)
