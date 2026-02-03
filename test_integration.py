"""Integration test to verify NL-to-SQL and query execution pipeline."""
import asyncio
import logging
from services.nl_to_sql import NLToSQLService
from services.wca_api import WCAService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_pipeline():
    """Test the complete NL -> SQL -> Results pipeline."""
    print("\n" + "="*70)
    print("WCA BOT INTEGRATION TEST")
    print("="*70)

    # Initialize services
    nl_service = NLToSQLService()
    wca_service = WCAService()

    # Test questions
    test_questions = [
        "What is the world record for 3x3?",
        "Show me the top 5 rankings for 2x2",
        "Who has the best average for Megaminx?",
        "What are the top 3 rankings for 3x3 cube?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'-'*70}")
        print(f"Test {i}/{len(test_questions)}")
        print(f"{'-'*70}")
        print(f"Question: {question}")

        try:
            # Step 1: Convert to SQL
            sql_query = await nl_service.translate_to_sql(question)
            print(f"\nGenerated SQL:\n  {sql_query}")

            if not sql_query:
                print("[FAIL] Failed to generate SQL query")
                continue

            # Step 2: Execute query
            results = await wca_service.execute_query(sql_query)
            print(f"\nResults count: {len(results)}")

            # Step 3: Format results
            formatted = wca_service.format_results(results, max_results=10)
            print(f"\nFormatted output:\n{formatted}")

            print(f"\n[OK] Test {i} completed successfully")

        except Exception as e:
            print(f"\n[FAIL] Test {i} failed with error: {e}")
            logger.error(f"Error in test {i}", exc_info=e)

    # Cleanup
    await wca_service.close()

    print(f"\n{'='*70}")
    print("INTEGRATION TEST COMPLETE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(test_pipeline())
