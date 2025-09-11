#!/bin/bash

# Robotics SOTA Development Environment Launcher
# This script starts both the backend and frontend in development mode

echo "🚀 Starting Robotics SOTA Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️ Node.js not found in current environment${NC}"
    echo "Checking if nodejs-env conda environment exists..."
    
    if conda env list | grep -q "nodejs-env"; then
        echo -e "${GREEN}✅ Found nodejs-env conda environment${NC}"
        NODE_ENV_EXISTS=true
    else
        echo -e "${RED}❌ Node.js is not installed${NC}"
        echo "Please install Node.js via conda environment:"
        echo "  conda create -n nodejs-env nodejs=18.20.5 -c conda-forge"
        echo "Or install via your package manager:"
        echo "  macOS: brew install node"
        echo "  Ubuntu: sudo apt install nodejs npm"
        exit 1
    fi
else
    NODE_ENV_EXISTS=false
fi

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python is not installed${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    echo -e "${GREEN}👋 Development environment stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${BLUE}🐍 Starting Python backend server...${NC}"
cd backend
$PYTHON_CMD -c "
import sys, os
sys.path.insert(0, '.')
os.chdir('$(pwd)')

from app import create_app, db

app = create_app()
print('🚀 Starting Robotics SOTA backend server...')
print('📊 Database:', app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'))

with app.app_context():
    db.create_all()
    print('✅ Database ready!')

print('🌐 Backend available at: http://127.0.0.1:8080')
print('📋 API endpoints:')
print('  - GET /api/labs - List all robotics labs')
print('  - GET /api/papers - List papers (when data available)')  
print('  - GET /api/trends - List research trends')
app.run(host='127.0.0.1', port=8080, debug=True)
" &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://127.0.0.1:8080/api/labs > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Backend may be starting up, waiting...${NC}"
    sleep 2
fi

# Start frontend
echo -e "${BLUE}⚛️ Starting React frontend...${NC}"
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    if [ "$NODE_ENV_EXISTS" = true ]; then
        echo -e "${BLUE}Using conda nodejs-env environment...${NC}"
        conda run -n nodejs-env npm install
    else
        npm install
    fi
fi

# Start frontend development server
echo -e "${GREEN}🌐 Starting frontend development server...${NC}"
if [ "$NODE_ENV_EXISTS" = true ]; then
    conda run -n nodejs-env npm start &
else
    npm start &
fi
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}🎉 Development environment started successfully!${NC}"
echo -e "${GREEN}📱 Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}🖥️  Backend:  http://127.0.0.1:8080${NC}"
echo -e "${GREEN}📊 API Docs: http://127.0.0.1:8080/api/labs${NC}"
echo
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for user to stop
wait