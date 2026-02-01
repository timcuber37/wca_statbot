"""Quick script to check database tables."""
import asyncio
import aiomysql

async def check_tables():
    conn = await aiomysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='poke990',
        db='wca'
    )

    async with conn.cursor() as cursor:
        await cursor.execute("SHOW TABLES")
        tables = await cursor.fetchall()
        print("Tables in WCA database:")
        for table in tables:
            print(f"  - {table[0]}")

        print(f"\nTotal: {len(tables)} tables")

        # Check row counts for key tables
        print("\nRow counts:")
        for table in tables:
            table_name = table[0]
            await cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            count = await cursor.fetchone()
            print(f"  {table_name}: {count[0]:,} rows")

    conn.close()

asyncio.run(check_tables())
