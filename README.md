# GitHub Repository Lens

A deep research analysis tool for GitHub repositories using LangGraph and MCP (Model Context Protocol).

## Features

- **Multi-Provider LLM Support**: OpenAI, Gemini, and OpenRouter
- **Real-time Analysis**: SSE streaming for live progress updates
- **LangGraph Integration**: Structured workflow for repository analysis
- **MCP Protocol**: Leverages `github-repo-mcp` for code/file access
- **PDF Report Generation**: Async PDF generation via Celery
- **Structured Output**: Modules, code highlights, and architectural principles

## Tech Stack

- **FastAPI** - Web framework with SSE streaming
- **LangChain v1 + LangGraph** - LLM orchestration and workflow
- **Celery + Redis** - Async task processing
- **Loguru** - Structured logging
- **WeasyPrint** - PDF generation

## Project Structure

```
app/
├── api/           # FastAPI routes and schemas
├── core/          # LLM factory, MCP client, logging
├── graph/         # LangGraph research workflow
├── mcp/           # MCP client implementation
├── prompts/       # Prompt templates (YAML)
├── services/      # Analyzer, PDF generator
├── tasks/         # Celery tasks
├── config.py      # Settings (pydantic-settings)
└── main.py        # FastAPI app entry point
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repo-url>
cd GithubRepoLens
cp env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up --build
```

Services:
- API: http://localhost:8000
- Flower (Celery monitor): http://localhost:5555

### 3. Run Locally

```bash
# Install dependencies
pip install -e ".[dev]"

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Start API
python -m uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A app.tasks.celery_tasks:celery_app worker --loglevel=info
```

## Configuration

Edit `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (`openai`, `gemini`, `openrouter`) | `openai` |
| `LLM_MODEL` | Model name | `gpt-4o-mini` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GEMINI_API_KEY` | Gemini API key | - |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |
| `CELERY_BROKER_URL` | Redis broker URL | `redis://localhost:6379/0` |

## API Endpoints

### Health Check
```
GET /api/health
```

### Analyze Repository (with SSE Streaming)
```
POST /api/analyze
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo",
  "language": "en"  // Optional: en (default), zh, ja, etc.
}

Response: Server-Sent Events (SSE) stream with real-time progress
```

### Generate PDF Report
```
POST /api/report/pdf
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo",
  "project_name": "my-project",
  "analysis_result": {...}
}
```

### Check PDF Status
```
GET /api/report/pdf/{task_id}
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## License

MIT
