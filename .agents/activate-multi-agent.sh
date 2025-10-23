#!/bin/bash

# Multi-Agent Activation Script
# Configures and activates AI agents for any project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
AGENTS_DIR="${PROJECT_ROOT}/.agents"
COPILOT_DIR="${PROJECT_ROOT}/.copilot"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect project type
detect_project_type() {
    local project_type="unknown"
    
    if [[ -f "package.json" ]]; then
        if grep -q "react" package.json; then
            project_type="react-frontend"
        elif grep -q "vue" package.json; then
            project_type="vue-frontend"
        elif grep -q "angular" package.json; then
            project_type="angular-frontend"
        elif grep -q "express" package.json; then
            project_type="node-backend"
        elif grep -q "next" package.json; then
            project_type="next-fullstack"
        else
            project_type="javascript"
        fi
    elif [[ -f "composer.json" ]]; then
        project_type="php-backend"
    elif [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        project_type="python-backend"
    elif [[ -f "pom.xml" ]] || [[ -f "build.gradle" ]]; then
        project_type="java-backend"
    elif [[ -f "Cargo.toml" ]]; then
        project_type="rust-backend"
    elif [[ -f "go.mod" ]]; then
        project_type="go-backend"
    elif [[ -f "docker-compose.yml" ]] || [[ -f "docker-compose.yaml" ]]; then
        project_type="containerized-app"
    elif [[ -f "Dockerfile" ]]; then
        project_type="containerized-service"
    fi
    
    echo "$project_type"
}

# Function to get recommended agents for project type
get_recommended_agents() {
    local project_type="$1"
    local agents=""
    
    case "$project_type" in
        "react-frontend"|"vue-frontend"|"angular-frontend")
            agents="fullstack-architect frontend-specialist ux-specialist qa-specialist performance-specialist"
            ;;
        "node-backend"|"php-backend"|"python-backend"|"java-backend"|"rust-backend"|"go-backend")
            agents="fullstack-architect backend-specialist security-specialist performance-specialist qa-specialist"
            ;;
        "next-fullstack"|"containerized-app")
            agents="fullstack-architect frontend-specialist backend-specialist devops-specialist security-specialist"
            ;;
        "containerized-service")
            agents="fullstack-architect backend-specialist devops-specialist security-specialist performance-specialist"
            ;;
        *)
            agents="fullstack-architect frontend-specialist backend-specialist devops-specialist"
            ;;
    esac
    
    echo "$agents"
}

# Function to copy agent configurations
copy_agent_configs() {
    print_status "Copying agent configurations..."
    
    # Create directories if they don't exist
    mkdir -p "$AGENTS_DIR"
    mkdir -p "$COPILOT_DIR"
    
    # Copy main configuration
    if [[ -f "${SCRIPT_DIR}/multi-agent-config.json" ]]; then
        cp "${SCRIPT_DIR}/multi-agent-config.json" "$AGENTS_DIR/"
        print_success "Copied main agent configuration"
    else
        print_error "Main configuration file not found!"
        return 1
    fi
    
    # Copy copilot instructions
    if [[ -f "${SCRIPT_DIR}/../.copilot/instructions.md" ]]; then
        cp "${SCRIPT_DIR}/../.copilot/instructions.md" "$COPILOT_DIR/"
        print_success "Copied Copilot instructions"
    else
        print_error "Copilot instructions not found!"
        return 1
    fi
    
    # Copy individual agent configurations
    local agent_dirs=(
        "01-arquitecto-fullstack-mvp"
        "02-frontend-react-css-vanilla"
        "03-backend-php-security"
        "04-devops-docker-nginx"
        "05-performance-web"
        "06-security-auditor"
        "07-qa-accessibility"
        "08-seo-technical-content"
        "09-ux-ui-designer"
        "10-ai-integration-specialist"
        "11-comercial-ventas-experto"
        "12-observer-optimizer"
    )
    
    for agent_dir in "${agent_dirs[@]}"; do
        if [[ -d "${SCRIPT_DIR}/../${agent_dir}" ]]; then
            cp -r "${SCRIPT_DIR}/../${agent_dir}" "$AGENTS_DIR/"
            print_success "Copied agent: $agent_dir"
        else
            print_warning "Agent directory not found: $agent_dir"
        fi
    done
    
    # Copy RAG knowledge structure
    if [[ -d "${SCRIPT_DIR}/../rag-knowledge" ]]; then
        cp -r "${SCRIPT_DIR}/../rag-knowledge" "$AGENTS_DIR/"
        print_success "Copied RAG knowledge base structure"
    else
        print_warning "RAG knowledge structure not found"
    fi
}

