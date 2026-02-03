"""Check WCA database schema."""
import asyncio
import aiomysql

async def check_schema():
    conn = await aiomysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='poke990',
        db='wca'
    )

    async with conn.cursor() as cursor:
        # Check structure of key tables
        tables = ['results', 'ranks_single', 'ranks_average', 'persons', 'competitions', 'events']

        for table in tables:
            print(f"\n{'='*80}")
            print(f"Table: {table}")
            print(f"{'='*80}")
            await cursor.execute(f"DESCRIBE {table}")
            columns = await cursor.fetchall()
            print(f"{'Column':<30} {'Type':<20} {'Null':<5} {'Key':<5}")
            print("-" * 80)
            for col in columns:
                print(f"{col[0]:<30} {col[1]:<20} {col[2]:<5} {col[3]:<5}")

            # Show sample data
            print(f"\nSample data (first 2 rows):")
            await cursor.execute(f"SELECT * FROM {table} LIMIT 2")
            rows = await cursor.fetchall()
            if rows:
                # Get column names
                await cursor.execute(f"DESCRIBE {table}")
                cols = await cursor.fetchall()
                col_names = [c[0] for c in cols]
                print(f"{' | '.join(col_names[:5])}")  # Show first 5 columns
                for row in rows:
                    print(f"{' | '.join(str(x) for x in row[:5])}")

    conn.close()

asyncio.run(check_schema())
