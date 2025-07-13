# Brain API Documentation

Base URL: `http://localhost:8001/api/v1`

## Authentication

Currently using basic authentication. JWT tokens will be implemented in the next phase.

## Endpoints

### Health Check

**GET** `/health`

Check if the service is running and all dependencies are healthy.

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "pgvector": "enabled",
  "services": {
    "embeddings": "healthy",
    "llm": "healthy",
    "vector_store": "healthy"
  }
}
```

### Documents

#### Upload Document

**POST** `/documents/upload`

Upload a document for processing. The document will be redacted, chunked, and indexed.

Request:
- Method: `multipart/form-data`
- Field: `file` (required) - PDF, TXT, or DOCX file

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "example.pdf",
  "mime_type": "application/pdf",
  "size": 1024000,
  "status": "processed",
  "chunk_count": 42,
  "created_at": "2024-01-01T12:00:00Z",
  "processed_at": "2024-01-01T12:00:30Z"
}
```

#### List Documents

**GET** `/documents`

List all uploaded documents with pagination.

Query Parameters:
- `skip` (int, default: 0) - Number of documents to skip
- `limit` (int, default: 10, max: 100) - Number of documents to return
- `status` (string, optional) - Filter by status: `processing`, `processed`, `failed`

Response:
```json
{
  "documents": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "example.pdf",
      "mime_type": "application/pdf",
      "size": 1024000,
      "status": "processed",
      "chunk_count": 42,
      "created_at": "2024-01-01T12:00:00Z",
      "processed_at": "2024-01-01T12:00:30Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 10
}
```

#### Get Document

**GET** `/documents/{document_id}`

Get details of a specific document.

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "example.pdf",
  "mime_type": "application/pdf",
  "size": 1024000,
  "status": "processed",
  "chunk_count": 42,
  "created_at": "2024-01-01T12:00:00Z",
  "processed_at": "2024-01-01T12:00:30Z"
}
```

#### Delete Document

**DELETE** `/documents/{document_id}`

Delete a document and all its associated data.

Response:
```json
{
  "message": "Document deleted successfully"
}
```

#### Download Document

**GET** `/documents/{document_id}/download`

Download the processed (redacted) version of the document.

Response: Binary file stream

### Chat

#### Send Query

**POST** `/chat`

Send a query and get a response based on the indexed documents.

Request:
```json
{
  "query": "What is the main topic of the documents?",
  "max_results": 5,
  "document_ids": ["123e4567-e89b-12d3-a456-426614174000"],
  "similarity_threshold": 0.7,
  "chat_history": [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"}
  ]
}
```

Response:
```json
{
  "response": "Based on the documents, the main topic is...",
  "sources": ["document1.pdf", "document2.pdf"],
  "confidence": 0.85
}
```

#### Search Documents

**POST** `/chat/search`

Search for relevant document chunks without generating a response.

Request:
```json
{
  "query": "machine learning",
  "max_results": 10,
  "document_ids": ["123e4567-e89b-12d3-a456-426614174000"],
  "similarity_threshold": 0.7
}
```

Response:
```json
{
  "results": [
    {
      "chunk_id": "456e7890-e89b-12d3-a456-426614174000",
      "document_id": "123e4567-e89b-12d3-a456-426614174000",
      "document_name": "example.pdf",
      "content": "This chunk contains information about machine learning...",
      "similarity_score": 0.92,
      "metadata": {
        "page": 5,
        "section": "Introduction"
      }
    }
  ],
  "total": 3,
  "query": "machine learning"
}
```

#### Stream Chat Response

**POST** `/chat/stream`

Stream the chat response as it's generated.

Request: Same as `/chat`

Response: Server-Sent Events stream
```
data: {"text": "Based on"}
data: {"text": " the documents,"}
data: {"text": " the main topic is..."}
data: {"sources": ["document1.pdf"], "done": true}
```

#### WebSocket Chat

**WebSocket** `/chat/ws`

Real-time bidirectional chat communication.

Client Message:
```json
{
  "type": "query",
  "query": "What is the main topic?",
  "chat_history": []
}
```

Server Messages:
```json
{"type": "text", "text": "Based on the documents..."}
{"type": "complete", "sources": ["document1.pdf"]}
{"type": "error", "error": "Error message"}
```

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error description"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `413` - File Too Large
- `415` - Unsupported Media Type
- `500` - Internal Server Error

## Rate Limiting

Currently no rate limiting is implemented. This will be added in a future version.

## File Size Limits

- Maximum file size: 10MB
- Supported formats: PDF, TXT, DOCX

## Performance Notes

- Vector search typically returns in <100ms
- Document processing time varies: ~1-2 seconds per page
- Streaming responses have minimal latency
- WebSocket connections support real-time interaction