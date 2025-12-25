# Contributing to GaiaRouter

Thank you for your interest in contributing to GaiaRouter! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Philosophy](#development-philosophy)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Development Philosophy

### Spec-Driven Development (SDD)

GaiaRouter follows **Spec-Driven Development (SDD)** methodology. This means:

**📋 Specification First**
- Write comprehensive specifications before coding
- Define clear requirements and success criteria
- Document API contracts and behaviors

**🏗️ Design Driven**
- Create detailed design documents
- Plan architecture and module interactions
- Review designs before implementation

**✅ Task Decomposition**
- Break down work into manageable tasks
- Estimate effort and set priorities
- Track progress systematically

**📚 Documentation Complete**
- Maintain complete documentation at every stage
- Keep docs synchronized with code
- Document design decisions and trade-offs

### Why SDD?

SDD brings significant benefits to the project:

✅ **Better Architecture** - Thoughtful design before implementation
✅ **Fewer Bugs** - Clear specifications reduce misunderstandings
✅ **Easier Onboarding** - New contributors can understand the system quickly
✅ **Maintainable Code** - Well-documented code with clear intent
✅ **Predictable Delivery** - Task breakdown enables accurate estimation

### SDD in Practice

When contributing to GaiaRouter, follow this workflow:

```
1. Specification → 2. Design → 3. Tasks → 4. Implementation → 5. Testing → 6. Documentation
```

**For significant features:**

1. **Write a Specification** (`docs/development/sdd/specs/`)
   - What problem are you solving?
   - What are the requirements?
   - What is the API contract?

2. **Create a Design** (`docs/development/sdd/designs/`)
   - How will it integrate with existing architecture?
   - What modules will be affected?
   - What are the data flows?

3. **Break Down Tasks** (`docs/development/sdd/tasks/`)
   - What needs to be implemented?
   - What is the order and priority?
   - What are the dependencies?

4. **Implement** (`src/`)
   - Follow the design document
   - Write tests alongside code
   - Keep code clean and documented

5. **Document** (`docs/`)
   - Update user documentation
   - Update API documentation
   - Update CHANGELOG.md

**For small fixes or improvements:**
- SDD can be lightweight - a clear issue description may suffice
- For bug fixes, reproduction steps serve as specification
- For small refactors, code comments may serve as documentation

**📖 Learn more:** [SDD Documentation](docs/development/sdd/README.md)

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/GaiaRouter.git
   cd GaiaRouter
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original/GaiaRouter.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black isort mypy

# Configure environment
cp env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/init.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** and motivation
- **Proposed solution** or approach
- **Alternatives considered**
- **Additional context** or screenshots

### Code Contributions

1. **Pick an issue** or create one to discuss your changes
2. **Write code** following our coding standards
3. **Add tests** for your changes
4. **Update documentation** as needed
5. **Submit a pull request**

## Coding Standards

### Python (Backend)

We follow PEP 8 style guide with some modifications:

```python
# Use Black for formatting
black .

# Use isort for import sorting
isort .

# Use mypy for type checking
mypy src/
```

**Key conventions:**
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters
- Use async/await for I/O operations

**Example:**

```python
async def get_user(user_id: int) -> Optional[User]:
    """
    Retrieve a user by ID.

    Args:
        user_id: The unique identifier of the user

    Returns:
        User object if found, None otherwise
    """
    return await user_repository.get(user_id)
```

### TypeScript (Frontend)

We follow the Vue 3 Composition API style guide:

```typescript
// Use ESLint and Prettier
npm run lint
npm run format
```

**Key conventions:**
- Use TypeScript for all new code
- Use Composition API with `<script setup>`
- Define prop types and emits
- Use Pinia for state management

**Example:**

```typescript
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  userId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  update: [user: User]
}>()

const user = ref<User | null>(null)
</script>
```

### SQL and Migrations

- Use Alembic for database migrations
- Name migrations descriptively: `001_create_users_table.py`
- Always include both upgrade and downgrade functions
- Test migrations on a copy of production data

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process or tooling changes

**Examples:**

```
feat(api): add streaming support for chat completions

Implement Server-Sent Events (SSE) for streaming responses
from AI providers. This reduces latency and improves user
experience.

Closes #123
```

```
fix(auth): prevent API key leakage in error messages

Remove sensitive information from error responses to prevent
accidental exposure of API keys.

Fixes #456
```

## Pull Request Process

1. **Update documentation** to reflect your changes
2. **Add tests** for new functionality
3. **Run the test suite** and ensure all tests pass:
   ```bash
   pytest
   npm test
   ```
4. **Update CHANGELOG.md** with your changes
5. **Create a pull request** with:
   - Clear title following commit conventions
   - Description of changes and motivation
   - Link to related issues
   - Screenshots for UI changes
6. **Address review feedback** promptly
7. **Squash commits** if requested before merging

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No new warnings generated
- [ ] CHANGELOG.md updated
- [ ] Backwards compatibility maintained (or breaking changes documented)

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/gaiarouter

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_chat_completion
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test:unit

# Run e2e tests
npm run test:e2e
```

### Writing Tests

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Test edge cases and error conditions

**Example:**

```python
async def test_chat_completion_with_valid_api_key():
    """Test chat completion with valid API key succeeds"""
    response = await client.post(
        "/v1/chat/completions",
        json={"model": "gpt-3.5-turbo", "messages": [...]},
        headers={"Authorization": "Bearer valid-key"}
    )
    assert response.status_code == 200
    assert "choices" in response.json()
```

## Documentation

- Update relevant documentation for code changes
- Add docstrings to all public functions and classes
- Update API documentation for endpoint changes
- Add examples for new features
- Keep README.md up to date

### Documentation Structure

```
docs/
├── getting-started/     # Installation and setup guides
├── guides/              # User guides and tutorials
├── api/                 # API reference
├── architecture/        # Architecture documentation
└── development/         # Development guides
```

## Development Workflow

### Feature Development

1. Create feature branch from `main`
2. Implement feature with tests
3. Update documentation
4. Submit pull request
5. Address review feedback
6. Merge when approved

### Bug Fixes

1. Create bug fix branch from `main`
2. Write failing test reproducing the bug
3. Fix the bug
4. Verify test passes
5. Submit pull request

### Release Process

Releases are managed by maintainers:

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release tag
4. Build and publish packages
5. Announce release

## Questions?

- Check existing issues and discussions
- Read the documentation
- Ask in GitHub Discussions
- Contact maintainers

## Recognition

Contributors are recognized in:
- CHANGELOG.md for their contributions
- GitHub Contributors page
- Release notes for significant contributions

Thank you for contributing to GaiaRouter!
