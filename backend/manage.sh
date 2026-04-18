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
        if [ "$#" -ne 4 ]; then
            echo "Usage: ./manage.sh create-admin <username> <email> <password>"
            exit 1
        fi
        echo "Creating Admin User: $2..."
        # Using the Flask CLI command we integrated earlier
        uv run flask --app app:create_app create-admin "$2" "$3" "$4"
        ;;
    # worker)
    #     echo "Starting Celery Worker..."
    #     uv run python worker.py
    #     ;;
    # beat)
    #     echo "Starting Celery Beat..."
    #     uv run python beat.py
    #     ;;
    *)
        echo "Usage: ./manage.sh {run|create-admin}"
        echo "  run: Starts the server and redirects output to output.txt"
        echo "  create-admin <username> <email> <password>: Creates a new admin user"
        ;;
esac
