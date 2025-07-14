import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Chip,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import { useMutation } from '@tanstack/react-query'
import { documentsApi } from '../services/api'

interface UploadFile {
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  progress?: number
}

function UploadPage() {
  const [files, setFiles] = useState<UploadFile[]>([])
  const navigate = useNavigate()

  const uploadMutation = useMutation({
    mutationFn: async (uploadFile: UploadFile) => {
      return documentsApi.upload(uploadFile.file)
    },
    onSuccess: (_, uploadFile) => {
      setFiles((prev) =>
        prev.map((f) =>
          f.file === uploadFile.file ? { ...f, status: 'success' } : f
        )
      )
    },
    onError: (error: any, uploadFile) => {
      setFiles((prev) =>
        prev.map((f) =>
          f.file === uploadFile.file
            ? { ...f, status: 'error', error: error.response?.data?.detail || 'Upload failed' }
            : f
        )
      )
    },
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    onDrop: (acceptedFiles, rejectedFiles) => {
      const newFiles: UploadFile[] = acceptedFiles.map((file) => ({
        file,
        status: 'pending',
      }))
      setFiles((prev) => [...prev, ...newFiles])

      if (rejectedFiles.length > 0) {
        console.error('Rejected files:', rejectedFiles)
      }
    },
  })

  const handleUpload = async () => {
    const pendingFiles = files.filter((f) => f.status === 'pending')
    
    for (const uploadFile of pendingFiles) {
      setFiles((prev) =>
        prev.map((f) =>
          f.file === uploadFile.file ? { ...f, status: 'uploading' } : f
        )
      )
      await uploadMutation.mutateAsync(uploadFile)
    }
  }

  const handleClear = () => {
    setFiles([])
  }

  const handleViewDocuments = () => {
    navigate('/documents')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const pendingCount = files.filter((f) => f.status === 'pending').length
  const uploadingCount = files.filter((f) => f.status === 'uploading').length
  const successCount = files.filter((f) => f.status === 'success').length
  const errorCount = files.filter((f) => f.status === 'error').length

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Upload Documents
      </Typography>

      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 3,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          transition: 'all 0.2s',
          '&:hover': {
            backgroundColor: 'action.hover',
            borderColor: 'primary.main',
          },
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon sx={{ fontSize: 48, color: 'action.active', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag & drop files here, or click to select'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supported formats: PDF, TXT, DOCX (max 10MB)
        </Typography>
      </Paper>

      {files.length > 0 && (
        <>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              {pendingCount > 0 && (
                <Chip label={`${pendingCount} pending`} size="small" />
              )}
              {uploadingCount > 0 && (
                <Chip
                  label={`${uploadingCount} uploading`}
                  color="primary"
                  size="small"
                />
              )}
              {successCount > 0 && (
                <Chip
                  label={`${successCount} completed`}
                  color="success"
                  size="small"
                />
              )}
              {errorCount > 0 && (
                <Chip
                  label={`${errorCount} failed`}
                  color="error"
                  size="small"
                />
              )}
            </Box>

            <List>
              {files.map((uploadFile, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    {uploadFile.status === 'success' ? (
                      <CheckIcon color="success" />
                    ) : uploadFile.status === 'error' ? (
                      <ErrorIcon color="error" />
                    ) : (
                      <FileIcon />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={uploadFile.file.name}
                    secondary={
                      <>
                        {formatFileSize(uploadFile.file.size)}
                        {uploadFile.error && (
                          <Typography
                            component="span"
                            variant="body2"
                            color="error"
                            sx={{ ml: 1 }}
                          >
                            - {uploadFile.error}
                          </Typography>
                        )}
                      </>
                    }
                  />
                  {uploadFile.status === 'uploading' && (
                    <Box sx={{ width: 100 }}>
                      <LinearProgress />
                    </Box>
                  )}
                </ListItem>
              ))}
            </List>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={pendingCount === 0 || uploadingCount > 0}
                startIcon={<UploadIcon />}
              >
                Upload {pendingCount > 0 && `(${pendingCount})`}
              </Button>
              <Button onClick={handleClear} disabled={uploadingCount > 0}>
                Clear All
              </Button>
              {successCount > 0 && (
                <Button onClick={handleViewDocuments} color="success">
                  View Documents
                </Button>
              )}
            </Box>
          </Paper>
        </>
      )}

      <Alert severity="info">
        <Typography variant="body2">
          <strong>Important:</strong> All documents will be automatically redacted
          to remove any personally identifiable information (PII) before storage.
          The original documents are not retained.
        </Typography>
      </Alert>
    </Box>
  )
}

export default UploadPage