# AMAW MVP Backend

Agentic Multimodal AI Workspace - Backend API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
```bash
cp env.example .env
# Edit .env with your API keys
```

### 3. Set Up PostgreSQL Database
```bash
# Create database
createdb amaw_mvp

# Initialize tables
python init_db.py
```

### 4. Start the Server
```bash
python start.py
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Yes |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage directory | No |

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Configuration
│   ├── database/      # Database connection
│   ├── models/        # Database models
│   └── services/      # Business logic
├── main.py           # FastAPI application
├── start.py          # Startup script
└── init_db.py        # Database initialization
```

### API Endpoints

#### YouTube API (`/api/youtube`)
- `POST /extract` - Extract content from YouTube URL
- `GET /video/{video_id}` - Get video information
- `POST /validate` - Validate YouTube URL

#### AI API (`/api/ai`)
- `POST /process` - Process AI request with context
- `POST /analyze` - Analyze content from connected nodes
- `POST /generate-image` - Generate image using Gemini
- `GET /chat/{node_id}` - Get chat history

#### Nodes API (`/api/nodes`)
- `POST /create` - Create a new node
- `GET /list` - Get all nodes
- `GET /{node_id}` - Get specific node
- `PUT /{node_id}` - Update node
- `DELETE /{node_id}` - Delete node
- `GET /{node_id}/content` - Get node content

## 🗄️ Database Schema

### Tables
- **nodes** - Canvas nodes
- **content** - Extracted content
- **embeddings** - Vector embeddings
- **chat_sessions** - AI chat history
- **generated_images** - AI-generated images

### Vector Database
- **ChromaDB** - Local vector storage for embeddings

## 🤖 AI Integration

### Gemini AI
- **Text Generation** - Content analysis and responses
- **Image Generation** - AI-generated images
- **Content Processing** - YouTube video analysis

### YouTube Data API
- **Video Information** - Metadata extraction
- **Content Analysis** - Transcript and description processing

## 🔄 Development Workflow

1. **Backend Development** - FastAPI server with PostgreSQL
2. **Frontend Integration** - React app connects to backend
3. **AI Processing** - Gemini handles content analysis
4. **Vector Storage** - ChromaDB for embeddings

## 📝 Next Steps

1. Set up API keys (Gemini, YouTube)
2. Configure PostgreSQL database
3. Test API endpoints
4. Integrate with frontend
5. Deploy and scale
