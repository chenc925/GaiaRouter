# Development Guide

Welcome to the GaiaRouter development guide! This document will help you set up your development environment and understand our development process.

## 🎯 Development Philosophy

GaiaRouter is developed using **Spec-Driven Development (SDD)** methodology, emphasizing:

- **Specification First** - Define comprehensive specs before coding
- **Design Driven** - Base implementation on solid design documents
- **Task Decomposition** - Break down work into manageable tasks
- **Documentation Complete** - Maintain complete documentation at every stage

**→ Learn more about our SDD process: [SDD Documentation](sdd/README.md)**

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0+ or PostgreSQL 13+
- Git

### Development Environment Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-org/GaiaRouter.git
cd GaiaRouter
```

2. **Backend setup**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black isort mypy
```

3. **Frontend setup**

```bash
cd frontend
npm install
```

4. **Configure environment**

```bash
cp env.example .env
# Edit .env with your local configuration
```

5. **Initialize database**

```bash
python scripts/init.py
```

6. **Run services**

```bash
# Terminal 1: Backend
python -m uvicorn src.gaiarouter.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

## Development Workflow

### 1. Spec-Driven Development Process

GaiaRouter follows a structured development process:

```
Specs → Design → Tasks → Implementation → Testing → Documentation
```

**For new features:**

1. **Write Specification** (`docs/development/sdd/specs/`)
   - Define feature requirements
   - Document API contracts
   - Set success criteria

2. **Design Solution** (`docs/development/sdd/designs/`)
   - Architect the solution
   - Design module interactions
   - Plan data flows

3. **Break Down Tasks** (`docs/development/sdd/tasks/`)
   - Create actionable tasks
   - Estimate effort
   - Set priorities

4. **Implement** (`src/`)
   - Write code following design
   - Follow coding standards
   - Write tests

5. **Document** (`docs/`)
   - Update user documentation
   - Update API documentation
   - Update CHANGELOG

**→ See [SDD Documentation](sdd/README.md) for detailed methodology**

### 2. Git Workflow

We follow a feature branch workflow:

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push and create PR
git push origin feature/your-feature-name
```

