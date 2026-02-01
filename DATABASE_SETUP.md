# WCA Database Setup Guide

This guide will help you set up the local MySQL database for the WCA Statistics Bot.

## Prerequisites

1. **MySQL Server** must be installed on your system
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use XAMPP/WAMP/MAMP which includes MySQL

2. **Python packages** (already installed via requirements.txt):
   - aiomysql
   - PyMySQL

## Setup Steps

### 1. Install and Start MySQL

Make sure MySQL is installed and running on your system.

**Windows (if using MySQL directly):**
- Start MySQL from Services or via command: `net start MySQL`

**Windows (if using XAMPP/WAMP):**
- Start the MySQL service from the control panel

**To verify MySQL is running:**
```bash
mysql --version
```

### 2. Configure Database Credentials

Edit your `.env` file and update the database settings:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=wca
DATABASE_URL=mysql+aiomysql://root:your_mysql_password_here@localhost:3306/wca
```

**Important:** Replace `your_mysql_password_here` with your actual MySQL root password.

### 3. Run the Database Setup Script

The setup script will:
1. Create the `wca` database
2. Import the `wca_export.sql` file
3. Test the database connection

Run the script:
```bash
python setup_database.py
```

**Note:** The import process may take several minutes depending on the size of the SQL file.

### 4. Verify the Setup

After the script completes successfully, you should see:
- Database created
- Tables imported
- Row counts for key tables (Persons, Results, Competitions, Events)

## Troubleshooting

### Error: "Can't connect to MySQL server"
- Make sure MySQL is running
- Check that the host and port are correct in your .env file
- Verify your MySQL credentials

### Error: "Access denied"
- Double-check your MySQL username and password in the .env file
- Make sure the MySQL user has permissions to create databases

### Error: "SQL file not found"
- Make sure `wca_export.sql` is in the same directory as `setup_database.py`
- Check the file path in the script

### Large SQL File Import Issues
If the SQL file is very large (>100MB), you may want to import it manually:

```bash
# Create the database first
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS wca"

# Import the SQL file
mysql -u root -p wca < wca_export.sql
```

## Database Schema

The WCA database includes tables such as:
- **Persons**: Information about all WCA competitors
- **Results**: All competition results
- **Competitions**: Competition details
- **Events**: Puzzle events (3x3, 2x2, etc.)
- **RanksSingle**: World rankings for single solves
- **RanksAverage**: World rankings for averages
- And more...

## Testing the Bot

Once the database is set up, you can test the bot:

1. Start the bot: `python bot.py`
2. In Discord, try a query: `!wca query What is the world record for 3x3?`
3. The bot should now return real data from the WCA database!

## Updating the Database

The WCA releases new database exports regularly. To update:

1. Download the latest export from: https://www.worldcubeassociation.org/export/results
2. Replace `wca_export.sql` with the new file
3. Run the setup script again (it will drop and recreate the database)

## Performance Tips

- The database has indexes on commonly queried columns
- For large queries, consider adding LIMIT clauses
- The bot uses connection pooling for efficient database access
