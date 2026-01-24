# PRD: Email API Service - System Architecture & Infrastructure

## 1. Overview
This PRD outlines the technical architecture, database design, and infrastructure requirements for the Email API Service.

## 2. Architecture Overview

### 2.1 Layered Architecture
```
┌─────────────────────────────────┐
│   FastAPI Application           │
├─────────────────────────────────┤
│   API Endpoints (Routes)        │
├─────────────────────────────────┤
│   Services (Business Logic)     │
├─────────────────────────────────┤
│   Repositories (Data Access)    │
├─────────────────────────────────┤
│   Database (PostgreSQL)         │
└─────────────────────────────────┘
```

### 2.2 Directory Structure
```
app/
├── api/                 # API endpoints and dependencies
│   ├── v1/
│   │   ├── endpoints/  # Route handlers
│   │   └── router.py   # API router
│   └── deps.py         # Dependency injection
├── config/             # Configuration management
│   └── database/       # DB connection
├── core/               # Core utilities
│   ├── exceptions.py   # Custom exceptions
│   └── security.py     # JWT and encryption
├── models/             # SQLAlchemy models
├── repositories/       # Database access layer
├── services/           # Business logic layer
├── schemas/            # Pydantic schemas
├── middlewares/        # FastAPI middlewares
├── interfaces/         # Interface definitions
├── routes/             # Legacy routes (deprecated)
├── controllers/        # Controllers (if needed)
├── utils/              # Utility functions
├── static/             # Static files
├── templates/          # Email templates
├── dependencies.py     # App dependencies
├── init_database.py    # Database initialization
└── main.py             # Application entry point
```

## 3. Database Design

### 3.1 Tables
- **users**: User account information
- **roles**: Role definitions (admin, user)
- **permissions**: Permission definitions
- **role_permissions**: Role-Permission association
- **user_roles**: User-Role association
- **emails**: Sent email records
- **team**: Team/organization information (structure prepared, functionality not yet implemented)
- **user_team**: User-Team association with team-specific roles (owner, member)

### 3.2 Key Relationships
- User → many Roles (many-to-many) - Global roles (admin, user)
- Role → many Permissions (many-to-many)
- User → many Emails (one-to-many)
- User → many Teams (many-to-many) - Team membership
- User → many Owned Teams (one-to-many) - Teams owned by user
- Team → one Owner (many-to-one) - Team creator
- Team → many Members (many-to-many) - Team members

### 3.3 Indexing Strategy
- Primary keys on all tables
- Index on users.email (unique)
- Index on emails.user_id
- Index on emails.created_at
- Index on emails.status
- Composite indexes for common queries

## 4. Technology Stack

### 4.1 Backend
- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLAlchemy 2.0 (async with asyncpg)
- **Database**: PostgreSQL 14+ (async connection via asyncpg)
- **Async**: asyncio, asyncpg for production, aiosqlite for testing
- **Authentication**: JWT with PyJWT (jose)
- **Validation**: Pydantic v2
- **Password Hashing**: bcrypt

### 4.2 Email
- **SMTP Protocol**: RFC 5321
- **Providers**: Gmail, Outlook, Custom SMTP
- **Template Engine**: Jinja2
- **Queue**: Task queue (Future: Celery)

### 4.3 Testing
- **Framework**: pytest
- **Async Support**: pytest-asyncio
- **HTTP Client**: httpx
- **Coverage**: pytest-cov

### 4.4 Development
- **Package Manager**: pip with requirements.txt
- **Environment**: python-dotenv
- **Linting**: pylint, black
- **Type Checking**: mypy

## 5. API Structure

### 5.1 Version Management
- Current version: v1
- Base URL: `/api/v1/`
- Future: Support v2 for breaking changes

### 5.2 Response Format
```json
{
  "status": "success",
  "data": {},
  "error": null,
  "timestamp": "2024-01-23T19:30:00Z"
}
```

### 5.3 Pagination
- Default page size: 20
- Max page size: 100
- Query params: `page`, `page_size`

### 5.4 Error Handling
- HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Error response with message and code
- Validation errors with field details

## 6. Security Architecture

### 6.1 Authentication
- JWT tokens with HS256 algorithm (configurable)
- Access token: 30 minutes expiration (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)
- Refresh token: 7 days expiration (configurable via REFRESH_TOKEN_EXPIRE_DAYS)
- Token stored in Authorization header

### 6.2 Authorization
- Role-based access control (RBAC)
- Permission checking at endpoint level
- Admin-only endpoints protected
- User isolation enforced at service layer

### 6.3 Data Protection
- Passwords hashed with bcrypt (cost: 12)
- HTTPS/TLS for all connections
- SQL injection prevention via ORM
- CORS protection

## 7. Deployment Architecture

### 7.1 Development
- Local PostgreSQL (async connection via asyncpg)
- uvicorn server (reload enabled)
- Environment variables: `.env` file with standard PostgreSQL variables:
  - `PGHOST`: Database host (default: localhost)
  - `PGPORT`: Database port (default: 5432)
  - `PGUSER`: Database user
  - `PGPASSWORD`: Database password
  - `PGDATABASE`: Database name
  - `SECRET_KEY`: JWT secret key
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
  - `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)
  - `ALGORITHM`: JWT algorithm (default: HS256)
  - `CORS_ORIGINS`: Comma-separated list of allowed origins

### 7.2 Production (Vercel)
- Vercel deployment
- Vercel Postgres database
- Serverless functions
- Environment variables via Vercel dashboard

## 8. Performance Optimization

### 8.1 Database
- Async connection pooling (asyncpg)
- Query optimization
- Lazy loading relationships
- Batch operations for bulk inserts
- All database operations are async for better performance

### 8.2 API
- Response caching headers
- Compression (gzip)
- Pagination for large datasets
- Async request handling

### 8.3 Monitoring
- Logging at key points
- Error tracking
- Performance metrics
- Database query analysis

## 9. Non-Functional Requirements
- **Scalability**: 10,000+ concurrent users
- **Response Time**: < 500ms (p99)
- **Uptime**: 99.9%
- **Data Retention**: 1 year for emails, permanent for users
- **Backup**: Daily backups with 30-day retention
- **Recovery Time**: < 4 hours RTO

## 10. Compliance & Standards
- RESTful API design
- OpenAPI/Swagger documentation
- GDPR compliance (data export, deletion)
- PCI DSS for payment processing (future)

## 11. Configuration Management

### 11.1 Unified Configuration
- Configuration is managed through `app/config/config.py`
- Uses environment variables with sensible defaults
- Database URL is constructed from individual PostgreSQL variables
- Security settings (JWT, tokens) are configurable via environment variables
- No hardcoded credentials or connection strings

### 11.2 Configuration Structure
- `app_config`: Application metadata (name, version, description)
- `database_config`: PostgreSQL connection parameters
- `security_config`: JWT and authentication settings
- `cors_config`: CORS origins configuration

## 12. Future Enhancements
- Message queue (Celery/RabbitMQ)
- Caching layer (Redis)
- Microservices architecture
- GraphQL API
- WebSocket support for real-time updates
- Email delivery status webhooks
- Advanced analytics dashboard
- **Teams functionality**: Full implementation of team management (structure is prepared)