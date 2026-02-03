"""Configuration management for the WCA Discord bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")  # Optional: for testing in specific server

# Anthropic Configuration (for NL-to-SQL translation)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")  # or "claude-3-5-sonnet-20241022" or "claude-3-haiku-20240307" for cost savings

# WCA API Configuration
WCA_API_BASE_URL = os.getenv("WCA_API_BASE_URL", "https://www.worldcubeassociation.org/api/v0")
# Alternative: If using the unofficial REST API
WCA_REST_API_URL = os.getenv("WCA_REST_API_URL", "https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api")

# Database Configuration (if using local database)
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g., "mysql+aiomysql://user:pass@localhost/wca"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "wca")

# Bot Settings
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!wca")
MAX_QUERY_RESULTS = int(os.getenv("MAX_QUERY_RESULTS", "50"))

