# InstaLogic Frontend

React + Vite frontend for the InstaLogic website.

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The build files will be in the `dist` folder.

## Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/              # Static assets
│   └── homepagess.png  # Background image
├── src/
│   ├── components/     # React components
│   │   ├── Navbar.jsx
│   │   ├── Hero.jsx
│   │   ├── Services.jsx
│   │   ├── About.jsx
│   │   ├── Contact.jsx
│   │   ├── Footer.jsx
│   │   └── Sidebar.jsx
│   ├── App.jsx         # Main App component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── index.html          # HTML template
├── vite.config.js      # Vite configuration
└── package.json        # Dependencies
```

## Features

- ⚡️ Built with Vite for fast development
- ⚛️ React 18
- 🎨 Component-based architecture
- 📱 Fully responsive design
- 🔗 API integration with FastAPI backend
- 🎯 Smooth scrolling navigation
- 📮 Contact form with backend integration

## Environment Variables

The backend API is proxied through Vite. The proxy is configured in `vite.config.js`.

## Technologies Used

- React 18
- Vite
- Axios for API calls
- CSS Modules
- Google Fonts (Poppins)
