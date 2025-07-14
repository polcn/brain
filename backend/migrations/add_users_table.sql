-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create index on username for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Add user_id foreign key to documents table
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Add user_id index to documents
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);

-- Update audit_log user_id to UUID type to match users table
-- First drop the existing constraint if any
ALTER TABLE audit_log 
DROP CONSTRAINT IF EXISTS fk_audit_log_user;

-- Change column type, converting empty strings to NULL
ALTER TABLE audit_log 
ALTER COLUMN user_id TYPE UUID 
USING CASE 
    WHEN user_id IS NULL OR user_id = '' THEN NULL
    ELSE user_id::UUID 
END;

-- Add foreign key constraint
ALTER TABLE audit_log
ADD CONSTRAINT fk_audit_log_user 
FOREIGN KEY (user_id) REFERENCES users(id);