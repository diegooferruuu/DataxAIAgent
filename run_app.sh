#!/bin/bash

# Script to run the DATAX Streamlit application

# Check if the virtual environment is activated
if [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  No virtual environment detected."
    echo "Please activate your conda/venv environment first:"
    echo "  conda activate datax"
    exit 1
fi

# Run the Streamlit app
echo "🚀 Starting DATAX Streamlit application..."
streamlit run app.py
