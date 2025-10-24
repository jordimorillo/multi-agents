#!/bin/bash
# Setup script para Multi-Agent System con LangChain + LangGraph

set -e

echo "🚀 Multi-Agent System Setup"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}❌ Python 3.9+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✅ pip upgraded${NC}"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Configuring environment..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# LLM Configuration
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Linear.app Integration
LINEAR_API_KEY=lin_api_your-key-here
LINEAR_TEAM_ID=TEAM-123

# GitHub Integration
GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO=owner/repo-name

# LangSmith (Optional - for observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_your-key-here
LANGCHAIN_PROJECT=multi-agents

# Agent Configuration
DEFAULT_MODEL=gpt-4-turbo-preview
DEFAULT_TEMPERATURE=0.2
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env with your API keys${NC}"
else
    echo -e "${YELLOW}⚠️  .env already exists${NC}"
fi

# Create directory structure
echo ""
echo "📁 Creating directory structure..."
mkdir -p .rag_store
mkdir -p logs
mkdir -p checkpoints
mkdir -p examples/outputs
echo -e "${GREEN}✅ Directories created${NC}"

# Initialize RAG knowledge base
echo ""
echo "🧠 Initializing RAG knowledge base..."
if [ -f "scripts/init_rag.py" ]; then
    python scripts/init_rag.py
    echo -e "${GREEN}✅ RAG initialized${NC}"
else
    echo -e "${YELLOW}⚠️  RAG init script not found (optional)${NC}"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short || echo -e "${YELLOW}⚠️  Some tests failed (optional)${NC}"
else
    echo -e "${YELLOW}⚠️  pytest not found, skipping tests${NC}"
fi

# Summary
echo ""
echo "========================================="
echo -e "${GREEN}✅ Setup completed!${NC}"
echo "========================================="
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Edit .env with your API keys:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run example workflow:"
echo "   python -m examples.simple_task"
echo ""
echo "4. Or use the Python API:"
echo "   python"
echo "   >>> from graphs.workflow import MultiAgentWorkflow"
echo "   >>> workflow = MultiAgentWorkflow(config)"
echo "   >>> await workflow.execute(...)"
echo ""
echo "📚 Documentation:"
echo "   - README_LANGGRAPH.md"
echo "   - architecture/LANGGRAPH_ARCHITECTURE.md"
echo ""
echo "🎯 Happy coding!"
