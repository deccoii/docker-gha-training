# Docker Final Exam (ESGI B3)

## Docker Image Creation

### 1. Fork the repo
✅ Repository forked and cloned locally

### 2. Dockerfile Creation

#### Requirements Analysis
- ✅ **Latest Python version**: Using `python:3.13-slim` (Python 3.13.5 - latest stable)
- ✅ **Smallest tag possible**: `-slim` variant reduces image size by ~70% vs standard
- ✅ **Optimized image**: Multi-layer optimization and build cache strategies
- ✅ **Security best practices**: Non-root user, minimal dependencies, health checks

#### Dockerfile Breakdown

**Base Image Selection:**
```dockerfile
FROM python:3.13-slim
```
- Python 3.13.5: Latest stable version (Released June 11, 2025)
- `slim` tag: Minimal Debian-based image (~45MB vs ~165MB for standard)

**Environment Optimization:**
```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app
```
- `PYTHONDONTWRITEBYTECODE=1`: Prevents .pyc file generation
- `PYTHONUNBUFFERED=1`: Ensures real-time log output
- `PIP_NO_CACHE_DIR=1`: Reduces image size by not caching pip downloads
- `PIP_DISABLE_PIP_VERSION_CHECK=1`: Speeds up pip operations

**Security Measures:**
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
# ... later in file ...
RUN chown -R appuser:appuser /app
USER appuser
```
- Creates and switches to non-root user
- Follows principle of least privilege

**Build Optimization Strategies:**
1. **Layer Caching**: Dependencies copied before application code
2. **Single RUN Commands**: Reduces layer count
3. **Cleanup**: Removes package lists and temporary files
4. **.dockerignore**: Excludes unnecessary files from build context

**Health Check Implementation:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/books')" || exit 1
```
- Uses Python's built-in urllib (no external dependencies)
- Tests actual API endpoint functionality

#### Supporting Files Created

**`.dockerignore` File:**
- Excludes development files, caches, and documentation
- Reduces build context size significantly
- Improves build performance

**Application Modification:**
- Modified `app/main.py` to bind to `0.0.0.0:5000`
- Enables external access to containerized application

### 3. Build Docker Image with Tag

**Build Command:**
```bash
docker build -t myapp:1 .
```

**Build Output:**
![Docker Build](/images/build.png)

### 4. Run the Container

**Run Command:**
```bash
docker run -d -p 8080:5000 --name myapp_container myapp:1
```

![Container Running](/images/running.png)

### 5. Check Container Status and Accessibility

**Status Check Command**
```bash
docker ps
```
**Output:**
![Docker ps Output](/images/status_check.png)

## Docker Compose

### 1. Create "docker-compose.yaml"

#### Docker Compose File Creation

**File:** `docker-compose.yaml`
```yaml
version: '3.8'

services:
  myapp:
    image: myapp:1
    container_name: myapp_compose_container
    ports:
      - "8080:5000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/books')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

#### Configuration Breakdown

**Service Definition:**
- `services:` - Defines all services in this compose file
- `myapp:` - Service name as required

**Image and Container:**
- `image: myapp:1` - Uses the Docker image built in step 3
- `container_name: myapp_compose_container` - Custom container name for identification

**Port Mapping:**
- `ports: - "8080:5000"` - Maps host port 8080 to container port 5000

**Restart Policy:**
- `restart: unless-stopped` - Automatically restarts if crashes (unless manually stopped)

**Health Check:**
- Tests API endpoint every 30 seconds
- Helps monitor service health
- Automatic restart if health checks fail

### 2. PostgreSQL Database Setup

#### PostgreSQL Configuration

**Image Selection:**
```yaml
image: postgres:17
```
- PostgreSQL 17: Latest stable version (released September 26, 2024)
- Avoids `latest` tag to prevent automatic upgrades
- Production-ready with all latest features

**Security Implementation - Docker Secrets:**
```yaml
secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
```
- Password stored in separate file, not environment variables
- File permissions set to 600 (owner read-only)
- Excluded from version control via `.gitignore`

**Data Persistence:**
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```
- Named volume for PostgreSQL data persistence
- Data survives container restarts and recreations
- Automatic backup and restore capability

**Database Configuration:**
```yaml
environment:
  POSTGRES_DB: myapp_db
  POSTGRES_USER: myapp_user
  POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

### 3. Database Readiness and Service Dependencies

#### Service Dependency Configuration

**Enhanced depends_on with Health Check Condition:**
```yaml
myapp:
  depends_on:
    postgres:
      condition: service_healthy
