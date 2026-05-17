# WCA StatBot

An AI-powered tool that lets you query World Cube Association competition data using plain English. Available as both a web app and a Discord bot.

**Live site:** [wca-statbot.fly.dev](https://wca-statbot.fly.dev)

## Features

- Natural language to SQL translation using Anthropic's Claude AI
- Query WCA statistics using plain English — no SQL required
- Web interface with instant results displayed in formatted tables
- Discord bot with the same query capabilities
- Google sign-in via Supabase Auth
- Save and revisit past queries from your profile
- Guest access with 5 free queries before sign-in required

## Database

The app queries a database populated from the official [WCA data export](https://www.worldcubeassociation.org/export/results) (March 14, 2026), containing:

| Stat | Count |
|------|-------|
| Competitors | 281,645 |
| Results | 6,346,883 |
| Competitions | 17,150 |
| Events | 21 |

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Anthropic Claude (natural language to SQL)
- **WCA Database:** TiDB Serverless (MySQL-compatible)
- **Auth & Saved Queries:** Supabase (PostgreSQL + Auth)
- **Discord:** discord.py
- **Deployment:** Fly.io, Docker, Gunicorn

## How It Works

1. User asks a question in plain English (web or Discord)
2. Claude AI translates the question into a SQL query against the WCA database schema
3. The query executes against TiDB Serverless and results are returned in a formatted table

## Web App

The web interface provides:
- A search bar to ask any question about WCA data
- Formatted result tables with the generated SQL visible
- Google sign-in for unlimited queries and saved query history
- A profile page with account info and saved queries

## Discord Bot

### Commands

| Command | Description |
|---------|-------------|
| `!wca query <question>` | Ask a question about WCA data |
| `!wca q <question>` | Short alias for query |
| `!wca ask <question>` | Another alias for query |
| `!wca help` | Show available commands |
| `!wca ping` | Check bot latency |

### Add to Your Server

1. Use the [invite link](https://discord.com/oauth2/authorize?client_id=1450571905043267594&permissions=2048&scope=bot) to add the bot
2. Select your server (requires **Manage Server** permissions)
3. Authorize the requested permissions
4. Type `!wca query` followed by your question in any text channel

## Example Questions

- What is the world record for 3x3?
- Who are the top 10 fastest 2x2 solvers?
- How many competitions have been held in the United States in 2025?
- Who has the most world record single results?
- Who placed first in 3x3 finals at the 2023 World Championship?

## Project Structure

```
wca_statbot/
├── app.py                  # Flask web application
├── bot.py                  # Discord bot
├── config.py               # Configuration management
├── services/
│   ├── nl_to_sql.py        # Natural language to SQL translation (Claude AI)
│   ├── wca_api.py          # WCA database query execution and formatting
│   ├── auth.py             # Supabase authentication helpers
│   └── saved_queries.py    # Saved query CRUD operations
├── templates/
│   ├── index.html          # Main query page
│   ├── about.html          # About page
│   ├── login.html          # Login page (Google / WCA auth)
│   └── profile.html        # Profile page with saved queries
├── static/
│   └── style.css           # Styles
├── Dockerfile              # Docker container for deployment
├── fly.toml                # Fly.io configuration
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not in git)
```

## Local Development

### Prerequisites

- Python 3.10+
- [Anthropic API key](https://console.anthropic.com/)
- TiDB Serverless database (or local MySQL) with WCA data imported
- Supabase project (for auth and saved queries)
- Discord bot token (if running the bot)

### Setup

```bash
git clone https://github.com/timcuber37/wca_statbot.git
cd wca_statbot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file:

```env
# Anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# WCA Database (TiDB Serverless)
DB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com
DB_PORT=4000
DB_USER=your_tidb_user
DB_PASSWORD=your_tidb_password
DB_NAME=wca
DB_SSL=true

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key

# Discord (optional, for bot only)
DISCORD_TOKEN=your_discord_token
DISCORD_GUILD_ID=your_guild_id

# App Settings
MAX_QUERY_RESULTS=50
COMMAND_PREFIX=!wca
```

### Run the web app

```bash
python app.py
```

### Run the Discord bot

```bash
python bot.py
```

## Deployment

The app is deployed on [Fly.io](https://fly.io) using Docker.

```bash
# Deploy
fly deploy

# Set secrets
fly secrets set ANTHROPIC_API_KEY=... DB_HOST=... DB_PORT=... DB_USER=... DB_PASSWORD=... DB_NAME=... DB_SSL=true SUPABASE_URL=... SUPABASE_ANON_KEY=...
```

## Security

- SQL validation rejects non-SELECT queries and blocks dangerous keywords
- Rate limiting on all API endpoints (flask-limiter)
- HTML escaping on all query result output
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy)
- Input validation and length limits
- Row Level Security on Supabase saved queries table

## License

MIT License — see [LICENSE](LICENSE) for details.

---

Built for the speedcubing community.
