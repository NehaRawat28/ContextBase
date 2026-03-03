# ContextBase AI Frontend

A modern, responsive React frontend for the ContextBase AI knowledge base assistant.

## Features

### 🎨 Modern UI/UX

- Clean, modern design with smooth animations and professional SVG icons
- Chat-like interface for natural conversations
- Responsive design that works on all devices
- Dark/light theme toggle with system preference detection

### 🚀 Enhanced User Experience

- Real-time typing indicators
- Auto-resizing text input
- Message timestamps
- Smooth scrolling to new messages
- Clear chat functionality
- Error handling with user-friendly messages

### ♿ Accessibility

- ARIA labels for screen readers
- Keyboard navigation support
- High contrast mode support
- Reduced motion support for users with vestibular disorders
- Focus indicators for all interactive elements
- Professional SVG icons instead of emojis for better accessibility

### 🛠 Technical Features

- Custom React hooks for API management
- Error boundary for graceful error handling
- CSS custom properties for theming
- Modern CSS with CSS Grid and Flexbox
- Optimized performance with React best practices
- Scalable SVG icon system

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Theme System

The app supports both light and dark themes:

- Automatically detects system preference
- Manual toggle available in the header
- Preference is saved to localStorage
- Smooth transitions between themes

## API Integration

The frontend connects to the Python backend at `http://127.0.0.1:8000` and expects:

- POST `/query` endpoint
- JSON payload: `{ "question": string, "k": number }`
- JSON response: `{ "answer": string }`

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers with modern CSS support

## React + Vite

This project uses React with Vite for fast development and building. The React Compiler is enabled for optimized performance.
