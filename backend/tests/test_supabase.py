import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def verify_conn(db_url: str):
    # Ensure it uses postgresql+asyncpg
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    print(f"Attempting to connect to: {db_url.split('@')[-1]} (password masked)")
    
    try:
        engine = create_async_engine(db_url, echo=True)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1;"))
            val = result.scalar()
            print(f"Success! Connection verified. SELECT 1 returned: {val}")
        await engine.dispose()
    except Exception as e:
        print(f"Connection failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_supabase.py <DATABASE_URL>")
        sys.exit(1)
    url = sys.argv[1]
    asyncio.run(verify_conn(url))
