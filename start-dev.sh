#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"

BACKEND_PID=""
FRONTEND_PID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "� Starting Robotics SOTA Development Environment..."

cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"

    if [[ -n "${FRONTEND_PID:-}" ]] && ps -p "${FRONTEND_PID}" > /dev/null 2>&1; then
        kill "${FRONTEND_PID}" 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi

    if [[ -n "${BACKEND_PID:-}" ]] && ps -p "${BACKEND_PID}" > /dev/null 2>&1; then
        kill "${BACKEND_PID}" 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi

    echo -e "${GREEN}👋 Development environment stopped${NC}"
    exit 0
}

trap cleanup INT TERM

echo -e "${BLUE}� Checking prerequisites...${NC}"

USE_CONDA_NODE=false
if ! command -v node >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Node.js not found in current PATH${NC}"
    if command -v conda >/dev/null 2>&1 && conda env list | grep -q "nodejs-env"; then
        echo -e "${GREEN}✅ Using nodejs-env conda environment for Node.js${NC}"
        USE_CONDA_NODE=true
    else
        echo -e "${RED}❌ Node.js is not installed${NC}"
        echo "Install it via conda or your package manager, e.g.:"
        echo "  conda create -n nodejs-env nodejs=18.20.5 -c conda-forge"
        echo "  brew install node"
        echo "  sudo apt install nodejs npm"
        exit 1
    fi
fi

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo -e "${RED}❌ Python is not installed${NC}"
    exit 1
fi

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

echo -e "${BLUE}🐍 Starting Python backend via run_dev.py...${NC}"
pushd "${BACKEND_DIR}" >/dev/null
"${PYTHON_CMD}" run_dev.py --host 127.0.0.1 --port 8080 --debug &
BACKEND_PID=$!
popd >/dev/null

echo -e "${BLUE}⏳ Waiting for backend readiness...${NC}"
BACKEND_READY=false
for attempt in {1..10}; do
    if curl -sSf http://127.0.0.1:8080/api/labs >/dev/null 2>&1; then
        BACKEND_READY=true
        break
    fi
    sleep 1
done

if [[ "${BACKEND_READY}" == true ]]; then
    echo -e "${GREEN}✅ Backend is responding at http://127.0.0.1:8080${NC}"
else
    echo -e "${YELLOW}⚠️ Backend is still starting; continuing anyway.${NC}"
fi

echo -e "${BLUE}⚛️ Starting Next.js frontend...${NC}"
pushd "${FRONTEND_DIR}" >/dev/null

if [[ ! -d "node_modules" ]]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    if [[ "${USE_CONDA_NODE}" == true ]]; then
        conda run -n nodejs-env npm install
    else
        npm install
    fi
fi

if [[ "${USE_CONDA_NODE}" == true ]]; then
    conda run -n nodejs-env npm run dev &
else
    npm run dev &
fi
FRONTEND_PID=$!
popd >/dev/null

echo -e "${GREEN}🎉 Development environment started successfully!${NC}"
echo -e "${GREEN}📱 Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}🖥️  Backend:  http://127.0.0.1:8080${NC}"
echo -e "${GREEN}📊 API Docs: http://127.0.0.1:8080/api/labs${NC}"
echo
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

wait