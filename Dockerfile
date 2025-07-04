# Use Python 3.9 with Alpine Linux 3.13 as the base image
# Alpine is a lightweight Linux distribution, perfect for containers
FROM python:3.9-alpine3.13

# Add metadata label for maintainer information
LABEL maintainer="shubhamsre1997@gmail.com"

# Set environment variable to ensure Python output is sent straight to terminal
# without being buffered (useful for logging in containers)
ENV PYTHONUNBUFFERED=1

# Copy dependency files to a temporary location in the container
# These files will be used during the build process
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy the application code to the /app directory in the container
COPY ./app /app

# Set the working directory for subsequent commands
WORKDIR /app

# Expose port 8000 for the application to listen on
EXPOSE 8000

# Define a build argument with default value 'false'
# This allows us to conditionally install development dependencies
ARG DEV=false

# Multi-stage RUN command to set up the Python environment and install dependencies
RUN python -m venv /py && \
    # Upgrade pip to the latest version
    /py/bin/pip install --upgrade pip && \
    # Install PostgreSQL client tools (psql, pg_dump, etc.)
    apk add --update --no-cache postgresql-client jpeg-dev && \
    # Install build dependencies temporarily for compiling Python packages
    # These will be removed later to keep the image size small
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev zlib zlib-dev && \
    # Install production dependencies from requirements.txt
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Conditionally install development dependencies if DEV=true
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    # Clean up temporary files to reduce image size
    rm -rf /tmp && \
    # Remove build dependencies to keep the final image lean
    apk del .tmp-build-deps && \
    # Create a non-root user for security best practices
    # This user will run the application instead of root
    # Create a non-root user 'django-user' for security
    # --disabled-password: No password login allowed
    # --no-create-home: Don't create a home directory
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    # Create directories for storing media files uploaded by users
    mkdir -p /vol/web/media && \
    # Create directory for collecting static files (CSS, JS, images)
    mkdir -p /vol/web/static && \
    # Change ownership of /vol directory and contents to django-user
    chown -R django-user:django-user /vol && \
    # Set directory permissions to 755 (rwxr-xr-x)
    # Owner can read/write/execute, others can read/execute
    chmod -R 755 /vol



    

# Add the Python virtual environment to the system PATH
# This ensures that 'python' and 'pip' commands use the virtual environment
ENV PATH="/py/bin:$PATH"

# Switch to the non-root user for security
USER django-user

