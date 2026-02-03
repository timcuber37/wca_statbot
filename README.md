# WCA Statistics Bot

A Discord bot that translates natural language questions into SQL queries to fetch World Cube Association (WCA) statistics from a local MySQL database.

## Features

- 🤖 Natural language to SQL translation using Anthropic's Claude AI (Haiku model)
- 📊 Query WCA statistics using plain English
- 🗄️ Local MySQL database with 6.2M+ competition results
- 🔍 Support for world records, rankings, competition results, and more
- 💬 Easy-to-use Discord commands
- ⚡ Fast queries with connection pooling
- 📐 Dynamic column formatting for readable results

## Database Statistics

The bot connects to a local MySQL database containing:
- **279,869** competitors (persons)
- **6,266,346** competition results
- **16,817** competitions
- **21** puzzle events
- **979,165** single solve rankings
- **848,675** average rankings
- **28,935,325** individual solve attempts

## Prerequisites

- Python 3.8 or higher
- MySQL Server (or XAMPP/WAMP/MAMP)
- Discord Bot Token ([Create a bot](https://discord.com/developers/applications))
- Anthropic API Key ([Get one here](https://console.anthropic.com/))
- WCA Database Export ([Download here](https://www.worldcubeassociation.org/export/results))

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd wca_statbot
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root with the following:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# Anthropic (Claude) Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# WCA API Configuration
WCA_API_BASE_URL=https://www.worldcubeassociation.org/api/v0

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=wca
DATABASE_URL=mysql+aiomysql://root:your_mysql_password_here@localhost:3306/wca

# Bot Settings
COMMAND_PREFIX=!wca
MAX_QUERY_RESULTS=50
```

### 5. Set up the MySQL database

#### Install MySQL
- **Windows**: Download from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/) or use XAMPP/WAMP
- **macOS**: `brew install mysql`
- **Linux**: `sudo apt-get install mysql-server`

#### Download WCA Data
1. Download the latest WCA database export from [WCA Results Export](https://www.worldcubeassociation.org/export/results)
2. Extract the `wca_export.sql` file
3. Place it in the `wca_statbot` directory

#### Import the database
```bash
python setup_database.py
```

This script will:
- Create the `wca` database
- Import all WCA data (may take several minutes)
- Verify the setup and show table counts

For detailed database setup instructions, see [DATABASE_SETUP.md](DATABASE_SETUP.md)

### 6. Enable Discord Bot Permissions

In the Discord Developer Portal:
1. Go to your bot application
2. Navigate to "Bot" settings
3. Enable **MESSAGE CONTENT INTENT** under "Privileged Gateway Intents"
4. Invite the bot to your server with proper permissions (Send Messages, Read Messages, etc.)

### 7. Run the bot
```bash
python bot.py
```

You should see:
```
WCA Statbot#8882 has connected to Discord!
Bot is in 1 guild(s)
```

## Usage

### Commands

Once the bot is running, use these commands in Discord:

#### Query Command
```
!wca query <your question>
```
or the shorter version:
```
!wcaquery <your question>
```

**Examples:**
- `!wca query What is the world record for 3x3?`
- `!wca query Who are the top 10 fastest 3x3 average times?`
- `!wca query Who is the world record holder for 4x4?`
- `!wca query Show me the top 10 American rankings for 3x3 average`
- `!wca query Who are the top 10 rankings for clock?`
- `!wca query Who has the most competition results?`

#### Other Commands
- `!wca help` - Show help information
- `!wca ping` - Check if the bot is responsive

### Supported Event IDs

The bot recognizes these WCA event identifiers:
- `333` - 3x3x3 Cube
- `222` - 2x2x2 Cube
- `444` - 4x4x4 Cube
- `555` - 5x5x5 Cube
- `666` - 6x6x6 Cube
- `777` - 7x7x7 Cube
- `333bf` - 3x3x3 Blindfolded
- `333fm` - 3x3x3 Fewest Moves
- `333oh` - 3x3x3 One-Handed
- `clock` - Clock
- `minx` - Megaminx
- `pyram` - Pyraminx
- `skewb` - Skewb
- `sq1` - Square-1
- `444bf` - 4x4x4 Blindfolded
- `555bf` - 5x5x5 Blindfolded
- `333mbf` - 3x3x3 Multi-Blind

## Architecture

### Project Structure
```
wca_statbot/
├── bot.py                  # Main Discord bot with command handlers
├── config.py              # Configuration management
├── setup_database.py      # Database setup and import script
├── services/
│   ├── nl_to_sql.py      # Natural language to SQL translator (Claude AI)
│   └── wca_api.py        # Database query executor and result formatter
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (not in git)
├── DATABASE_SETUP.md     # Detailed database setup guide
└── README.md             # This file
```

### How It Works

1. **User sends a question** in Discord (e.g., "Who is the world record holder for 3x3?")
2. **Discord bot receives** the message via `bot.py`
3. **NL-to-SQL service** (`nl_to_sql.py`) sends the question to Claude AI with WCA database schema
4. **Claude generates SQL** query based on the question and schema
5. **WCA API service** (`wca_api.py`) executes the SQL against the MySQL database
6. **Results are formatted** with dynamic column alignment
7. **Bot sends response** back to Discord with the formatted results

### Database Schema

The bot uses the official WCA database schema with these main tables:

- **ranks_single**: World rankings for single solves
- **ranks_average**: World rankings for averages
- **results**: All competition results
- **persons**: Competitor information
- **competitions**: Competition details
- **events**: Puzzle event information
- **countries**: Country information

Times are stored in centiseconds (1/100th of a second). For example:
- 1000 = 10.00 seconds
- 6000 = 1:00.00 (1 minute)

## Configuration

Key settings in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `ANTHROPIC_MODEL` | Claude model to use | claude-3-haiku-20240307 |
| `DB_HOST` | MySQL host | localhost |
| `DB_PORT` | MySQL port | 3306 |
| `DB_USER` | MySQL username | root |
| `DB_PASSWORD` | MySQL password | Required |
| `DB_NAME` | Database name | wca |
| `COMMAND_PREFIX` | Bot command prefix | !wca |
| `MAX_QUERY_RESULTS` | Max results to display | 50 |

## Troubleshooting

### Bot not responding to commands
- Verify MESSAGE CONTENT INTENT is enabled in Discord Developer Portal
- Check that the command prefix is correct (`!wca` or `!wcaquery`)
- Review bot logs for errors

### Database connection errors
- Ensure MySQL is running
- Verify database credentials in `.env` file
- Check that the `wca` database exists

### SQL query errors
- The bot generates SQL based on natural language - try rephrasing your question
- Check logs to see the generated SQL query
- Some complex queries may not be supported

### API rate limits
- Claude API has rate limits - space out requests if needed
- Consider upgrading to a higher Anthropic API tier for more requests

## Updating WCA Data

The WCA releases new database exports regularly (usually monthly). To update:

1. Download the latest export from [WCA Results Export](https://www.worldcubeassociation.org/export/results)
2. Replace `wca_export.sql` with the new file
3. Run the setup script again:
   ```bash
   python setup_database.py
   ```

## Performance

- **Database**: Uses connection pooling (1-10 connections) for efficient queries
- **Response Time**: Most queries complete in 1-3 seconds
- **Caching**: Results are not cached - all queries are real-time
- **Formatting**: Dynamic column width calculation for readable output

## Future Improvements

- [ ] Add query result caching for frequently asked questions
- [ ] Support for more complex multi-table joins
- [ ] Add visualization/charts for rankings and trends
- [ ] Support for historical data queries (e.g., "WR progression")
- [ ] Add pagination for very large result sets
- [ ] Implement rate limiting per user
- [ ] Add query history and favorites
- [ ] Support for competition-specific queries

## Development

### Running Tests
```bash
# Test configuration
python test_setup.py

# Test integration
python test_integration.py

# Check database schema
python check_schema.py

# Check table row counts
python check_tables.py
```

### Adding New Features
1. Update the schema context in `services/nl_to_sql.py` if adding new tables
2. Modify `services/wca_api.py` for custom result formatting
3. Add new commands in `bot.py` following the existing pattern

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Credits

- **WCA**: World Cube Association for providing the database export
- **Discord.py**: Discord API wrapper
- **Anthropic**: Claude AI for natural language processing
- **aiomysql**: Async MySQL connector

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the console output
3. Open an issue on GitHub
4. Contact the maintainers

---

Built with ❤️ for the speedcubing community
