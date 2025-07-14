# Brain API Documentation

This document provides detailed information about the Brain Document AI API endpoints.

## Base URL

```
http://localhost:8001/api/v1
```

## Authentication

All API endpoints (except authentication endpoints themselves) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "newuser",
  "password": "securepassword123",
  "is_active": true,
  "is_superuser": false
}

Response 200:
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "newuser",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-07-14T16:00:00Z",
    "updated_at": "2025-07-14T16:00:00Z"
  },
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=newuser&password=securepassword123

Response 200:
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

#### Login (JSON)
```http
POST /auth/login-json
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword123"
}

Response 200:
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### User Management Endpoints

#### Get Current User
```http
GET /users/me
Authorization: Bearer <token>

Response 200:
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "newuser",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-07-14T16:00:00Z",
  "updated_at": "2025-07-14T16:00:00Z"
}
```

#### Update Current User
```http
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "username": "newusername",
  "password": "newpassword123"
}

Response 200: Updated user object
```

#### List All Users (Admin Only)
```http
GET /users/
Authorization: Bearer <admin-token>

Response 200:
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "username": "user1",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-07-14T16:00:00Z",
    "updated_at": "2025-07-14T16:00:00Z"
  }
]
```

#### Get User by ID (Admin Only)
```http
GET /users/{user_id}
Authorization: Bearer <admin-token>

Response 200: User object
```

#### Update User (Admin Only)
```http
PUT /users/{user_id}
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "email": "updated@example.com",
  "is_active": false,
  "is_superuser": true
}

Response 200: Updated user object
```

#### Delete User (Admin Only)
```http
DELETE /users/{user_id}
Authorization: Bearer <admin-token>

Response 204: No Content
```

## Document Endpoints

All document endpoints require authentication and return only documents owned by the authenticated user.

### Upload Document
```http
POST /documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file-data>

Response 200:
{
  "id": "uuid",
  "filename": "document.pdf",
  "original_name": "document.pdf",
  "file_size": 1024000,
  "content_type": "application/pdf",
  "status": "processing",
  "error_message": null,
  "created_at": "2025-07-14T16:00:00Z",
  "updated_at": "2025-07-14T16:00:00Z"
}
```

### List Documents
```http
GET /documents/
Authorization: Bearer <token>
Query Parameters:
  - skip: int (default: 0)
  - limit: int (default: 10, max: 100)
  - status: string (optional: pending|processing|completed|failed)

Response 200:
{
  "documents": [
    {
      "id": "uuid",
      "filename": "document.pdf",
      "original_name": "document.pdf",
      "file_size": 1024000,
      "content_type": "application/pdf",
      "status": "completed",
      "error_message": null,
      "created_at": "2025-07-14T16:00:00Z",
      "updated_at": "2025-07-14T16:00:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 10
}
```

### Get Document
```http
GET /documents/{document_id}
Authorization: Bearer <token>

Response 200: Document object
Response 404: Document not found or not owned by user
```

### Download Document
```http
GET /documents/{document_id}/download
Authorization: Bearer <token>

Response 200: File stream
Response 404: Document not found or not owned by user
```

### Delete Document
```http
DELETE /documents/{document_id}
Authorization: Bearer <token>

Response 200:
{
  "message": "Document deleted successfully"
}
Response 404: Document not found or not owned by user
```

## Chat/Q&A Endpoints

### Chat Query
```http
POST /chat/
Authorization: Bearer <token> (optional)
Content-Type: application/json

{
  "query": "What is the main topic of the documents?",
  "max_results": 5,
  "document_ids": ["uuid1", "uuid2"],  // optional
  "similarity_threshold": 0.7,  // optional
  "chat_history": [  // optional
    {
      "role": "user",
      "content": "Previous question"
    },
    {
      "role": "assistant",
      "content": "Previous answer"
    }
  ]
}

Response 200:
{
  "answer": "Based on the provided documents...",
  "sources": [
    {
      "document_id": "uuid",
      "document_name": "document.pdf",
      "chunk_id": "uuid",
      "similarity_score": 0.85
    }
  ],
  "context_used": true
}
```

**Note**: If authenticated, the chat will only search documents owned by the user unless specific document_ids are provided.

### Search Documents
```http
POST /chat/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "search terms",
  "document_ids": ["uuid1", "uuid2"],  // optional
  "max_results": 10,
  "threshold": 0.7
}

Response 200:
{
  "query": "search terms",
  "results": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "document_name": "document.pdf",
      "content": "Relevant text content...",
      "similarity_score": 0.85,
      "metadata": {}
    }
  ],
  "total": 10
}
```

### Stream Chat Response
```http
POST /chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "Question?",
  "max_results": 5
}

Response: Server-Sent Events stream
data: {"text": "Partial response..."}
data: {"text": "More content..."}
data: {"sources": ["doc1.pdf", "doc2.pdf"], "done": true}
```

### WebSocket Chat
```
WS /chat/ws
Authorization: Bearer <token>

Send:
{
  "type": "query",
  "query": "Question?",
  "chat_history": []
}

Receive:
{
  "type": "text",
  "text": "Response chunk..."
}
{
  "type": "complete",
  "sources": ["doc1.pdf", "doc2.pdf"]
}
```

## Health Check

### Health Status
```http
GET /health

Response 200:
{
  "status": "healthy",
  "service": "brain-api",
  "version": "0.1.0",
  "components": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "s3": {"status": "healthy"},
    "embeddings": {"status": "healthy", "using_mock": true},
    "llm": {"status": "healthy", "using_mock": true}
  }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing the issue"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. This is planned for future releases.

## Pagination

Endpoints that return lists support pagination with `skip` and `limit` parameters:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 10, max: 100)

## Filtering

Some endpoints support filtering:
- Documents can be filtered by `status`
- Search endpoints support similarity threshold filtering

## Security Notes

1. All passwords are hashed using bcrypt
2. JWT tokens expire after 30 minutes
3. Documents are isolated per user
4. Admin endpoints require superuser privileges
5. All API calls should use HTTPS in production