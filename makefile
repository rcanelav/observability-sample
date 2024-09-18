# Variables
PYTHON ?= python3
PORT ?= 7000
OTEL_LOGGING_ENABLED = true
LOGS_EXPORTER = otlp,console
COMPOSE_FILE = docker-compose.yaml

# Targets
.PHONY: all install bootstrap run docker-up docker-down clean

# Default target when running 'make' without a target
all: docker-up install bootstrap run

# Install OpenTelemetry libraries
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install opentelemetry-distro opentelemetry-exporter-otlp
	$(PYTHON) -m pip install opentelemetry-distro[otlp] opentelemetry-instrumentation

# Run OpenTelemetry bootstrap for auto-instrumentation
bootstrap:
	$(PYTHON) -m opentelemetry.bootstrap -a install

# Run the Flask app with OpenTelemetry instrumentation
run:
	@echo "Enabling OpenTelemetry Python Logging Auto-Instrumentation"
	export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=$(OTEL_LOGGING_ENABLED) && \
	cd src && \
	opentelemetry-instrument \
		--service_name roll_dice \
		--logs_exporter=$(LOGS_EXPORTER) \
		flask run -p $(PORT)

# Start Docker Compose services
docker-up:
	docker-compose -f $(COMPOSE_FILE) up -d

# Stop Docker Compose services
docker-down:
	docker-compose -f $(COMPOSE_FILE) down

# Clean the project (optional, modify as needed)
clean:
	rm -rf __pycache__ .pytest_cache
	rm -rf .opentelemetry-instrumentation
