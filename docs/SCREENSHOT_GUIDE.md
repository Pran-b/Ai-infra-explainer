# Screenshot Guide for AWS Infrastructure Explainer

This guide helps you capture professional screenshots for the README documentation.

## 📸 Required Screenshots

### 1. **Smart Query Engine Demo** (`smart-query-demo.png`)
**What to capture:**
- Smart Query tab open
- Example query: "Show me running EC2 instances"
- Show the Smart Data Collection progress
- Display the AI analysis results with actual instance details
- Include the context debug information showing data size

**Steps:**
1. Open Smart Query tab
2. Enter query: "Show me running EC2 instances"
3. Click "⚡ Smart Query"
4. Wait for results to load
5. Expand "🔍 Context Preview" to show debugging info
6. Take screenshot of the entire interface

---

### 2. **Complex Query Processing Demo** (`complex-queries-demo.png`)
**What to capture:**
- Complex Queries tab open
- Show pre-defined query buttons
- Example result with visualizations (charts/graphs)
- Export options visible
- Structured data display

**Steps:**
1. Open Complex Queries tab
2. Click "Running EC2s with Security Groups" button
3. Click "⚡ Process Structured Query"
4. Show the formatted results with charts
5. Make sure export buttons are visible
6. Take screenshot

---

### 3. **Resource Interaction Demo** (`resource-interaction-demo.png`)
**What to capture:**
- Resource Interaction tab open
- List of AWS resources with checkboxes
- Selected resources highlighted
- AI analysis results for specific resources
- Recommendations section

**Steps:**
1. Open Resource Interaction tab
2. Expand one service (e.g., EC2 Resources)
3. Select 1-2 resources with checkboxes
4. Enter a question like "What are the security risks?"
5. Click "🤖 Analyze Selected Resources"
6. Show the AI analysis results
7. Take screenshot

---

### 4. **LLM Configuration Demo** (`llm-configuration-demo.png`)
**What to capture:**
- Sidebar with LLM provider selection
- AWS Bedrock configuration expanded
- Available models list
- Connection test results
- Both Ollama and Bedrock options visible

**Steps:**
1. Show sidebar with "Select LLM Provider" radio buttons
2. Select "Bedrock" option
3. Expand "🔐 AWS Bedrock Configuration"
4. Click "🔄 Fetch Available Models"
5. Show the model list with status indicators
6. Take screenshot of the configuration panel

---

### 5. **Main Dashboard Overview** (`main-dashboard.png`)
**What to capture:**
- Full application interface
- All tabs visible (Smart Query, General Query, Complex Queries, Resource Interaction)
- Sidebar with configurations
- Infrastructure Overview panel on the right
- Clean, professional look

**Steps:**
1. Ensure app is freshly loaded
2. Select a nice theme (Light or Dark)
3. Show all main interface elements
4. Make sure no error messages are visible
5. Take full-screen screenshot

---

### 6. **Data Collection Progress** (`data-collection-demo.png`)
**What to capture:**
- Smart data collection in progress
- Progress bar visible
- Status messages showing which services are being collected
- Success message at the end

**Steps:**
1. Start a Smart Query
2. Capture the progress indicators
3. Show the "🎯 Smart Data Collection" message
4. Include the "✅ Successfully collected data" message

---

## 🎨 Screenshot Guidelines

### Technical Requirements:
- **Resolution**: Minimum 1920x1080 (Full HD)
- **Format**: PNG (for transparency and quality)
- **DPI**: 144 DPI or higher for crisp display
- **Browser**: Use Chrome or Firefox for consistent rendering

### Visual Guidelines:
- **Clean Interface**: No browser bookmarks bar, minimize distractions
- **Consistent Theme**: Use the same theme across all screenshots
- **Professional Data**: Use realistic but non-sensitive AWS resource names
- **Full Context**: Show enough interface elements to understand the feature
- **Highlight Key Features**: Ensure important UI elements are visible

### Browser Setup:
```bash
# Recommended browser window size
# Width: 1400px
# Height: 900px
# Zoom: 100%
```

### Data Preparation:
- Ensure you have some AWS resources to demonstrate
- Use generic resource names (avoid company-specific names)
- Test all features work properly before screenshotting

---

## 🖼️ Optional Screenshots

### 7. **Error Handling Demo** (`error-handling-demo.png`)
- Show graceful error handling
- AWS permission errors
- Connection timeouts
- User-friendly error messages

### 8. **Export Functionality** (`export-demo.png`)
- Show export options
- Download buttons
- Different export formats (JSON, CSV, Markdown)

### 9. **Visualizations Demo** (`visualizations-demo.png`)
- Interactive charts
- Security group analysis charts
- Cost distribution graphs
- Resource state pie charts

---

## 📝 Screenshot Naming Convention

- Use kebab-case (lowercase with hyphens)
- Be descriptive but concise
- Include the feature name
- Add `-demo` suffix for feature demonstrations

Examples:
- `smart-query-demo.png`
- `complex-queries-demo.png`
- `resource-interaction-demo.png`
- `llm-configuration-demo.png`

---

## 🔧 Tools for Screenshots

### Recommended Tools:
- **macOS**: Cmd+Shift+4 (built-in), CleanShot X, Skitch
- **Windows**: Snipping Tool, Greenshot, ShareX
- **Linux**: GNOME Screenshot, Flameshot, Shutter
- **Browser Extensions**: Awesome Screenshot, FireShot

### Image Editing:
- **Basic**: Preview (macOS), Paint (Windows), GIMP (Linux)
- **Advanced**: Adobe Photoshop, Canva, Figma
- **Online**: Photopea, Canva, Remove.bg

---

## ✅ Quality Checklist

Before submitting screenshots:

- [ ] All text is readable at normal viewing size
- [ ] No sensitive or company-specific information visible
- [ ] UI elements are properly aligned and not cut off
- [ ] Colors are consistent with the application theme
- [ ] No browser UI distractions (bookmarks, extensions)
- [ ] Screenshots demonstrate the actual functionality
- [ ] File sizes are reasonable (< 2MB per image)
- [ ] Images are properly compressed for web use

---

## 🚀 After Capturing Screenshots

1. **Optimize Images**:
   ```bash
   # Install imagemagick for optimization
   brew install imagemagick  # macOS
   
   # Optimize PNG files
   convert input.png -strip -quality 85 output.png
   ```

2. **Update README Paths**:
   - Ensure all image paths in README.md match your screenshot names
   - Test that images display correctly on GitHub

3. **Git Add Images**:
   ```bash
   git add docs/images/
   git commit -m "docs: Add comprehensive screenshots"
   ```

---

This guide ensures your screenshots are professional, consistent, and effectively demonstrate the application's capabilities!
