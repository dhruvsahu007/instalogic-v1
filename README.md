# InstaLogic - Full Stack Application

A modern single-page website built with React (frontend) and FastAPI (backend).

## Project Structure

```
InstaLogic/
├── frontend/           # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   │   └── homepagess.png
│   └── package.json
│
├── backend/            # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
│
└── README.md
```

## Quick Start

### Backend Setup

1. Navigate to the backend folder:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
.\venv\Scripts\activate.bat
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend folder:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Features

### Frontend
- ⚛️ React 18 with Vite
- 🎨 Modern, responsive design
- 🖼️ Custom background image
- 📱 Mobile-friendly navigation
- 🔄 Smooth scrolling
- 📮 Contact form with backend integration

### Backend
- 🚀 FastAPI framework
- 🔌 RESTful API endpoints
- 📊 Services management
- 📧 Contact form handling
- 🔒 CORS configured
- 📝 Auto-generated API docs

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/services` - Get all services
- `GET /api/services/{id}` - Get specific service
- `POST /api/contact` - Submit contact form
- `GET /api/contact/messages` - Get all messages (admin)
- `GET /api/health` - Health check

## Technologies

### Frontend
- React 18
- Vite
- Axios
- CSS3

### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic

## Development

1. Start the backend server first (runs on port 8000)
2. Start the frontend server (runs on port 3000)
3. The frontend is configured to proxy API requests to the backend

## Production Build

### Frontend
```bash
cd frontend
npm run build
```

### Backend
Use a production ASGI server like Gunicorn with Uvicorn workers:
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

© 2025 InstaLogic. All rights reserved.
