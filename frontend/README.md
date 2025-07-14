# Brain Frontend

React-based frontend for the Brain Document AI Assistant.

## Features

- 📄 Document upload with drag-and-drop
- 💬 Interactive chat interface
- 📊 Document management dashboard
- 🔍 Source attribution for AI responses
- 🎨 Material-UI components
- 🔄 Real-time status updates

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:3001

### Docker Development

```bash
# From project root
make frontend-up    # Start frontend container
make frontend-logs  # View logs
make frontend-down  # Stop frontend
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components (routes)
├── services/      # API service layer
├── utils/         # Utility functions
├── hooks/         # Custom React hooks
└── styles/        # Global styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

## Environment Variables

Create a `.env.local` file:

```env
VITE_API_URL=http://localhost:8001
```

## Tech Stack

- React 18
- TypeScript
- Vite
- Material-UI
- React Query
- React Router
- Axios
- React Dropzone