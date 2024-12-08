#!/bin/bash

# Run Flake8 using Docker Compose
docker-compose run --rm app sh -c "flake8"
