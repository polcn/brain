#!/usr/bin/env python3
"""
Database setup script for Brain application.
Creates database, installs pgvector extension, and runs initial migrations.
"""

import asyncio
import os
import sys
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

async def create_database():
    """Create database and enable pgvector extension."""
    
    # Parse database URL
    db_url = os.getenv("DATABASE_URL", "postgresql://brain_user:brain_password@localhost:5433/brain")
    
    # Extract components
    if db_url.startswith("postgresql://"):
        db_url = db_url[13:]  # Remove postgresql://
    
    user_pass, host_db = db_url.split("@")
    user, password = user_pass.split(":")
    host_port, db_name = host_db.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 5432
    
    print(f"Connecting to PostgreSQL at {host}:{port}")
    
    # First connect to postgres database to create our database
    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)",
            db_name
        )
        
        if not exists:
            print(f"Creating database: {db_name}")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
        else:
            print(f"Database {db_name} already exists")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    
    # Now connect to our database and setup pgvector
    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        
        # Check if pgvector extension is available
        available = await conn.fetchval(
            "SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'vector'"
        )
        
        if available == 0:
            print("ERROR: pgvector extension not available!")
            print("Please install pgvector for PostgreSQL")
            return False
        
        # Enable pgvector
        print("Enabling pgvector extension...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Verify installation
        version = await conn.fetchval("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        print(f"pgvector version {version} installed successfully")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"Error setting up pgvector: {e}")
        return False


async def main():
    """Main setup function."""
    print("Setting up Brain database...")
    
    success = await create_database()
    
    if success:
        print("\nDatabase setup complete!")
        print("Next steps:")
        print("1. Run 'alembic upgrade head' to create tables")
        print("2. Start the application with 'uvicorn backend.app:app --port 8001'")
    else:
        print("\nDatabase setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())