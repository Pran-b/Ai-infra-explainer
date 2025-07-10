# Contributing to AWS Infrastructure Explainer

Thank you for your interest in contributing to AWS Infrastructure Explainer! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### 1. **Report Issues**
- Use GitHub Issues to report bugs or request features
- Provide detailed information about the issue
- Include steps to reproduce for bugs
- Use issue templates when available

### 2. **Submit Pull Requests**
- Fork the repository
- Create a feature branch from `main`
- Make your changes with clear commit messages
- Add tests for new functionality
- Update documentation as needed
- Submit a pull request

### 3. **Improve Documentation**
- Fix typos or unclear instructions
- Add examples or use cases
- Improve code comments
- Create or update guides

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+
- AWS CLI configured
- Git

### Local Development
```bash
# Fork and clone the repo
git clone https://github.com/your-username/Ai-infra-explainer.git
cd Ai-infra-explainer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run the application
streamlit run ui-app-new.py
```

## 📝 Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use type hints where appropriate
- Write descriptive docstrings

### Code Quality
```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy modules/

# Run tests
pytest tests/
```

### Commit Messages
Use conventional commit format:
```
feat: add smart query suggestions
fix: resolve datetime serialization issue
docs: update README with new features
refactor: extract query processing logic
test: add unit tests for AWS data manager
```

## 🧪 Testing

### Writing Tests
- Write unit tests for new functions
- Use pytest framework
- Mock AWS API calls in tests
- Test error conditions

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=modules

# Run specific test file
pytest tests/test_dynamic_query_engine.py
```

## 📁 Project Structure

```
Ai-infra-explainer/
├── modules/                    # Core application modules
│   ├── __init__.py
│   ├── aws_data_manager.py    # AWS data collection
│   ├── bedrock_manager.py     # AWS Bedrock integration
│   ├── ollama_manager.py      # Ollama integration
│   ├── dynamic_query_engine.py # Smart query processing
│   ├── complex_query_processor.py # Advanced query handling
│   └── resource_interaction_manager.py # Resource analysis
├── tests/                     # Unit tests
│   ├── __init__.py
│   ├── test_aws_data_manager.py
│   ├── test_dynamic_query_engine.py
│   └── test_complex_query_processor.py
├── docs/                      # Documentation
│   ├── images/               # Screenshots and diagrams
│   ├── SCREENSHOT_GUIDE.md   # Screenshot guidelines
│   └── API.md               # API documentation
├── ui-app-new.py             # Main Streamlit application
├── aws_collector.py          # Legacy AWS data collector
├── qa_engine.py              # Question-answering engine
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
└── README.md                 # Main documentation
```

## 🌟 Feature Development

### Adding New AWS Services

1. **Update Dynamic Query Engine**:
   ```python
   # In modules/dynamic_query_engine.py
   self.query_to_services.update({
       'new_service': ['NewService'],
       'new_resource': ['NewService']
   })
   
   self.service_collectors['NewService'] = self._collect_new_service_data
   ```

2. **Implement Data Collector**:
   ```python
   def _collect_new_service_data(self, aws_profile: str = None) -> Dict[str, Any]:
       """Collect New Service data efficiently"""
       client = self._get_boto3_client('newservice', aws_profile)
       data = {}
       
       try:
           # Implement data collection logic
           data['resources'] = client.list_resources().get('Resources', [])
           # Serialize datetime objects
           data = serialize_datetime(data)
       except ClientError as e:
           data['error'] = str(e)
       
       return {"NewService": data}
   ```

3. **Add Complex Query Support**:
   ```python
   # In modules/complex_query_processor.py
   self.query_patterns['new_service_analysis'] = {
       'pattern': r'new_service.*analysis',
       'processor': self._process_new_service_analysis
   }
   ```

4. **Update Tests**:
   ```python
   # In tests/test_dynamic_query_engine.py
   def test_new_service_collection():
       # Add test for new service
       pass
   ```

### Adding New LLM Providers

1. **Create Manager Module**:
   ```python
   # modules/new_llm_manager.py
   def get_new_llm_models():
       """Get available models from new LLM provider"""
       pass
   
   def is_new_llm_available():
       """Check if new LLM provider is available"""
       pass
   ```

2. **Update UI Configuration**:
   ```python
   # In ui-app-new.py
   llm_provider = st.sidebar.radio(
       "Select LLM Provider", 
       ["Ollama", "Bedrock", "NewLLM"]
   )
   ```

3. **Implement Query Engine**:
   ```python
   # modules/new_llm_query_engine.py
   def query_new_llm_model(query, text_documents, **kwargs):
       """Query new LLM provider"""
       pass
   ```

## 🐛 Bug Reports

### Good Bug Reports Include:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages and stack traces
- Screenshots if applicable

### Bug Report Template:
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. macOS 12.0]
 - Python version: [e.g. 3.9.7]
 - AWS CLI version: [e.g. 2.4.6]

**Additional context**
Any other context about the problem.
```

## 🚀 Feature Requests

### Good Feature Requests Include:
- Clear use case and motivation
- Detailed description of proposed functionality
- Examples of how it would be used
- Consider alternatives and trade-offs

### Feature Request Template:
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've considered.

**Additional context**
Any other context or screenshots.
```

## 📋 Pull Request Guidelines

### Before Submitting:
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains changes

### PR Template:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] Added new tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

## 🎯 Areas for Contribution

### High Priority:
- **Additional AWS Services**: Add support for more AWS services
- **Enhanced Visualizations**: Improve charts and graphs
- **Performance Optimizations**: Reduce query times
- **Error Handling**: Better error messages and recovery
- **Documentation**: More examples and tutorials

### Medium Priority:
- **Testing**: Increase test coverage
- **UI/UX Improvements**: Better user interface
- **Export Options**: Additional export formats
- **Caching**: Implement data caching for performance
- **Monitoring**: Add application monitoring

### Low Priority:
- **Code Refactoring**: Improve code organization
- **Dependencies**: Update and optimize dependencies
- **Deployment**: Docker containerization
- **CI/CD**: Automated testing and deployment

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- Contributors page
- Special mention for significant contributions

## 📞 Getting Help

- **Discord**: [Project Discord Server]
- **GitHub Discussions**: For questions and discussions
- **Email**: [maintainer email]
- **Documentation**: Check existing docs first

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AWS Infrastructure Explainer! 🎉
