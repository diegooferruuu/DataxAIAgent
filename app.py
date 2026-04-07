import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Import local modules
from src.ingestion.metadata_reader import extract_metadata
from src.extraction.cognitive_titles import extract_report_titles_cognitively


# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="DATAX - Document Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }
    .metadata-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .titles-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ca02c;
        margin-bottom: 0.5rem;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #d62728;
    }
    .success-box {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2ca02c;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# Header
# ==========================================
st.markdown('<div class="main-title">📊 DATAX</div>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# API Key Configuration (Sidebar)
# ==========================================
with st.sidebar:
    st.header("🔑 API Configuration")
    api_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        help="Your API key is stored only in this session and not saved"
    )
    st.markdown("---")
    if not api_key:
        st.warning("⚠️ API Key is required to use the analysis features")

# ==========================================
# File Upload Section
# ==========================================
st.header("📁 Upload Document")
st.write("Supported formats: PDF, XLSX, CSV, PNG")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "xlsx", "csv", "png"],
    help="Upload a document to analyze"
)

if uploaded_file is not None and api_key:
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_file_path = tmp_file.name
    
    try:
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📋 Metadata", "🏷️ Report Titles", "📊 Full Analysis"])
        
        # ==========================================
        # Tab 1: Metadata
        # ==========================================
        with tab1:
            st.subheader("Document Metadata")
            
            with st.spinner("Extracting metadata..."):
                metadata = extract_metadata(tmp_file_path)
            
            # Display metadata in a formatted way
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="metadata-box">', unsafe_allow_html=True)
                st.write(f"**File Name:** {metadata['source_file']}")
                st.write(f"**Extension:** {metadata['extension']}")
                st.write(f"**File Size:** {metadata['size_bytes']:,} bytes ({metadata['size_bytes'] / (1024*1024):.2f} MB)")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metadata-box">', unsafe_allow_html=True)
                st.write(f"**Created (OS):** {metadata['os_creation_date']}")
                st.write(f"**Modified (OS):** {metadata['os_modification_date']}")
                if metadata['internal_author']:
                    st.write(f"**Author:** {metadata['internal_author']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if metadata['extra_details']:
                st.markdown(f"""
                <div class="metadata-box">
                    <b>Additional Details:</b><br>
                    {metadata['extra_details']}
                </div>
                """, unsafe_allow_html=True)
            
            # Full metadata JSON
            with st.expander("📋 Full Metadata (JSON)"):
                st.json(metadata)
        
        # ==========================================
        # Tab 2: Report Titles
        # ==========================================
        with tab2:
            st.subheader("Extracted Table Titles")
            
            with st.spinner("Analyzing document for table titles..."):
                titles_result = extract_report_titles_cognitively(tmp_file_path, api_key=api_key)
            
            if titles_result.table_titles:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.write(f"✅ Found {len(titles_result.table_titles)} table(s)")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("**Titles:**")
                for idx, title in enumerate(titles_result.table_titles, 1):
                    st.markdown(f"""
                    <div class="titles-box">
                        <b>{idx}.</b> {title}
                    </div>
                    """, unsafe_allow_html=True)
                
                if titles_result.analysis_justification:
                    with st.expander("📝 Analysis Justification"):
                        st.write(titles_result.analysis_justification)
            else:
                st.markdown("""
                <div class="error-box">
                    <b>⚠️ No tables found</b><br>
                    No numerical tables were detected in this document.
                </div>
                """, unsafe_allow_html=True)
                if titles_result.analysis_justification:
                    st.write(f"**Reason:** {titles_result.analysis_justification}")
        
        # ==========================================
        # Tab 3: Full Analysis
        # ==========================================
        with tab3:
            st.subheader("Complete Analysis Report")
            
            analysis_report = {
                "timestamp": datetime.now().isoformat(),
                "file_metadata": metadata,
                "table_extraction": {
                    "titles": titles_result.table_titles,
                    "justification": titles_result.analysis_justification,
                    "count": len(titles_result.table_titles)
                }
            }
            
            st.json(analysis_report)
            
            # Download button
            json_str = json.dumps(analysis_report, indent=2)
            st.download_button(
                label="📥 Download Analysis Report (JSON)",
                data=json_str,
                file_name=f"analysis_{Path(uploaded_file.name).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.success("✅ Analysis complete!")
        
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
            <b>❌ Error during analysis:</b><br>
            {str(e)}
        </div>
        """, unsafe_allow_html=True)
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass

elif uploaded_file is not None and not api_key:
    st.markdown("""
    <div class="error-box">
        <b>❌ API Key Required</b><br>
        Please provide your Gemini API Key in the sidebar to analyze documents.
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("👆 Upload a document to begin analysis")

# ==========================================
# Sidebar Information
# ==========================================
with st.sidebar:
    st.header("ℹ️ INFO")
    
    
    st.markdown("---")
    st.subheader("📖 Supported Formats")
    st.write("""
    - **PDF** - Portable Document Format
    - **XLSX** - Excel Spreadsheets
    - **CSV** - Comma-Separated Values
    - **PNG** - Image Files
    """)
    
    st.markdown("---")
    st.subheader("🔧 Features")
    st.write("""
    - 📋 OS & Internal Metadata Extraction
    - 🏷️ AI-Powered Table Title Recognition
    - 📊 Comprehensive Analysis Reports
    - 💾 Export to JSON
    """)
