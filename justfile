# Justfile for Task Management Backend
# Usage: just <command>

# Install dependencies
install:
    pip install -r requirements.txt

# Install development dependencies
install-dev:
    pip install -r requirements-dev.txt

# Run the application
run:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
    pytest tests/ -v --cov=app --cov-report=term-missing

# Run tests with coverage report
test-cov:
    pytest tests/ --cov=app --cov-report=html

# Format code
format:
    black app/ tests/
    isort app/ tests/

# Lint code
lint:
    flake8 app/ tests/
    black --check app/ tests/
    isort --check-only app/ tests/

# Type checking
type-check:
    mypy app/

# Database migrations
db-migrate:
    alembic revision --autogenerate -m "{{message}}"

db-upgrade:
    alembic upgrade head

db-downgrade:
    alembic downgrade -1

# Seed database
seed:
    python scripts/seed.py

# Setup database
setup-db:
    python scripts/setup_db.py

# Docker commands
docker-build:
    docker build -t task-management-backend .

docker-run:
    docker-compose up -d

docker-stop:
    docker-compose down

docker-logs:
    docker-compose logs -f

docker-db-setup:
    docker-compose exec web python scripts/setup_db.py

# Docker database seed
docker-db-seed:
    docker-compose exec web python scripts/seed.py

# Development setup
dev-setup: install-dev setup-db seed
    @echo "Development environment setup complete!"

# Clean up
clean:
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name "*.egg-info" -delete
    rm -rf .coverage htmlcov/

# Show help
default:
    @just --list
