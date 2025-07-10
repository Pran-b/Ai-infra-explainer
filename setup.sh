#!/bin/bash
# AWS Infrastructure Explainer Setup Script
# This script helps you get started quickly with the AWS Infrastructure Explainer

set -e

echo "🧠 AWS Infrastructure Explainer Setup"
echo "======================================"
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python $PYTHON_VERSION found"
        return 0
    else
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        return 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found"
        return 0
    else
        print_error "pip3 is not installed. Please install pip."
        return 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found. Please run this script from the project root."
        return 1
    fi
}

# Check AWS CLI
check_aws_cli() {
    if command -v aws &> /dev/null; then
        AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1)
        print_status "$AWS_VERSION found"
        return 0
    else
        print_warning "AWS CLI not found. Installing..."
        install_aws_cli
    fi
}

# Install AWS CLI
install_aws_cli() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install awscli
            print_status "AWS CLI installed via Homebrew"
        else
            print_info "Please install AWS CLI manually:"
            print_info "curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg'"
            print_info "sudo installer -pkg AWSCLIV2.pkg -target /"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf awscliv2.zip aws/
        print_status "AWS CLI installed"
    else
        print_warning "Please install AWS CLI manually for your operating system"
        print_info "Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    fi
}

# Configure AWS CLI
configure_aws() {
    print_info "Checking AWS CLI configuration..."
    
    if aws configure list &> /dev/null; then
        print_status "AWS CLI is already configured"
        
        # Show current configuration
        echo
        print_info "Current AWS Configuration:"
        aws configure list
        echo
        
        read -p "Do you want to reconfigure AWS CLI? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aws configure
        fi
    else
        print_warning "AWS CLI not configured. Please configure it now:"
        print_info "You'll need your AWS Access Key ID and Secret Access Key"
        aws configure
    fi
}

# Check/Install Ollama (optional)
check_ollama() {
    echo
    read -p "Do you want to use Ollama for local AI? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v ollama &> /dev/null; then
            print_status "Ollama found"
            
            # Check if models are available
            if ollama list | grep -q "llama2"; then
                print_status "Ollama models available"
            else
                print_info "Downloading Ollama models (this may take a while)..."
                ollama pull llama2
                print_status "Ollama models downloaded"
            fi
        else
            print_warning "Ollama not found. Installing..."
            install_ollama
        fi
    else
        print_info "Skipping Ollama installation. You can use AWS Bedrock instead."
    fi
}

# Install Ollama
install_ollama() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        print_warning "Please install Ollama manually for your operating system"
        print_info "Visit: https://ollama.ai/download"
        return
    fi
    
    print_status "Ollama installed"
    
    # Start Ollama service
    print_info "Starting Ollama service..."
    ollama serve &
    sleep 5
    
    # Download models
    print_info "Downloading AI models (this may take a while)..."
    ollama pull llama2
    print_status "AI models downloaded"
}

# Test the installation
test_installation() {
    print_info "Testing the installation..."
    
    # Test Python demo
    if python3 demo.py > /dev/null 2>&1; then
        print_status "Demo script runs successfully"
    else
        print_warning "Demo script has issues. Check your AWS configuration."
    fi
    
    # Test Streamlit
    if command -v streamlit &> /dev/null; then
        print_status "Streamlit is ready"
    else
        print_error "Streamlit not found. Please check your installation."
        return 1
    fi
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo
    
    # Check prerequisites
    if ! check_python; then
        exit 1
    fi
    
    if ! check_pip; then
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # AWS setup
    check_aws_cli
    configure_aws
    
    # Optional Ollama setup
    check_ollama
    
    # Test installation
    test_installation
    
    echo
    print_status "Setup completed successfully!"
    echo
    print_info "Next steps:"
    print_info "1. Run the demo: python3 demo.py"
    print_info "2. Start the application: streamlit run ui-app-new.py"
    print_info "3. Open your browser to: http://localhost:8501"
    echo
    print_info "For detailed documentation, visit: docs/README.md"
    echo
    print_info "Need help? Check the troubleshooting guide: docs/USAGE_GUIDE.md"
    echo
}

# Check if script is run from project root
if [ ! -f "ui-app-new.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Run main function
main "$@"
