# Getting Started with GaiaRouter

Welcome to GaiaRouter! This guide will help you set up and run GaiaRouter on your local machine.

## What is GaiaRouter?

GaiaRouter is an AI model routing service that provides a unified API interface to access multiple AI model providers (OpenAI, Anthropic, Google, OpenRouter). It supports streaming responses and includes complete backend management functionality.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+**
- **MySQL 8.0+** or **PostgreSQL 13+**
- **pip** (Python package manager)
- **npm** (Node package manager)

## Quick Start

Follow these steps to get GaiaRouter up and running:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd GaiaRouter
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp env.example .env
# Edit .env file with your database credentials and API keys

# Initialize the database and create admin user
python scripts/init.py

# Start the backend service
python -m uvicorn src.gaiarouter.main:app --reload
```

The backend API will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at http://localhost:3000

### 4. Access the Application

- **Admin Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Default Admin Credentials**:
  - Username: `admin`
  - Password: `admin123`
  - ⚠️ **Important**: Change the default password after first login!

## Next Steps

- [Configuration Guide](configuration.md) - Learn how to configure environment variables
- [Installation Guide](installation.md) - Detailed installation instructions
- [User Guide](../guides/user-guide/user-guide.md) - Learn how to use GaiaRouter
- [API Documentation](../api/api-documentation.md) - Explore the REST API

## Getting Help

- Check the [FAQ](../guides/faq.md)
- Read the [Troubleshooting Guide](../guides/troubleshooting.md)
- Open an issue on GitHub

## Docker Quick Start

If you prefer using Docker:

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Create admin user
docker-compose exec api python scripts/create_admin_user.py
```

See the [Docker Deployment Guide](../deployment/docker-deployment.md) for more details.
