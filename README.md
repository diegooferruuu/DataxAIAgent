# DataxAIAgent

## 📊 DATAX - Document Analysis System

A comprehensive document analysis platform powered by AI that extracts metadata and identifies numerical tables from various document formats.

### ✨ Features

- 📋 **Metadata Extraction** - Extracts OS and internal document metadata
- 🏷️ **AI-Powered Table Recognition** - Identifies numerical tables using Gemini 2.0 Flash
- 📊 **Comprehensive Analysis** - Provides structured analysis and JSON export
- 🔄 **Multi-Format Support** - Handles PDF, XLSX, CSV, and PNG files

### 🚀 Quick Start

#### Prerequisites

- Python 3.8+
- Conda or Python venv
- Google Gemini API Key

#### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd DataxAIAgent
   ```

2. **Create and activate virtual environment**
   ```bash
   conda activate datax
   # or
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

#### Running the Streamlit App

```bash
streamlit run app.py
```

Or use the script:
```bash
bash run_app.sh
```

The app will open at `http://localhost:8501`

### 📁 Project Structure

```
src/
├── config/          # Configuration and prompts
├── database/        # Database connections
├── extraction/      # Title and content extraction
├── ingestion/       # Metadata reading and routing
└── validation/      # Data validation schemas
data/
└── raw/            # Input documents
orchestration/
└── main_pipeline_dag.py  # Airflow DAG
```

### 🎯 Usage

1. Open the DATAX web interface
2. Upload a document (PDF, XLSX, CSV, or PNG)
3. View extracted metadata in the "Metadata" tab
4. See identified table titles in the "Report Titles" tab
5. Download the complete analysis as JSON

### 📝 API Reference

#### `extract_metadata(file_path: str) -> dict`
Extracts comprehensive metadata from a file.

**Supported Formats:**
- PDF (pages, author, creation date)
- XLSX (sheets, creator, creation date)
- CSV (basic file metadata)
- PNG (basic file metadata)

#### `extract_report_titles_cognitively(file_path: str) -> ExtractedTitles`
Uses Gemini AI to identify numerical table titles in documents.

**Returns:**
- `table_titles`: List of identified table titles
- `analysis_justification`: Explanation of the analysis

### 🔧 Configuration

Key configuration files:
- `src/config/settings.py` - Application settings
- `src/config/prompts.py` - AI prompts
- `.env` - Environment variables

### 📦 Requirements

Main dependencies:
- streamlit >= 1.0
- google-genai >= 0.3
- pydantic >= 2.0
- pypdf >= 4.0
- openpyxl >= 3.0
- python-dotenv >= 1.0

See `requirements.txt` for complete list.

### 🤝 Contributing

Contributions are welcome! Please follow the existing code structure and add tests for new features.

### 📄 License

[Add your license here]
