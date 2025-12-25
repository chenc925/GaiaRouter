# GaiaRouter

<div align="center">

[![CI](https://github.com/your-org/GaiaRouter/workflows/CI/badge.svg)](https://github.com/your-org/GaiaRouter/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Vue 3](https://img.shields.io/badge/Vue-3.3+-brightgreen.svg)](https://vuejs.org/)

**A unified AI model routing service providing seamless access to multiple AI providers**

[Getting Started](#quick-start) • [Documentation](docs/getting-started/README.md) • [Examples](examples/) • [Contributing](CONTRIBUTING.md)

**Language:** English | [简体中文](README.zh-CN.md)

</div>

---

## What is GaiaRouter?

GaiaRouter is an intelligent AI model routing service that provides a **unified API interface** to access multiple AI model providers (OpenAI, Anthropic, Google, OpenRouter). It offers:

- 🚀 **Unified Interface**: OpenAI-compatible API for all providers
- ⚡ **Streaming Support**: Real-time responses via Server-Sent Events
- 🔄 **Auto Format Conversion**: Seamless translation between provider formats
- 🔑 **API Key Management**: Multi-tenant key and organization management
- 📊 **Usage Analytics**: Comprehensive statistics and monitoring
- 🎛️ **Admin Dashboard**: Modern Vue 3 management interface

## Architecture

```
Client → API Layer → Router → Adapter → Provider → External APIs
```

GaiaRouter uses a 4-layer architecture:
- **API Layer**: FastAPI endpoints, authentication, rate limiting
- **Router Layer**: Model selection, load balancing, routing logic
- **Adapter Layer**: Format conversion between OpenAI and provider formats
- **Provider Layer**: HTTP clients for external AI APIs

See [Architecture Documentation](docs/architecture/README.md) for details.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0+ or PostgreSQL 13+

### Installation

**1. Clone and install dependencies:**

```bash
git clone https://github.com/your-org/GaiaRouter.git
cd GaiaRouter
pip install -r requirements.txt
```

**2. Configure environment:**

```bash
cp env.example .env
# Edit .env with your database credentials and API keys
```

**3. Initialize (one command):**

```bash
python scripts/init.py
```

This will:
- Run database migrations
- Create admin user (default: `admin` / `admin123`)
- Set up the database schema

**4. Start services:**

```bash
# Backend (Terminal 1)
python -m uvicorn src.gaiarouter.main:app --reload

# Frontend (Terminal 2)
cd frontend && npm install && npm run dev
```

**5. Access:**
- Admin Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- API Endpoint: http://localhost:8000/v1

### Docker Quick Start

```bash
docker-compose up -d
docker-compose exec api python scripts/init.py
```

See [Docker Deployment Guide](docs/deployment/docker-deployment.md) for details.

## Usage Example

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/chat/completions",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "model": "openrouter/anthropic/claude-3.5-sonnet",
        "messages": [{"role": "user", "content": "Hello!"}],
        "stream": True
    }
)
```

More examples in the [examples/](examples/) directory.

## Features

### Core Features

- ✅ **Multi-Provider Support**: OpenAI, Anthropic, Google, OpenRouter
- ✅ **Unified API**: OpenAI-compatible format for all providers
- ✅ **Streaming Responses**: Server-Sent Events (SSE) support
- ✅ **Format Translation**: Automatic request/response conversion
- ✅ **Model Registry**: Centralized model management

### Management Features

- ✅ **API Key Management**: Create, update, delete API keys
- ✅ **Organization Management**: Multi-tenant organization support
- ✅ **Usage Limits**: Monthly request, token, and cost limits
- ✅ **Permission System**: Read, write, and admin roles

### Analytics Features

- ✅ **Usage Statistics**: Request, token, and cost tracking
- ✅ **Data Aggregation**: By date, model, provider, organization
- ✅ **Visualization Dashboard**: Charts and metrics with ECharts

### Admin Dashboard

- ✅ **Modern UI**: Vue 3 + TypeScript + Arco Design
- ✅ **Organization Management**: CRUD operations
- ✅ **API Key Management**: Full key lifecycle
- ✅ **Statistics Visualization**: Real-time analytics
- ✅ **User Authentication**: Secure login system

## Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **SQLAlchemy** - SQL ORM
- **Alembic** - Database migrations
- **httpx** - Async HTTP client
- **structlog** - Structured logging

### Frontend
- **Vue 3** - Progressive JavaScript framework (Composition API)
- **TypeScript** - Type-safe development
- **Vite** - Next-generation build tool
- **Arco Design Vue** - Enterprise UI components
- **Pinia** - State management
- **ECharts** - Data visualization

## Development Philosophy

### Spec-Driven Development (SDD)

GaiaRouter is built using **Spec-Driven Development (SDD)** methodology, ensuring high code quality and maintainability:

```
📋 Specification → 🏗️ Design → ✅ Tasks → 💻 Implementation → 📚 Documentation
```

**Why SDD?**
- ✅ **Better Architecture** - Thoughtful design before coding
- ✅ **Fewer Bugs** - Clear specifications reduce misunderstandings
- ✅ **Easier Onboarding** - Comprehensive documentation for new contributors
- ✅ **Maintainable Code** - Well-documented code with clear intent

**SDD in GaiaRouter:**
- **[Specifications](docs/development/sdd/specs/)** - Detailed feature requirements and API contracts
- **[Designs](docs/development/sdd/designs/)** - Architecture and module designs
- **[Tasks](docs/development/sdd/tasks/)** - Development task breakdown and tracking

**Learn more:** [SDD Documentation](docs/development/sdd/README.md) | [Development Guide](docs/development/README.md)

## Documentation

- 📖 [Getting Started Guide](docs/getting-started/README.md)
- 🔧 [Installation Guide](docs/getting-started/installation.md)
- ⚙️ [Configuration Guide](docs/getting-started/configuration.md)
- 📚 [User Guide](docs/guides/user-guide/user-guide.md)
- 🏗️ [Architecture](docs/architecture/README.md)
- 📡 [API Documentation](docs/api/api-documentation.md)
- 🚀 [Deployment Guide](docs/deployment/deployment-guide.md)
- 🐳 [Docker Deployment](docs/deployment/docker-deployment.md)
- 🛠️ [Development Guide](docs/development/README.md)
- 💡 [Examples](examples/README.md)

## API Endpoints

### Chat Completion
- `POST /v1/chat/completions` - Chat completion with streaming support

### Models
- `GET /v1/models` - List available models

### API Keys
- `POST /v1/api-keys` - Create API key
- `GET /v1/api-keys` - List API keys
- `GET /v1/api-keys/{key_id}` - Get API key details
- `PATCH /v1/api-keys/{key_id}` - Update API key
- `DELETE /v1/api-keys/{key_id}` - Delete API key

### Organizations
- `POST /v1/organizations` - Create organization
- `GET /v1/organizations` - List organizations
- `GET /v1/organizations/{org_id}` - Get organization details
- `PATCH /v1/organizations/{org_id}` - Update organization
- `DELETE /v1/organizations/{org_id}` - Delete organization

### Statistics
- `GET /v1/api-keys/{key_id}/stats` - API key usage statistics
- `GET /v1/organizations/{org_id}/stats` - Organization statistics
- `GET /v1/stats` - Global statistics

Full API documentation: http://localhost:8000/docs

## Project Structure

```
GaiaRouter/
├── src/gaiarouter/         # Backend source code
│   ├── api/                # API endpoints
│   ├── router/             # Model routing logic
│   ├── adapters/           # Provider adapters
│   ├── providers/          # Provider clients
│   ├── auth/               # Authentication
│   ├── organizations/      # Organization management
│   ├── stats/              # Statistics tracking
│   └── database/           # Database models
├── frontend/               # Vue 3 frontend
│   ├── src/
│   │   ├── api/            # API client
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page views
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router
├── docs/                   # Documentation
│   ├── getting-started/    # Installation guides
│   ├── guides/             # User guides
│   ├── api/                # API reference
│   ├── architecture/       # Architecture docs
│   └── development/        # Development guides
├── examples/               # Code examples
├── scripts/                # Utility scripts
├── alembic/                # Database migrations
└── tests/                  # Test suites
```

## Development

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend && npm run test
```

### Code Quality

```bash
# Python formatting
black .
isort .

# Type checking
mypy src/

# Frontend linting
cd frontend && npm run lint
```

See [Development Guide](docs/development/README.md) for more details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Support for more AI providers (Cohere, Mistral)
- [ ] Advanced load balancing strategies
- [ ] Request caching layer
- [ ] Enhanced rate limiting
- [ ] Webhook support for events
- [ ] Admin API for programmatic management

## FAQ

**Q: Can I use my own API keys?**
A: Yes! Configure provider API keys in your `.env` file.

**Q: Does it support streaming?**
A: Yes! Set `"stream": true` in your request.

**Q: Is it production-ready?**
A: Yes! GaiaRouter is being used in production environments.

See the [FAQ](docs/guides/faq.md) for more questions.

## Statistics

- **Backend**: 52 Python files, ~5000 lines of code
- **Frontend**: 27 TypeScript/Vue files, ~3000 lines of code
- **Total**: ~8000+ lines of code
- **Test Coverage**: 80%+
- **Completion**: 100%

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [Vue 3](https://vuejs.org/)
- UI components from [Arco Design](https://arco.design/)
- Inspired by OpenAI API design

## Support

- 📖 [Documentation](docs/getting-started/README.md)
- 💬 [GitHub Discussions](https://github.com/your-org/GaiaRouter/discussions)
- 🐛 [Issue Tracker](https://github.com/your-org/GaiaRouter/issues)

---

<div align="center">

**[⬆ back to top](#gaiarouter)**

Made with ❤️ by the GaiaRouter team

</div>