```

**Why This Works:**
- `depends_on` with `condition: service_healthy` waits for PostgreSQL health check to pass
- PostgreSQL health check verifies database accepts connections: `pg_isready -U myapp_user -d myapp_db`
- Application container only starts after database is confirmed ready
- Prevents connection errors and application crashes


### 4. Start Docker Compose Stack

**Start Command:**
```bash
docker-compose up -d
```
**Command Output:**
![Docker Compose up](/images/docker_compose.png)

## GitHub Actions CI/CD Implementation

### Overview

This project implements two GitHub Actions workflows following DevOps best practices:

1. **`docker-build-push.yml`** - Builds and pushes Docker images to GitHub Container Registry
2. **`test.yml`** - Runs comprehensive testing and security scans

### 1. Docker Build and Push Workflow

#### Purpose
Builds and pushes Docker images to GitHub Container Registry (ghcr.io) only when code is pushed to the `main` branch.

#### Key Features

**Security Best Practices:**
- ✅ Uses `GITHUB_TOKEN` for authentication (no manual secrets needed)
- ✅ Implements proper permissions (`contents: read`, `packages: write`)
- ✅ Only pushes images on main branch, not on pull requests
- ✅ Includes vulnerability scanning with Trivy

**Performance Optimization:**
- ✅ Docker Buildx for advanced building features
- ✅ Multi-platform builds (linux/amd64, linux/arm64)
- ✅ GitHub Actions cache for Docker layers (`cache-from: type=gha`)
- ✅ Cache maximization with `cache-to: type=gha,mode=max`

**Image Tagging Strategy:**
- ✅ Branch-based tags for development
- ✅ SHA-based tags for traceability
- ✅ `latest` tag only for main branch
- ✅ PR-specific tags for pull requests

**Security Scanning:**
- ✅ Trivy vulnerability scanner integration
- ✅ SARIF format output for GitHub Security tab
- ✅ Automated security reporting

#### Workflow Triggers
```yaml
on:
  push:
    branches: [main]      # Builds and pushes on main
  pull_request:
    branches: [main]      # Only builds on PRs (no push)
```

### 2. Build and Test Workflow

#### Purpose
Comprehensive testing pipeline that validates code quality, functionality, and security.

#### Key Features

**Multi-Python Version Testing:**
- ✅ Matrix strategy testing Python 3.10.x through 3.13.x
- ✅ Ensures compatibility across Python versions
- ✅ Parallel execution for faster feedback

**Comprehensive Testing Pipeline:**
Three distinct job types:

1. **Unit Testing (`test` job)**
   - Python syntax validation with flake8
   - Unit tests with pytest
   - Code coverage reporting
   - Codecov integration

2. **Docker Integration Testing (`docker-test` job)**
   - Builds Docker image
   - Tests container functionality
   - API endpoint validation
   - Dependency on unit tests passing

**Performance Optimizations:**
- ✅ Pip cache for faster dependency installation
- ✅ Docker layer caching
- ✅ Parallel job execution
- ✅ Strategic job dependencies

**Quality Gates:**
- ✅ Code linting enforcement
- ✅ Test coverage tracking
- ✅ Docker functionality validation
- ✅ Security vulnerability detection

### 3. Test Coverage Implementation

The project includes comprehensive unit tests (`app/test_main.py`) covering:
- ✅ All CRUD operations (Create, Read, Update, Delete)
- ✅ Error handling scenarios
- ✅ API endpoint validation
- ✅ Integration testing workflows

#### Test File Structure:
```python
class TestBooksAPI:
    def test_get_all_books(self, client)
    def test_get_book_by_id(self, client)
    def test_get_book_not_found(self, client)
    def test_add_new_book(self, client, sample_book)
    def test_add_book_missing_data(self, client)
    def test_update_book(self, client)
    def test_update_book_not_found(self, client)
    def test_delete_book(self, client)
    def test_delete_book_not_found(self, client)
    def test_api_integration(self, client, sample_book)
```

### 4. Usage Instructions

#### Initial Setup
1. Push code to `main` branch to trigger Docker image build
2. Create pull requests to trigger testing workflow
3. View results in GitHub Actions tab

#### Registry Access
Images are available at: `ghcr.io/[username]/[repository]:tag`

Example:
```bash
docker pull ghcr.io/yourusername/docker-gha-training:latest
```

#### Local Testing
```bash
# Install test dependencies
pip install pytest pytest-cov flask-testing requests

# Run tests
pytest app/ -v --cov=app
```

**Test Outputs**
![Test outputs](/images/tests.png)

