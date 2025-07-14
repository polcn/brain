import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface Document {
  id: string
  filename: string
  file_size: number
  file_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  created_at: string
  updated_at: string
  page_count?: number
  chunk_count?: number
  s3_key?: string
}

export interface ChatMessage {
  id?: string
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    document_id: string
    document_name: string
    chunk_text: string
    score: number
  }>
  timestamp?: string
}

export interface ChatResponse {
  response: string
  sources: Array<{
    document_id: string
    document_name: string
    chunk_text: string
    score: number
  }>
}

export interface HealthStatus {
  status: string
  database: boolean
  vector_store: boolean
  embeddings_service: boolean
  llm_service: boolean
  timestamp: string
}

export const documentsApi = {
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  list: async (skip = 0, limit = 20) => {
    const response = await api.get<Document[]>('/documents', {
      params: { skip, limit },
    })
    return response.data
  },

  get: async (id: string) => {
    const response = await api.get<Document>(`/documents/${id}`)
    return response.data
  },

  delete: async (id: string) => {
    await api.delete(`/documents/${id}`)
  },

  download: async (id: string) => {
    const response = await api.get(`/documents/${id}/download`, {
      responseType: 'blob',
    })
    return response.data
  },
}

export const chatApi = {
  query: async (query: string, documentIds?: string[]) => {
    const response = await api.post<ChatResponse>('/chat', {
      query,
      document_ids: documentIds,
    })
    return response.data
  },
}

export const healthApi = {
  check: async () => {
    const response = await api.get<HealthStatus>('/health')
    return response.data
  },
}

export default api