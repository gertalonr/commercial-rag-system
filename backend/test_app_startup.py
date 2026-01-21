import asyncio
import sys
import os

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, startup_event

async def test_startup():
    print("Testing App Startup...")
    try:
        await startup_event()
        print("✅ Startup Event Successful (DB Init & Admin Check)")
    except Exception as e:
        print(f"❌ Startup Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_startup())