**Commit message format:** [Conventional Commits](https://www.conventionalcommits.org/)

```
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: update dependencies
```

### 3. Code Review Process

1. Create Pull Request
2. Automated CI checks run
3. Code review by maintainers
4. Address feedback
5. Merge when approved

## Project Structure

```
GaiaRouter/
├── src/gaiarouter/         # Backend source code
│   ├── api/                # API layer - FastAPI endpoints
│   ├── router/             # Router layer - Model routing
│   ├── adapters/           # Adapter layer - Format conversion
│   ├── providers/          # Provider layer - External API clients
│   ├── auth/               # Authentication & authorization
│   ├── organizations/      # Organization management
│   ├── stats/              # Statistics tracking
│   └── database/           # Database models and migrations
│
├── frontend/               # Frontend application
│   ├── src/
│   │   ├── api/            # API client
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page views
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router
│
├── docs/development/       # Development documentation
│   ├── sdd/                # SDD process documents ⭐
│   │   ├── specs/          # Specifications
│   │   ├── designs/        # Design documents
│   │   └── tasks/          # Task breakdowns
│   ├── database.md         # Database guide
│   └── test-plan/          # Test plans
│
├── tests/                  # Test suites
├── scripts/                # Utility scripts
└── alembic/                # Database migrations
```

## Architecture Overview

GaiaRouter uses a **4-layer architecture**:

```
┌─────────────────────────────────────┐
│         Client Application           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  API Layer (FastAPI)                │  ← Endpoints, Auth, Validation
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Router Layer                        │  ← Model Routing, Load Balancing
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Adapter Layer                       │  ← Format Conversion
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Provider Layer                      │  ← External API Clients
└──────────────┬──────────────────────┘
               │
               ▼
        External AI APIs
```

**→ See [Architecture Documentation](../architecture/README.md) for details**

## Development Resources

### Documentation

- **[SDD Process](sdd/README.md)** ⭐ - Our development methodology
- **[Specifications](sdd/specs/)** - Feature specifications and requirements
- **[Design Documents](sdd/designs/)** - Architecture and module designs
- **[Task Breakdowns](sdd/tasks/)** - Development task decomposition
- **[Database Guide](database.md)** - Database schema and migrations
- **[Test Plan](test-plan/)** - Testing strategies

### Tools and Standards

- **Code Style**: Black (Python), ESLint + Prettier (TypeScript)
- **Type Checking**: mypy (Python), TypeScript
- **Testing**: pytest (Backend), Vitest (Frontend)
- **Documentation**: Markdown, JSDoc, Python docstrings

### Key Technologies

**Backend:**
- FastAPI - Async web framework
- SQLAlchemy - ORM
- Alembic - Database migrations
- httpx - HTTP client
- structlog - Structured logging

**Frontend:**
- Vue 3 - UI framework (Composition API)
- TypeScript - Type safety
- Vite - Build tool
- Arco Design - UI components
- Pinia - State management

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/gaiarouter --cov-report=html

# Run specific test
pytest tests/test_api.py::test_chat_completion
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test:unit

# Run with coverage
npm run test:unit -- --coverage
```

### Writing Tests

**Test Structure:**
```python
# tests/test_feature.py

import pytest
from src.gaiarouter.feature import function

async def test_function_success():
    """Test function with valid input"""
    result = await function(valid_input)
    assert result == expected_output

async def test_function_error():
    """Test function with invalid input"""
    with pytest.raises(ValueError):
        await function(invalid_input)
```

**→ See [Test Plan](test-plan/) for comprehensive testing guide**

## Code Quality

### Formatting and Linting

```bash
# Python
black .                    # Format code
isort .                    # Sort imports
mypy src/                  # Type checking

# TypeScript
cd frontend
npm run lint               # Lint code
npm run format             # Format code
```

### Pre-commit Hooks

Set up pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Database Development

### Creating Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add new table"

# Review and edit migration file
# Edit: alembic/versions/xxx_add_new_table.py

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

**→ See [Database Guide](database.md) for detailed instructions**

## Adding New Features

### Step-by-Step Process

Following SDD methodology:

1. **Write Specification**
   - Create `docs/development/sdd/specs/features/your-feature/spec.md`
   - Define requirements clearly
   - Get specification reviewed

2. **Create Design**
   - Create `docs/development/sdd/designs/your-feature/`
   - Design architecture and modules
   - Get design reviewed

3. **Break Down Tasks**
   - Create `docs/development/sdd/tasks/your-feature/task-breakdown.md`
   - List all implementation tasks
   - Estimate effort

4. **Implement**
   - Create feature branch
   - Implement according to design
   - Write tests (aim for >80% coverage)
   - Update documentation

5. **Test and Review**
   - Run all tests
   - Manual testing
   - Code review
   - Integration testing

6. **Document**
   - Update user documentation
   - Update API documentation
   - Update CHANGELOG.md

7. **Merge**
   - Address review feedback
   - Get approval
   - Merge to main

### Example: Adding a New Provider

```bash
# 1. Create specification
docs/development/sdd/specs/features/new-provider/
├── spec.md              # Provider overview
├── requirements.md      # Detailed requirements
└── api.md              # API integration details

# 2. Create design
docs/development/sdd/designs/new-provider/
├── architecture.md      # How it fits into system
└── implementation.md    # Implementation details

# 3. Implement
src/gaiarouter/
├── adapters/
│   └── new_provider_adapter.py
└── providers/
    └── new_provider.py

# 4. Test
tests/
├── test_new_provider_adapter.py
└── test_new_provider.py

# 5. Document
docs/
├── api/api-documentation.md    # Update API docs
└── getting-started/            # Update guides
```

## Debugging

### Backend Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use VS Code debugger
# See .vscode/launch.json
```

### Frontend Debugging

```javascript
// Browser DevTools
console.log('Debug info:', data)

// Vue DevTools
// Install browser extension
```

### Common Issues

**Database connection errors:**
```bash
# Check database is running
mysql -u root -p

# Check .env configuration
cat .env | grep DB_
```

**Import errors:**
```bash
# Ensure virtual environment is activated
which python

# Reinstall dependencies
pip install -r requirements.txt
```

## Performance Optimization

### Profiling

```python
# Python profiling
python -m cProfile -o output.prof script.py

# Analyze results
python -m pstats output.prof
```

### Monitoring

- Use structlog for structured logging
- Monitor async operations
- Track database query performance

## Contributing

We welcome contributions! Please:

1. Read [CONTRIBUTING.md](../../CONTRIBUTING.md)
2. Understand our [SDD process](sdd/README.md) ⭐
3. Follow coding standards
4. Write tests
5. Update documentation

## Resources

### Internal Documentation

- [SDD Methodology](sdd/README.md) ⭐
- [Architecture Overview](../architecture/README.md)
- [API Documentation](../api/api-documentation.md)
- [Database Guide](database.md)
- [Test Plan](test-plan/)

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions
- **Code Review**: Request feedback on your PR

---

<div align="center">

**[⬆ Back to Top](#development-guide)**

Happy coding! 🚀

</div>
