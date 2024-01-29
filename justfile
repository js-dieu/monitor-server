set dotenv-load := true
python_interpreter := trim(env("PYTHON_INTERPRETER", ""))
JUST_DIRECTORY := justfile_directory()
ALEMBIC_CONFIG_PATH := join( justfile_directory(), env("ALEMBIC_ROOT"), "alembic.ini")
COVERAGE_REPORT_PATH := join(justfile_directory(), "htmlcov")
TEST_DIRECTORY := join(justfile_directory(), env("PROJECT_SLUG"), "tests")

export ALEMBIC_CONFIG := ALEMBIC_CONFIG_PATH


default:
    @just --list

# Display global information about the project
info:
    @echo "\033[1mProject ${PROJECT_NAME} \033[0m"
    @if [ -z {{python_interpreter}} ]; then \
      echo "\033[33mNo specific interpreter used\033[0m"; \
    else \
      echo "\033[34mFrom interpreter\033[0m: \033[32m{{python_interpreter}}\033[0m"; \
    fi
    @echo "\033[34mALEMBIC_CONFIG\033[0m: \033[32m{{ALEMBIC_CONFIG}}\033[0m"
    @poetry env info
    @echo
    @echo "\033[1mServices \033[0m"
    @docker compose ps

# Prepare the whole project for development
setup: install start-services migrate-services
    @poetry run pre-commit install
    @echo
    @echo "Setup completed"

# Perform migrations on a per service (usually db is the one done here)
migrate-services: db-migrate


# Create a new virtual environment and Install your project's dependencies in it. Possible values for level: dev | prod
install level="dev":
    @if [ "{{ level }}" != "dev" -a "{{ level }}" != "prod" ]; then \
      echo "Invalid value given for parameter 'level'."; \
      echo "Got '{{ level }}', expected 'dev' or 'prod'."; \
      false; \
    fi
    @if [ "${PYTHON_INTERPRETER:=""}" != "" ]; then poetry env use ${PYTHON_INTERPRETER}; fi
    @poetry install {{ if level == "prod" { "--only-root" } else { "--with dev" } }}

# Remove all generated files such as builds, coverage reports, mypy caches ...
clean:
    @find {{JUST_DIRECTORY}} -type d -name ".pytest_cache" -exec rm -rf {} \; 2>/dev/null || true
    @find {{JUST_DIRECTORY}} -type d -name ".mypy_cache" -exec rm -rf {} \; 2>/dev/null || true
    @find {{JUST_DIRECTORY}} -name ".__pycache__" -exec rm -rf {} \; 2>/dev/null || true
    @find {{JUST_DIRECTORY}} -name ".ruff_cache" -exec rm -rf {} \; 2>/dev/null || true
    @for suffix in "pyc pyo"; do find {{JUST_DIRECTORY}} -name "*.${suffix}" -exec rm -f {} \; 2>/dev/null || true ; done
    @rm -rf {{COVERAGE_REPORT_PATH}} || true
    @rm -rf .coverage || true

# Shutdown the environment. By default, do not remove the environment. Possible values for method: keep | remove
teardown method="keep":
    @if [ "{{ method }}" != "keep" -a "{{ method }}" != "remove" ]; then \
      echo "Invalid value given for parameter 'method'."; \
      echo "Got '{{ method }}', expected 'keep' or 'remove'."; \
      false; \
    fi
    @if [ "{{ method }}" == "remove" ]; then rm -rf $(poetry env info -p); fi
    @docker compose {{ if method == "keep" { "stop" } else { "down" } }}

# Launch services in detached mode and for them to be ready
start-services:
    @docker compose up --wait -d

# List launched containers
list-services:
    @docker ps -f name=${PROJECT_NAME}

# Output and follow a service log. CONTAINER is to be retrieved from `just containers`.
logs CONTAINER:
    @docker logs {{ CONTAINER }} --follow

# Stop services
stop-services:
    @docker compose stop

# Create a new database migration steps
db-add-migration-step message:
    @poetry run alembic revision -m "{{ message }}"

# Performs database setup (up to head)
db-migrate:
    @echo "Preparing database for ${PROJECT_NAME}"
    @echo "  ALEMBIC_CONFIG => ${ALEMBIC_CONFIG}"
    @poetry run alembic upgrade head

db-test-migration:
    @echo "Testing database migration for ${PROJECT_NAME}"
    @echo "  ALEMBIC_CONFIG => ${ALEMBIC_CONFIG}"
    @poetry run alembic upgrade head --sql

# Prints out history of revisions applied to the database
db-history:
    @poetry run alembic history

# Find a string in python files
findpy PATTERN:
    @echo Searching for pattern [{{ PATTERN }}] in Python files
    @find . -name "*.py" | xargs grep --color {{ PATTERN }}

# Run linter in preview mode
lint-check:
    @poetry run ruff check ${PROJECT_SLUG} --preview

# Run linter and fix safe errors
lint-fix:
    @poetry run ruff check ${PROJECT_SLUG} --fix --preview

# Run typecheck
typecheck:
    @poetry run mypy --non-interactive --install-types ${PROJECT_SLUG}

# Run formatter and fix safe issues.
format:
    @poetry run ruff format ${PROJECT_SLUG} --preview

# Launch the service locally
serve:
    @poetry run uvicorn service_auth.entry_points.web.main:app --reload

# Run unit test only
unittest dirs=".":
    @cd {{ TEST_DIRECTORY }} && poetry run pytest -vv -m "not int" {{ dirs }}

# Run integration test only. This launches required services if not running.
inttest dirs=".": start-services db-migrate
    @cd {{ TEST_DIRECTORY }} && poetry run pytest -vv -m int {{ dirs }}

# Run all tests. This launches required services if not running.
test dirs=".": start-services db-migrate
    @cd {{ TEST_DIRECTORY }} && poetry run pytest -vv {{ dirs }}

# Run all tests with coverage. Default coverage report is html
coverage report_type="html": start-services
    @if [ "{{ report_type }}" != "text" -a "{{ report_type }}" != "html" ]; then \
      echo "Invalid value given for parameter 'report_type'."; \
      echo "Got '{{ report_type }}', expected 'text' or 'html'."; \
      false; \
    fi
    @poetry run pytest --cov --cov-report={{ report_type }}
