# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Standard open-source project documentation structure
- Comprehensive examples for API usage
- Architecture documentation with diagrams
- Contributing guidelines

### Changed
- Reorganized documentation following best practices
- Improved README with badges and better structure

## [1.0.0] - 2025-12-25

### Added
- Initial release of GaiaRouter
- Multi-provider AI model routing (OpenAI, Anthropic, Google, OpenRouter)
- Unified API interface compatible with OpenAI format
- Streaming response support via Server-Sent Events
- API key management system
- Organization management
- Usage statistics and monitoring
- Admin dashboard (Vue 3 + TypeScript)
- Database migrations with Alembic
- Docker support with docker-compose
- Comprehensive documentation

### Features

#### Core Functionality
- 4-layer architecture (API → Router → Adapter → Provider)
- Request/response format conversion for different providers
- Automatic model routing based on model ID
- Fallback handling for provider failures
- Rate limiting and usage quotas

#### API Endpoints
- `POST /v1/chat/completions` - Chat completion with streaming
- `GET /v1/models` - List available models
- `POST /v1/api-keys` - Create API key
- `GET /v1/api-keys` - List API keys
- `PATCH /v1/api-keys/{id}` - Update API key
- `DELETE /v1/api-keys/{id}` - Delete API key
- `POST /v1/organizations` - Create organization
- `GET /v1/organizations` - List organizations
- `GET /v1/stats` - Usage statistics

#### Backend
- FastAPI framework with async support
- SQLAlchemy ORM with MySQL/PostgreSQL support
- Structured logging with structlog
- Environment-based configuration
- JWT authentication
- Comprehensive error handling

#### Frontend
- Vue 3 with Composition API
- TypeScript for type safety
- Arco Design Vue component library
- Pinia state management
- ECharts data visualization
- Responsive design

#### Developer Tools
- Unified initialization script (`scripts/init.py`)
- Model synchronization tool (`scripts/sync_models.py`)
- Database migration management
- Alembic for schema versioning
- Development scripts

### Documentation
- Getting Started guide
- Installation and configuration guides
- API documentation with examples
- Architecture overview
- Deployment guides (Standard, Docker)
- User guide
- Maintenance manual
- Testing documentation

### Security
- API key authentication
- Hashed API key storage
- Permission-based access control (read/write/admin)
- Environment variable configuration
- No hardcoded credentials
- CORS configuration

### Performance
- Async I/O for concurrent request handling
- HTTP connection pooling
- Streaming responses for reduced latency
- Database query optimization
- Efficient error handling

## [0.2.0] - 2025-12-24

### Added
- Configuration improvements and cleanup
- Security fixes for credential management
- Initialization script consolidation

### Changed
- Removed hardcoded passwords from `alembic.ini`
- Consolidated initialization scripts
- Improved environment variable documentation

### Removed
- Redundant migration scripts (moved to archive)
- Obsolete configuration files (moved to archive)
- Duplicate model table creation script

## [0.1.0] - 2025-12-20

### Added
- Initial project structure
- Basic routing functionality
- OpenRouter integration
- Database schema design
- Basic API endpoints

### Development
- Set up FastAPI backend
- Set up Vue 3 frontend
- Database migrations with Alembic
- Docker configuration

---

## Version History

- **1.0.0** (2025-12-25) - First stable release
- **0.2.0** (2025-12-24) - Configuration and security improvements
- **0.1.0** (2025-12-20) - Initial development version

## Links

- [GitHub Repository](https://github.com/your-org/GaiaRouter)
- [Documentation](https://docs.gaiarouter.com)
- [Issue Tracker](https://github.com/your-org/GaiaRouter/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.