# Function to customize configuration for project
customize_config() {
    local project_type="$1"
    local project_name="$(basename "$PROJECT_ROOT")"
    
    print_status "Customizing configuration for project: $project_name"
    
    # Update main configuration with project details
    if [[ -f "$AGENTS_DIR/multi-agent-config.json" ]]; then
        sed -i.bak "s/CONFIGURABLE_PROJECT_NAME/$project_name/g" "$AGENTS_DIR/multi-agent-config.json"
        rm "$AGENTS_DIR/multi-agent-config.json.bak"
        print_success "Updated project name in configuration"
    fi
    
    # Create project-specific README
    cat > "$AGENTS_DIR/README.md" << EOF
# Multi-Agent System for $project_name

## Project Type: $project_type

## Quick Start

This project is configured with an AI multi-agent system for enhanced development productivity.

### Available Agents

- \`@fullstack-architect\` - Overall technical coordination and architecture
- \`@frontend-specialist\` - Frontend development and UI optimization
- \`@backend-specialist\` - Backend APIs and data processing
- \`@devops-specialist\` - Infrastructure and deployment
- \`@security-specialist\` - Security and compliance
- \`@performance-specialist\` - Performance optimization
- \`@qa-specialist\` - Quality assurance and testing
- \`@ux-specialist\` - User experience and design
- \`@data-specialist\` - Data architecture and analytics
- \`@ai-specialist\` - AI/ML integration
- \`@business-specialist\` - Business strategy and requirements

### Usage Examples

\`\`\`
# Activate specific agents for a task
@fullstack-architect @frontend-specialist Help me implement user authentication

# Get performance optimization advice
@performance-specialist @frontend-specialist Optimize page loading speed

# Security review for new feature
@security-specialist @backend-specialist Review the new payment endpoint
\`\`\`

### Configuration

Agent configurations are in \`.agents/\` directory:
- \`multi-agent-config.json\` - Main configuration
- \`01-arquitecto-fullstack-mvp/\` - Full-stack architect
- \`02-frontend-react-css-vanilla/\` - Frontend specialist
- etc.

### Customization

To customize agents for your specific technology stack:
1. Edit \`multi-agent-config.json\` to update agent expertise
2. Modify individual agent configurations in their directories
3. Update \`.copilot/instructions.md\` with project-specific patterns

EOF
    
    print_success "Created project-specific README"
}

# Function to validate installation
validate_installation() {
    print_status "Validating installation..."
    
    local errors=0
    
    # Check main configuration
    if [[ ! -f "$AGENTS_DIR/multi-agent-config.json" ]]; then
        print_error "Main configuration file missing"
        ((errors++))
    fi
    
    # Check copilot instructions
    if [[ ! -f "$COPILOT_DIR/instructions.md" ]]; then
        print_error "Copilot instructions missing"
        ((errors++))
    fi
    
    # Check at least core agents exist
    local core_agents=("01-arquitecto-fullstack-mvp" "02-frontend-react-css-vanilla" "03-backend-php-security")
    for agent in "${core_agents[@]}"; do
        if [[ ! -d "$AGENTS_DIR/$agent" ]]; then
            print_error "Core agent missing: $agent"
            ((errors++))
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        print_success "Installation validation passed"
        return 0
    else
        print_error "Installation validation failed with $errors errors"
        return 1
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Multi-Agent Activation Script

Usage: $0 [OPTIONS]

Options:
    -h, --help          Show this help message
    -f, --force         Force overwrite existing configuration
    -t, --type TYPE     Override project type detection
    -q, --quiet         Quiet mode - minimal output
    
Project Types:
    react-frontend      React-based frontend application
    vue-frontend        Vue.js frontend application
    angular-frontend    Angular frontend application
    node-backend        Node.js backend service
    php-backend         PHP backend application
    python-backend      Python backend service
    java-backend        Java backend application
    rust-backend        Rust backend service
    go-backend          Go backend service
    next-fullstack      Next.js full-stack application
    containerized-app   Multi-service containerized application
    
Examples:
    $0                  # Auto-detect project type and install
    $0 -t react-frontend # Force React frontend configuration
    $0 -f               # Force overwrite existing configuration
    
EOF
}

# Main function
main() {
    local force_overwrite=false
    local quiet_mode=false
    local override_type=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -f|--force)
                force_overwrite=true
                shift
                ;;
            -t|--type)
                override_type="$2"
                shift 2
                ;;
            -q|--quiet)
                quiet_mode=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check if already configured
    if [[ -d "$AGENTS_DIR" ]] && [[ "$force_overwrite" != true ]]; then
        print_warning "Agents already configured in this project"
        print_status "Use -f/--force to overwrite existing configuration"
        exit 1
    fi
    
    # Detect or use override project type
    local project_type
    if [[ -n "$override_type" ]]; then
        project_type="$override_type"
        print_status "Using override project type: $project_type"
    else
        project_type="$(detect_project_type)"
        print_status "Detected project type: $project_type"
    fi
    
    # Get recommended agents
    local recommended_agents="$(get_recommended_agents "$project_type")"
    if [[ "$quiet_mode" != true ]]; then
        print_status "Recommended agents: $recommended_agents"
    fi
    
    # Copy configurations
    copy_agent_configs || exit 1
    
    # Customize for project
    customize_config "$project_type"
    
    # Validate installation
    validate_installation || exit 1
    
    # Success message
    print_success "Multi-agent system activated for project!"
    print_status "Agent configurations installed in .agents/"
    print_status "Copilot instructions installed in .copilot/"
    
    if [[ "$quiet_mode" != true ]]; then
        echo
        print_status "Next steps:"
        echo "1. Review and customize agent configurations in .agents/"
        echo "2. Update .copilot/instructions.md with project-specific patterns"
        echo "3. Use agent mentions like @fullstack-architect in your development prompts"
        echo
        print_status "For help: cat .agents/README.md"
    fi
}

# Run main function with all arguments
main "$@"