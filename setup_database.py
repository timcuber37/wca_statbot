"""Database setup script for WCA Statistics Bot."""
import os
import sys
import asyncio
import aiomysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "wca")

SQL_FILE = "wca_export.sql"


async def create_database():
    """Create the WCA database if it doesn't exist."""
    print(f"[INFO] Connecting to MySQL server at {DB_HOST}:{DB_PORT}...")

    try:
        # Connect to MySQL server (without specifying database)
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
        )

        async with conn.cursor() as cursor:
            # Create database if it doesn't exist
            print(f"[INFO] Creating database '{DB_NAME}' if it doesn't exist...")
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print(f"[OK] Database '{DB_NAME}' is ready")

        conn.close()
        return True

    except Exception as e:
        print(f"[FAIL] Error creating database: {e}")
        return False


async def import_sql_file():
    """Import the WCA export SQL file into the database."""
    if not os.path.exists(SQL_FILE):
        print(f"[FAIL] SQL file '{SQL_FILE}' not found!")
        return False

    print(f"[INFO] Reading SQL file '{SQL_FILE}'...")
    file_size = os.path.getsize(SQL_FILE) / (1024 * 1024)  # Convert to MB
    print(f"[INFO] File size: {file_size:.2f} MB")

    try:
        # Connect to the WCA database
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
        )

        print("[INFO] Importing SQL file (this may take a few minutes)...")

        async with conn.cursor() as cursor:
            # Read the SQL file
            with open(SQL_FILE, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Split into individual statements (basic approach)
            # Note: This is a simple split and may not work for all SQL files
            statements = sql_content.split(';\n')

            total = len(statements)
            print(f"[INFO] Found {total} SQL statements to execute...")

            for i, statement in enumerate(statements, 1):
                statement = statement.strip()
                if statement:  # Skip empty statements
                    try:
                        await cursor.execute(statement)
                        if i % 100 == 0:
                            print(f"[INFO] Progress: {i}/{total} statements executed...")
                    except Exception as e:
                        # Continue on error (some statements may fail due to dependencies)
                        if "Duplicate entry" not in str(e):
                            print(f"[WARN] Error at statement {i}: {str(e)[:100]}")

            await conn.commit()
            print("[OK] SQL file imported successfully")

        conn.close()
        return True

    except Exception as e:
        print(f"[FAIL] Error importing SQL file: {e}")
        return False


async def test_database():
    """Test the database connection and query some data."""
    print("[INFO] Testing database connection...")

    try:
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
        )

        async with conn.cursor() as cursor:
            # List tables
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            print(f"[OK] Found {len(tables)} tables in database")

            # Check for key tables
            table_names = [table[0] for table in tables]
            required_tables = ['Persons', 'Results', 'Competitions', 'Events']

            for table in required_tables:
                if table in table_names:
                    await cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = await cursor.fetchone()
                    print(f"[OK] Table '{table}': {count[0]} rows")
                else:
                    print(f"[WARN] Required table '{table}' not found")

        conn.close()
        return True

    except Exception as e:
        print(f"[FAIL] Error testing database: {e}")
        return False


async def main():
    """Main setup function."""
    print("=" * 60)
    print("WCA Statistics Bot - Database Setup")
    print("=" * 60)
    print()

    # Check MySQL connection
    print(f"Configuration:")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  User: {DB_USER}")
    print(f"  Database: {DB_NAME}")
    print()

    # Step 1: Create database
    if not await create_database():
        print("\n[FAIL] Database creation failed. Please check your MySQL installation.")
        print("Make sure MySQL is running and credentials are correct in .env file.")
        return

    print()

    # Step 2: Import SQL file
    if not await import_sql_file():
        print("\n[FAIL] SQL import failed.")
        return

    print()

    # Step 3: Test database
    if not await test_database():
        print("\n[FAIL] Database test failed.")
        return

    print()
    print("=" * 60)
    print("[OK] Database setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Update your .env file with the DATABASE_URL:")
    print(f"   DATABASE_URL=mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("2. Run the bot with: python bot.py")


if __name__ == "__main__":
    asyncio.run(main())
