#!/bin/bash

# Deployment script for Moodle AI Assistant
# This script helps with quick deployment and updates

set -e

echo "🚀 Moodle AI Assistant Deployment Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your API keys before continuing.${NC}"
    read -p "Press enter when ready..."
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Menu
echo "Select deployment action:"
echo "1) Fresh installation (start services)"
echo "2) Update (rebuild and restart)"
echo "3) Stop services"
echo "4) View logs"
echo "5) Clean and reset (removes all data!)"
echo "6) Check status"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo -e "${GREEN}Starting fresh installation...${NC}"
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✓ Services started!${NC}"
        echo ""
        echo "Services:"
        echo "  - Backend: http://localhost:8000"
        echo "  - Qdrant: http://localhost:6333"
        echo ""
        echo "Next steps:"
        echo "  1. Install the Moodle plugin (Site Administration > Notifications)"
        echo "  2. Configure plugin settings (Site Administration > Plugins > Local plugins > AI Assistant)"
        echo "  3. Upload documents to knowledge base"
        ;;

    2)
        echo -e "${YELLOW}Updating services...${NC}"
        docker-compose down
        docker-compose build
        docker-compose up -d
        echo -e "${GREEN}✓ Services updated and restarted!${NC}"
        ;;

    3)
        echo -e "${YELLOW}Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;

    4)
        echo "Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;

    5)
        echo -e "${RED}⚠️  WARNING: This will delete all data including:${NC}"
        echo "  - Vector database (all indexed documents)"
        echo "  - Uploaded files"
        read -p "Are you sure? (type 'yes' to confirm): " confirm
        if [ "$confirm" = "yes" ]; then
            docker-compose down -v
            rm -rf qdrant_storage/
            echo -e "${GREEN}✓ All data cleaned${NC}"
        else
            echo "Cancelled"
        fi
        ;;

    6)
        echo "Service Status:"
        docker-compose ps
        echo ""
        echo "Testing endpoints..."

        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo -e "${GREEN}✓ Backend is running${NC}"
        else
            echo -e "${RED}❌ Backend is not responding${NC}"
        fi

        if curl -s http://localhost:6333/health > /dev/null; then
            echo -e "${GREEN}✓ Qdrant is running${NC}"
        else
            echo -e "${RED}❌ Qdrant is not responding${NC}"
        fi
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "Done! 🎉"
