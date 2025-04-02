#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      FastAPI Boilerplate Build Script      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Docker
if ! command_exists docker; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check for Docker Compose
if ! command_exists docker-compose; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}Setting up project environment...${NC}"

# Create data directory if it doesn't exist
if [ ! -d "./data" ]; then
    echo -e "${YELLOW}Creating data directory...${NC}"
    mkdir -p ./data/mongodb_data
    echo -e "${GREEN}✓ Data directory created${NC}"
else
    echo -e "${GREEN}✓ Data directory exists${NC}"
fi

# Check if .env file exists, if not copy from example
if [ ! -f "./.env" ]; then
    if [ -f "./.env.example" ]; then
        echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file. Please review and update the settings.${NC}"
    else
        echo -e "${RED}Error: .env.example file not found. Cannot create .env file.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check if dev-network exists, create if it doesn't
if ! docker network ls | grep -q "dev-network"; then
    echo -e "${YELLOW}Creating dev-network...${NC}"
    docker network create dev-network
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Created dev-network${NC}"
    else
        echo -e "${RED}Error: Failed to create dev-network${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ dev-network already exists${NC}"
fi

# Check if Python dependencies are installed in the local environment
echo -e "${YELLOW}Checking Python dependencies...${NC}"
if [ -d ".venv" ] || [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}Tip: You might want to create a virtual environment:${NC}"
    echo -e "  python -m venv .venv"
    echo -e "  source .venv/bin/activate"
    echo -e "  pip install -r requirements.txt or uv pip install"
fi

# Build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
    
    echo -e "\n${GREEN}Setup complete!${NC}"
    echo -e "${YELLOW}To start the application:${NC}"
    echo -e "  docker-compose up -d"
    echo -e "${YELLOW}To stop the application:${NC}"
    echo -e "  docker-compose down"
    echo -e "${YELLOW}To view logs:${NC}"
    echo -e "  docker-compose logs -f"
    
    echo -e "\n${BLUE}Your FastAPI application will be available at:${NC}"
    echo -e "  http://localhost:8002"
    echo -e "${BLUE}MongoDB will be available at:${NC}"
    echo -e "  mongodb://localhost:27017"
else
    echo -e "${RED}Error: Failed to build Docker images${NC}"
    exit 1
fi
