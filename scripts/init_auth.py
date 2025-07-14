#!/usr/bin/env python3
"""
Initialize authentication tables in the database.
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)


async def init_auth_tables():
    """Initialize authentication-related tables."""
    # Parse connection parameters
    db_url = settings.database_url
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
    
    # Connect to database
    conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name
    )
    
    try:
        # Read and execute SQL migration
        migration_path = Path(__file__).parent.parent / "backend" / "migrations" / "add_users_table.sql"
        with open(migration_path, 'r') as f:
            sql = f.read()
        
        logger.info("Executing authentication migration...")
        await conn.execute(sql)
        
        # Create a default admin user for testing
        from backend.core.auth import get_password_hash
        import uuid
        
        admin_id = uuid.uuid4()
        admin_email = "admin@example.com"
        admin_username = "admin"
        admin_password = get_password_hash("admin123")
        
        # Check if admin already exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE username = $1",
            admin_username
        )
        
        if not existing:
            await conn.execute(
                """
                INSERT INTO users (id, email, username, hashed_password, is_active, is_superuser)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                admin_id, admin_email, admin_username, admin_password, True, True
            )
            logger.info(f"Created default admin user: {admin_username} (password: admin123)")
        else:
            logger.info("Admin user already exists")
        
        logger.info("Authentication tables initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize auth tables: {str(e)}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_auth_tables())