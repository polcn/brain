import { useState, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Send as SendIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material'
import { useMutation } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import { chatApi, ChatMessage } from '../services/api'

function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const chatMutation = useMutation({
    mutationFn: (query: string) => chatApi.query(query),
    onSuccess: (data) => {
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        sources: data.sources,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    },
    onError: (error: any) => {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || 'Failed to get response'}`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || chatMutation.isPending) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    chatMutation.mutate(input)
    setInput('')
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {messages.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
            }}
          >
            <Typography variant="h6" color="text.secondary">
              Start a conversation by asking a question about your documents
            </Typography>
          </Box>
        ) : (
          messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              <Card
                sx={{
                  maxWidth: '70%',
                  backgroundColor:
                    message.role === 'user'
                      ? 'primary.main'
                      : 'background.paper',
                  color: message.role === 'user' ? 'white' : 'text.primary',
                }}
              >
                <CardContent>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </Box>
                  {message.sources && message.sources.length > 0 && (
                    <Accordion sx={{ mt: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="body2">
                          Sources ({message.sources.length})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        {message.sources.map((source, idx) => (
                          <Box key={idx} sx={{ mb: 2 }}>
                            <Chip
                              label={source.document_name}
                              size="small"
                              sx={{ mb: 1 }}
                            />
                            <Typography
                              variant="body2"
                              sx={{
                                fontSize: '0.875rem',
                                p: 1,
                                backgroundColor: 'grey.100',
                                borderRadius: 1,
                              }}
                            >
                              {source.chunk_text}
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Relevance: {(source.score * 100).toFixed(1)}%
                            </Typography>
                          </Box>
                        ))}
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>
              </Card>
            </Box>
          ))
        )}
        {chatMutation.isPending && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
            <Card>
              <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={20} sx={{ mr: 2 }} />
                <Typography>Thinking...</Typography>
              </CardContent>
            </Card>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>
      <Paper
        component="form"
        onSubmit={handleSubmit}
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask a question about your documents..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={chatMutation.isPending}
          sx={{ mr: 1 }}
        />
        <IconButton
          type="submit"
          color="primary"
          disabled={!input.trim() || chatMutation.isPending}
        >
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  )
}

export default ChatPage