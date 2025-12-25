# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GaiaRouter is an AI model routing service that provides a unified API interface to access multiple AI model providers (OpenAI, Anthropic, Google, OpenRouter). It features streaming support, request/response format conversion, and a complete admin dashboard.

**Tech Stack:**
- Backend: Python 3.11+ with FastAPI, SQLAlchemy, Alembic
- Frontend: Vue 3 + TypeScript + Arco Design Vue + Pinia
- Database: MySQL/PostgreSQL (Alibaba Cloud RDS)

## Common Commands

### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env.example .env
# Edit .env file with actual values (see ENV_SETUP.md)

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.gaiarouter.main:app --reload

# Code formatting and linting
black src/
flake8 src/
mypy src/

# Run tests (if available)
pytest
pytest --cov=src  # with coverage
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and fix
npm run lint
```

### Database Migrations

```bash
# Create a new migration
alembic revision -m "description"

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history
```

### Docker

```bash
# Start all services
docker-compose up -d

# Run migrations in Docker
docker-compose exec api alembic upgrade head

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## Architecture Overview

GaiaRouter uses a **layered architecture** with clear separation of concerns:

### Backend Layer Structure

```
API Layer → Router Layer → Adapter Layer → Provider Layer
```

1. **API Layer** (`src/gaiarouter/api/`)
   - Controllers handle HTTP requests/responses
   - Middleware: auth, logging, error handling
   - Schemas: request/response validation with Pydantic

2. **Router Layer** (`src/gaiarouter/router/`)
   - `ModelRouter` parses model identifiers and selects providers
   - `ModelRegistry` maintains model-to-provider mappings
   - Handles model routing logic (e.g., `openrouter/` prefix handling)

3. **Adapter Layer** (`src/gaiarouter/adapters/`)
   - `RequestAdapter`: converts unified format → provider-specific format
   - `ResponseAdapter`: converts provider format → unified format
   - Handles both regular and streaming responses
   - Each provider has its own adapter implementation

4. **Provider Layer** (`src/gaiarouter/providers/`)
   - `Provider` base class defines interface
   - Provider implementations for OpenAI, Anthropic, Google, OpenRouter
   - Handles actual HTTP calls to external APIs using httpx
   - Each provider manages its own API key and endpoints

### Key Components

- **Authentication** (`src/gaiarouter/auth/`)
  - `api_key_manager.py`: API key validation and management
  - `jwt_token.py`: JWT token generation for admin dashboard
  - `permission.py`: Role-based access control (read/write/admin)

- **Organizations** (`src/gaiarouter/organizations/`)
  - Organization management with hierarchical structure
  - Usage limits tracking (requests, tokens, costs)
  - Multi-tenancy support

- **Stats** (`src/gaiarouter/stats/`)
  - `collector.py`: collects request statistics
  - `storage.py`: persists stats to database
  - `query.py`: aggregates stats by date/model/provider

- **Database** (`src/gaiarouter/database/`)
  - `models.py`: SQLAlchemy ORM models
  - `connection.py`: database connection and session management
  - Uses Alembic for migrations

### Frontend Architecture

- **Views** (`frontend/src/views/`): Page components organized by feature
  - ApiKeys/, Organizations/, Stats/, Models/, Dashboard/, Chat/

- **Stores** (`frontend/src/stores/`): Pinia state management
  - One store per feature (auth, apiKeys, organizations, stats)

- **API** (`frontend/src/api/`): API client wrappers
  - Uses axios with centralized request/response interceptors
  - Error handling in `utils/request.ts`

## Important Patterns and Conventions

### Model ID Format
- Internal models: `{provider}/{model-name}` (e.g., `openai/gpt-4`)
- OpenRouter models: `openrouter/{original-id}` (e.g., `openrouter/anthropic/claude-2`)
- The router strips the `openrouter/` prefix when calling OpenRouter API

### Adding New Provider
1. Create provider class in `src/gaiarouter/providers/` inheriting from `Provider`
2. Create request/response adapters in `src/gaiarouter/adapters/`
3. Register in `ModelRouter._init_providers()` and `_init_adapters()`
4. Add API key to settings and environment variables
5. Register models in `ModelRegistry`

### Streaming Response Handling
- FastAPI uses `StreamingResponse` with SSE format
- Adapters implement `adapt_stream_chunk()` for chunk conversion
- Providers must yield chunks in their `chat_completion()` method when `stream=True`

### Database Sessions
- Use dependency injection: `db: Session = Depends(get_db)`
- Sessions are auto-committed/rolled back by FastAPI
- Don't manually commit in most cases

### Error Handling
- Custom exceptions in `src/gaiarouter/utils/errors.py`
- Global error handler in `src/gaiarouter/api/middleware/error.py`
- Returns structured error responses with appropriate HTTP status codes

## Configuration

### Environment Variables
The project uses `.env` file for configuration (never commit this file):

**Required:**
- Database: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- At least one provider API key: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`

**Optional:**
- Server: `HOST` (default: 0.0.0.0), `PORT` (default: 8000), `DEBUG` (default: false)

See `ENV_SETUP.md` for detailed configuration instructions.

### YAML Configuration
- `config.yaml` is deprecated in favor of environment variables
- Settings loaded via `src/gaiarouter/config/settings.py` using Pydantic Settings

## Development Workflow

### SDD (Spec-Driven Development)
This project follows SDD methodology:
- **specs/**: Feature specifications and requirements
- **designs/**: Architecture and module designs
- **tasks/**: Task breakdowns
- **docs/**: API documentation, deployment guides, user guides

When implementing features, refer to corresponding spec/design documents first.

### Code Style
- **Python**: Follow PEP 8, use black for formatting, type hints required
- **TypeScript**: ESLint configuration in frontend/, 2-space indentation
- **Naming**:
  - Python: snake_case for functions/variables, PascalCase for classes
  - TypeScript/Vue: camelCase for functions/variables, PascalCase for components

### API Documentation
- FastAPI auto-generates docs at `/docs` (Swagger UI) and `/redoc`
- Keep Pydantic schemas in `src/gaiarouter/api/schemas/`
- Update `docs/api/api-documentation.md` for major API changes

## Testing

The project includes pytest configuration in requirements.txt but test files are not yet implemented. When writing tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_router.py

# Run with verbose output
pytest -v
```

## Common Issues

### Database Connection
- Ensure Alembic migrations are up to date: `alembic upgrade head`
- Check database credentials in `.env`
- Verify network access to Alibaba Cloud RDS

### Model Not Found Errors
- Verify provider API key is set in `.env`
- Check model is registered in `ModelRegistry`
- For OpenRouter, ensure model ID includes `openrouter/` prefix

### CORS Issues
- Frontend dev server origins are configured in `src/gaiarouter/main.py`
- Add new origins to `cors_origins` list if needed

### Streaming Not Working
- Ensure client properly handles Server-Sent Events (SSE)
- Check provider adapter implements `adapt_stream_chunk()`
- Verify provider API key has streaming permissions
