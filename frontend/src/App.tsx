import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/Layout'
import DocumentsPage from './pages/DocumentsPage'
import ChatPage from './pages/ChatPage'
import UploadPage from './pages/UploadPage'

function App() {
  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </Layout>
    </Box>
  )
}

export default App