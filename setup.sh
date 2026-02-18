#!/bin/bash

# Setup script for Lead Platform MVP
# This script helps with initial setup and common tasks

set -e

echo "🚀 Lead Platform MVP - Setup Script"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your credentials."
    echo ""
    echo "Required configurations:"
    echo "  - WHATSAPP_API_TOKEN"
    echo "  - WHATSAPP_PHONE_NUMBER_ID"
    echo "  - OPENAI_API_KEY"
    echo "  - WEBHOOK_BASE_URL"
    echo ""
    read -p "Press Enter after you've configured .env..."
fi

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo "✅ Docker is installed"
}

# Function to check if Docker Compose is installed
check_docker_compose() {
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo "✅ Docker Compose is installed"
}

# Main menu
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1) Start the platform (first time)"
    echo "2) Stop the platform"
    echo "3) Restart the platform"
    echo "4) View logs"
    echo "5) Create a test landing page"
    echo "6) Backup database"
    echo "7) Run tests"
    echo "8) Update application"
    echo "9) Exit"
    echo ""
    read -p "Enter your choice [1-9]: " choice
    
    case $choice in
        1) start_platform ;;
        2) stop_platform ;;
        3) restart_platform ;;
        4) view_logs ;;
        5) create_landing_page ;;
        6) backup_database ;;
        7) run_tests ;;
        8) update_application ;;
        9) exit 0 ;;
        *) echo "Invalid option"; show_menu ;;
    esac
}

start_platform() {
    echo ""
    echo "🚀 Starting the platform..."
    check_docker
    check_docker_compose
    
    docker compose up -d
    
    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "📊 Running database migrations..."
    docker compose exec backend flask db upgrade || true
    
    echo ""
    echo "✅ Platform started successfully!"
    echo ""
    echo "Access:"
    echo "  - API: http://localhost:5000"
    echo "  - Admin: http://localhost:5000/admin"
    echo "  - Health: http://localhost:5000/health"
    echo ""
    
    show_menu
}

stop_platform() {
    echo ""
    echo "🛑 Stopping the platform..."
    docker compose down
    echo "✅ Platform stopped"
    show_menu
}

restart_platform() {
    echo ""
    echo "🔄 Restarting the platform..."
    docker compose restart
    echo "✅ Platform restarted"
    show_menu
}

view_logs() {
    echo ""
    echo "📋 Viewing logs (Ctrl+C to exit)..."
    echo ""
    docker compose logs -f
}

create_landing_page() {
    echo ""
    echo "📄 Create a Test Landing Page"
    echo "=============================="
    
    read -p "Enter slug (URL-friendly name, e.g., 'jardim-paulista'): " slug
    read -p "Enter title: " title
    read -p "Enter neighborhood: " neighborhood
    
    echo ""
    echo "Creating landing page..."
    
    curl -X POST http://localhost:5000/api/landing-pages \
      -H "Content-Type: application/json" \
      -d "{
        \"slug\": \"$slug\",
        \"title\": \"$title\",
        \"neighborhood\": \"$neighborhood\",
        \"hero_title\": \"$title\",
        \"hero_subtitle\": \"Entre em contato e receba um orçamento personalizado!\",
        \"cta_text\": \"Solicitar Orçamento\"
      }" || echo "Error creating landing page. Make sure the platform is running."
    
    echo ""
    echo "✅ Landing page created!"
    echo "Access: http://localhost:5000/landing/$slug"
    echo ""
    
    show_menu
}

backup_database() {
    echo ""
    echo "💾 Creating database backup..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="backup_$timestamp.sql"
    
    docker compose exec -T db pg_dump -U leads_user leads_platform > "$backup_file"
    
    echo "✅ Backup created: $backup_file"
    echo ""
    
    show_menu
}

run_tests() {
    echo ""
    echo "🧪 Running tests..."
    
    docker compose exec backend pytest -v
    
    echo ""
    show_menu
}

update_application() {
    echo ""
    echo "🔄 Updating application..."
    
    echo "Pulling latest changes..."
    git pull origin main || echo "Warning: Could not pull from git"
    
    echo "Rebuilding containers..."
    docker compose build
    
    echo "Restarting services..."
    docker compose down
    docker compose up -d
    
    echo "Running migrations..."
    sleep 10
    docker compose exec backend flask db upgrade || true
    
    echo "✅ Application updated!"
    echo ""
    
    show_menu
}

# Start the script
check_docker
check_docker_compose
show_menu
