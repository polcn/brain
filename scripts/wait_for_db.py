#!/usr/bin/env python3
"""
Wait for PostgreSQL database to be ready before starting the application.
"""

import asyncio
import asyncpg
import os
import sys
import time
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://brain_user:brain_password@localhost:5433/brain")
MAX_RETRIES = 30
RETRY_INTERVAL = 2


async def check_database_connection(database_url: str) -> bool:
    """Check if we can connect to the database."""
    try:
        conn = await asyncpg.connect(database_url)
        await conn.execute("SELECT 1")
        await conn.close()
        return True
    except Exception as e:
        print(f"Database not ready: {e}", file=sys.stderr)
        return False


async def wait_for_database(database_url: str, max_retries: int = MAX_RETRIES) -> bool:
    """Wait for database to be ready."""
    print(f"Waiting for database at {database_url}")
    
    for attempt in range(max_retries):
        if await check_database_connection(database_url):
            print("Database is ready!")
            return True
        
        print(f"Attempt {attempt + 1}/{max_retries} failed, retrying in {RETRY_INTERVAL} seconds...")
        await asyncio.sleep(RETRY_INTERVAL)
    
    return False


async def main():
    """Main function."""
    if not await wait_for_database(DATABASE_URL):
        print("Failed to connect to database after maximum retries", file=sys.stderr)
        sys.exit(1)
    
    print("Database connection successful")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())