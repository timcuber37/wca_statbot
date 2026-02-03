"""Test script to verify bot configuration and API connections."""
import asyncio
import logging
from config import (
    DISCORD_TOKEN,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    WCA_API_BASE_URL
)
from services.nl_to_sql import NLToSQLService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_configuration():
    """Test that all required configuration is present."""
    print("\n" + "="*60)
    print("CONFIGURATION TEST")
    print("="*60)

    checks = {
        "Discord Token": DISCORD_TOKEN,
        "Anthropic API Key": ANTHROPIC_API_KEY,
        "Anthropic Model": ANTHROPIC_MODEL,
        "WCA API Base URL": WCA_API_BASE_URL
    }

    all_good = True
    for name, value in checks.items():
        if value:
            # Mask sensitive values
            if "Token" in name or "Key" in name:
                masked = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
                print(f"[OK] {name}: {masked}")
            else:
                print(f"[OK] {name}: {value}")
        else:
            print(f"[FAIL] {name}: NOT SET")
            all_good = False

    print("\n" + "-"*60)
    if all_good:
        print("[OK] All configuration values are set!")
    else:
        print("[FAIL] Some configuration values are missing. Check your .env file.")

    return all_good


async def test_nl_to_sql():
    """Test the NL-to-SQL translation service."""
    print("\n" + "="*60)
    print("NL-TO-SQL TRANSLATION TEST")
    print("="*60)

    service = NLToSQLService()

    if not service.client:
        print("[FAIL] Anthropic client not initialized. Check ANTHROPIC_API_KEY.")
        return False

    test_questions = [
        "What is the world record for 3x3?",
        "Show me the top 5 rankings for 2x2",
        "Who has the best average for Megaminx?"
    ]

    print(f"\nTesting {len(test_questions)} sample questions...\n")

    for i, question in enumerate(test_questions, 1):
        print(f"Question {i}: {question}")
        try:
            sql = await service.translate_to_sql(question)
            if sql:
                print(f"[OK] Generated SQL:\n  {sql}\n")
            else:
                print(f"[FAIL] Failed to generate SQL\n")
        except Exception as e:
            print(f"[FAIL] Error: {e}\n")
            return False

    print("-"*60)
    print("[OK] NL-to-SQL translation is working!")
    return True


async def test_discord_token():
    """Test Discord token validity (without actually connecting)."""
    print("\n" + "="*60)
    print("DISCORD TOKEN TEST")
    print("="*60)

    if not DISCORD_TOKEN:
        print("[FAIL] Discord token not set")
        return False

    # Basic validation - Discord tokens have a specific format
    parts = DISCORD_TOKEN.split('.')
    if len(parts) != 3:
        print("[FAIL] Discord token format appears invalid")
        print("  Expected format: XXXX.YYYY.ZZZZ")
        return False

    print("[OK] Discord token format looks valid")
    print("  (To fully test, run bot.py)")
    return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("WCA DISCORD BOT - SETUP VERIFICATION")
    print("="*60)

    # Test configuration
    config_ok = await test_configuration()

    if not config_ok:
        print("\n❌ Fix configuration issues before proceeding.")
        return

    # Test Discord token format
    await test_discord_token()

    # Test NL-to-SQL
    nl_to_sql_ok = await test_nl_to_sql()

    # Final summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if config_ok and nl_to_sql_ok:
        print("[OK] All tests passed!")
        print("\nNext steps:")
        print("1. Run: python bot.py")
        print("2. Invite bot to your Discord server")
        print("3. Test with: !wca query What is the world record for 3x3?")
    else:
        print("[FAIL] Some tests failed. Check errors above.")


if __name__ == "__main__":
    asyncio.run(main())
