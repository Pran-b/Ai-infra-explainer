# 🏗️ Project Structure

This document explains the organization and structure of the AWS Infrastructure Explainer project.

## 📁 Directory Structure

```
aws-infrastructure-explainer/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 requirements.txt             # Python dependencies
├── 📄 requirements-dev.txt         # Development dependencies
├── 📄 .gitignore                   # Git ignore patterns
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 🚀 setup.sh                     # Automated setup script
├── 🧪 demo.py                      # Standalone demo script
├── 🎯 ui-app-new.py                # Main Streamlit application
├── 📄 ui_app.py                    # Legacy UI (deprecated)
├── 📄 aws_collector.py             # Legacy AWS collector (deprecated)
├── 📄 qa_engine.py                 # Legacy QA engine (deprecated)
├── 📁 modules/                     # Core application modules
│   ├── 📄 __init__.py
│   ├── 🔧 aws_data_manager.py      # AWS data collection
│   ├── 🧠 bedrock_manager.py       # AWS Bedrock integration
│   ├── 🤖 ollama_manager.py        # Ollama integration
│   ├── 🎨 theme_manager.py         # UI theme management
│   ├── ⚡ dynamic_query_engine.py  # Smart query processing
│   ├── 📊 complex_query_processor.py # Complex query handling
│   ├── 🔗 resource_interaction_manager.py # Resource analysis
│   └── 🔍 bedrock_query_engine.py  # Bedrock query engine
├── 📁 docs/                        # Documentation
│   ├── 📄 README.md                # Documentation index
│   ├── 📖 USAGE_GUIDE.md           # Comprehensive usage guide
│   ├── 🔧 API_DOCUMENTATION.md     # Technical API reference
│   ├── 📸 SCREENSHOT_GUIDE.md      # Screenshot capture guide
│   ├── 🎨 SCREENSHOT_MOCKUPS.md    # UI mockups and designs
│   └── 📁 images/                  # Screenshot and image assets
│       ├── 🖼️ logo.svg
│       ├── 🖼️ smart-query-demo.svg
│       ├── 🖼️ complex-queries-demo.svg
│       ├── 🖼️ resource-interaction-demo.svg
│       └── 🖼️ llm-configuration-demo.svg
└── 📁 __pycache__/                 # Python cache (auto-generated)
```

## 🔧 Core Components

### Main Application Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `ui-app-new.py` | Main Streamlit application | Multi-tab interface, LLM integration, theme management |
| `demo.py` | Standalone demo script | Test functionality without UI |
| `setup.sh` | Automated setup script | One-command installation and configuration |

### Module Architecture

#### Data Management
- **`aws_data_manager.py`**: Centralized AWS data collection
  - Supports 15+ AWS services
  - Handles authentication and regions
  - Provides data serialization

#### AI Integration
- **`bedrock_manager.py`**: AWS Bedrock integration
  - Model discovery and selection
  - Connection testing
  - Profile management

- **`ollama_manager.py`**: Local Ollama integration
  - Model availability checking
  - Connection management
  - Performance optimization

#### Query Processing
- **`dynamic_query_engine.py`**: Smart query processing
  - Query analysis and service detection
  - Targeted data collection
  - Context optimization

- **`complex_query_processor.py`**: Advanced query handling
  - Structured query processing
  - Visualization generation
  - Export functionality

#### Resource Management
- **`resource_interaction_manager.py`**: Resource-level analysis
  - Individual resource analysis
  - Multi-resource comparison
  - AI-powered recommendations

#### UI Components
- **`theme_manager.py`**: Theme and styling management
  - Light/dark theme support
  - Custom CSS injection
  - Consistent styling

## 📊 Data Flow

### 1. User Input Processing
```
User Query → Query Analysis → Service Detection → Data Collection
```

### 2. Smart Query Flow
```
Natural Language Query → 
Query Analysis (dynamic_query_engine) → 
Service Detection → 
Targeted Data Collection (aws_data_manager) → 
AI Processing (bedrock/ollama_manager) → 
Result Display
```

### 3. Complex Query Flow
```
Structured Query → 
Query Processing (complex_query_processor) → 
Data Collection → 
Visualization Generation → 
Export Options
```

### 4. Resource Interaction Flow
```
Resource Selection → 
Resource Analysis (resource_interaction_manager) → 
AI Analysis → 
Recommendations → 
Comparison Results
```

## 🔌 Integration Points

### External Services
- **AWS Services**: EC2, RDS, S3, Lambda, etc.
- **AWS Bedrock**: Claude, Titan, and other models
- **Ollama**: Local LLM inference
- **Streamlit**: Web interface framework

### Internal Dependencies
```
ui-app-new.py
├── modules/aws_data_manager.py
├── modules/bedrock_manager.py
├── modules/ollama_manager.py
├── modules/theme_manager.py
├── modules/dynamic_query_engine.py
├── modules/complex_query_processor.py
├── modules/resource_interaction_manager.py
└── modules/bedrock_query_engine.py
```

## 🎨 UI Architecture

### Tab Structure
1. **Smart Query Tab**
   - Natural language input
   - Progress indicators
   - AI response display
   - Context preview

2. **Complex Queries Tab**
   - Pre-defined query buttons
   - Structured query input
   - Visualization panels
   - Export options

3. **Resource Interaction Tab**
   - Resource selection interface
   - Analysis results
   - Comparison features
   - Recommendations

### Sidebar Components
- Theme selector
- LLM provider selection
- Model configuration
- AWS profile management
- Connection status indicators

## 🔧 Configuration Management

### Configuration Files
- `requirements.txt`: Python dependencies
- `requirements-dev.txt`: Development dependencies
- `.gitignore`: Version control exclusions

### Environment Variables
```bash
# AWS Configuration
AWS_PROFILE=default
AWS_DEFAULT_REGION=us-east-1

# Ollama Configuration
OLLAMA_HOST=localhost:11434

# Application Configuration
STREAMLIT_THEME=light
DEBUG_MODE=false
```

### Runtime Configuration
- AWS profiles (managed by `bedrock_manager.py`)
- LLM model selection (UI sidebar)
- Theme preferences (UI sidebar)
- Debug mode (session state)

## 📚 Documentation Structure

### User Documentation
- **README.md**: Main project overview
- **USAGE_GUIDE.md**: Comprehensive usage instructions
- **SCREENSHOT_GUIDE.md**: Visual documentation guide

### Developer Documentation
- **API_DOCUMENTATION.md**: Technical reference
- **CONTRIBUTING.md**: Development guidelines
- **SCREENSHOT_MOCKUPS.md**: UI design reference

### Visual Assets
- **SVG Screenshots**: Professional interface mockups
- **Logo**: Project branding
- **Diagrams**: Architecture and flow diagrams

## 🚀 Deployment Considerations

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run ui-app-new.py
```

### Production Deployment
- Consider using Docker containers
- Set up proper AWS IAM roles
- Configure environment variables
- Monitor resource usage

### Security Considerations
- No hardcoded credentials
- Uses AWS CLI configuration
- Respects IAM permissions
- Optional local AI processing

## 🔄 Future Enhancements

### Planned Features
- Docker containerization
- Multi-region support
- Advanced visualizations
- Custom query templates
- API endpoints
- Batch processing
- Automated reporting

### Extension Points
- Additional AWS services
- New LLM providers
- Custom visualization types
- Export formats
- Authentication systems
- Multi-user support

This structure provides a scalable, maintainable architecture that supports both current features and future enhancements.
