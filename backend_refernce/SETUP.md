# AMAW MVP Backend Setup Guide

## 🚀 Quick Setup Instructions

### 1. Create Environment File
Create a `.env` file in the backend directory with the following content:

```env
# Database Configuration
DATABASE_URL=postgresql://amaw_user:amaw_password@localhost:5432/amaw_mvp
POSTGRES_USER=amaw_user
POSTGRES_PASSWORD=amaw_password
POSTGRES_DB=amaw_mvp

# AI API Keys - ADD YOUR KEYS HERE
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# YouTube API - ADD YOUR KEY HERE
YOUTUBE_API_KEY=your_youtube_api_key_here

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# File Upload Settings
MAX_FILE_SIZE=50MB
UPLOAD_DIRECTORY=./uploads
```

### 2. Get API Keys

#### Gemini API Key (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy the key and replace `your_gemini_api_key_here` in .env

#### YouTube Data API v3 Key (Required)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the key and replace `your_youtube_api_key_here` in .env

### 3. Set Up PostgreSQL Database
```bash
# Install PostgreSQL (if not already installed)
# Windows: Download from https://www.postgresql.org/download/windows/

# Create database
createdb amaw_mvp

# Or using psql:
psql -U postgres
CREATE DATABASE amaw_mvp;
CREATE USER amaw_user WITH PASSWORD 'amaw_password';
GRANT ALL PRIVILEGES ON DATABASE amaw_mvp TO amaw_user;
\q
```

### 4. Initialize Database
```bash
cd backend
python init_db.py
```

### 5. Start the Backend Server
```bash
python start.py
```

The server will start at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## 🎯 Next Steps

1. **Test the API**: Visit http://localhost:8000/docs to test endpoints
2. **Frontend Integration**: Connect your React app to the backend
3. **YouTube Node**: Implement the YouTube node in your frontend
4. **AI Chat Integration**: Connect AI processing to your chat nodes

## 🔧 Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check database credentials in .env
- Verify database exists

### API Key Issues
- Ensure API keys are valid and active
- Check quota limits for YouTube API
- Verify Gemini API key permissions

### Port Conflicts
- Change port in start.py if 8000 is occupied
- Update CORS_ORIGINS in .env for different frontend ports

## 📚 API Endpoints

### YouTube API
- `POST /api/youtube/extract` - Extract content from YouTube URL
- `GET /api/youtube/video/{video_id}` - Get video information
- `POST /api/youtube/validate` - Validate YouTube URL

### AI API
- `POST /api/ai/process` - Process AI request with context
- `POST /api/ai/analyze` - Analyze content from connected nodes
- `POST /api/ai/generate-image` - Generate image using Gemini
- `GET /api/ai/chat/{node_id}` - Get chat history

### Nodes API
- `POST /api/nodes/create` - Create a new node
- `GET /api/nodes/list` - Get all nodes
- `GET /api/nodes/{node_id}` - Get specific node
- `PUT /api/nodes/{node_id}` - Update node
- `DELETE /api/nodes/{node_id}` - Delete node
- `GET /api/nodes/{node_id}/content` - Get node content

## 🎉 You're Ready!

Your backend is now set up and ready to power your AMAW MVP frontend!
