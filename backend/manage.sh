#!/bin/bash

# Hospital Management System - Management Script

# Navigate to the backend directory
cd "$(dirname "$0")"

case "$1" in
    run)
        echo "Starting Flask Server (logging to output.txt)..."
        # Run in foreground but redirect all output to output.txt
        uv run python run.py > output.txt 2>&1
        ;;
    create-admin)
        if [ "$#" -lt 6 ]; then
            echo "Usage: ./manage.sh create-admin <username> <email> <password> <full_name> <phone_number> [address] [pincode]"
            exit 1
        fi
        echo "Creating Admin User: $2..."
        # Shift command name and pass all remaining arguments
        shift
        uv run flask --app app:create_app create-admin "$@"
        ;;
    worker)
        echo "Starting Celery Worker..."
        uv run celery -A worker.celery worker --loglevel=info
        ;;
    beat)
        echo "Starting Celery Beat..."
        uv run celery -A worker.celery beat --loglevel=info
        ;;
    shell)
        echo "Starting Flask Shell..."
        uv run flask --app app:create_app shell
        ;;
    *)
        echo "Usage: ./manage.sh {run|create-admin|worker|beat|shell}"
        echo "  run: Starts the server and redirects output to output.txt"
        echo "  create-admin <username> <email> <password> <full_name> <phone_number> [address] [pincode]: Creates a new admin user"
        echo "  worker: Starts the Celery worker"
        echo "  beat: Starts the Celery beat scheduler"
        echo "  shell: Starts the Flask interactive shell"
        ;;
esac
