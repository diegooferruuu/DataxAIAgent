import os
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader
import openpyxl

def _get_base_metadata(file_path: str) -> dict:
    """Extracts Operating System metadata (Applies to all files)."""
    stats = os.stat(file_path)
    
    return {
        "source_file": Path(file_path).name,
        "extension": Path(file_path).suffix.lower(),
        "size_bytes": stats.st_size,
        "os_creation_date": datetime.fromtimestamp(stats.st_ctime).isoformat(),
        "os_modification_date": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "internal_author": None,
        "internal_creation_date": None,
        "extra_details": None # To store pages or sheet names
    }

def _enrich_pdf(file_path: str, metadata: dict) -> dict:
    """Extracts specific internal metadata from a PDF document."""
    try:
        reader = PdfReader(file_path)
        info = reader.metadata
        
        if info:
            # Metadata in PDFs usually starts with a '/'
            metadata["internal_author"] = info.get("/Author")
            
            # Basic cleanup of the PDF date if it exists
            raw_date = info.get("/CreationDate")
            metadata["internal_creation_date"] = raw_date if raw_date else None
            
        metadata["extra_details"] = f"Pages: {len(reader.pages)}"
        
    except Exception as e:
        metadata["extra_details"] = f"Error reading PDF: {str(e)}"
        
    return metadata

def _enrich_excel(file_path: str, metadata: dict) -> dict:
    """Extracts internal metadata from an XLSX file efficiently."""
    try:
        # read_only=True is crucial to avoid loading heavy data into memory
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        props = wb.properties
        
        metadata["internal_author"] = props.creator
        metadata["internal_creation_date"] = props.created.isoformat() if props.created else None
        metadata["extra_details"] = f"Sheets: {', '.join(wb.sheetnames)}"
        
        # Explicitly close to free memory
        wb.close()
        
    except Exception as e:
         metadata["extra_details"] = f"Error reading XLSX: {str(e)}"
         
    return metadata

def extract_metadata(file_path: str) -> dict:
    """
    Main orchestrator function.
    Receives a file path and returns a standardized dictionary with its metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # 1. Get base metadata (common for all)
    metadata = _get_base_metadata(file_path)
    extension = metadata["extension"]

    # 2. Enrich based on type (CSV only keeps base metadata)
    if extension == ".pdf":
        metadata = _enrich_pdf(file_path, metadata)
    elif extension in [".xlsx", ".xlsm"]:
        metadata = _enrich_excel(file_path, metadata)
        
    return metadata

# ==========================================
# Local testing block
# ==========================================
if __name__ == "__main__":
    # Change these file names to the ones you want to test
    files_to_test = ["data/raw/test.pdf", "data/raw/test.xlsx"]
    
    for path in files_to_test:
        print(f"\n--- Testing file: {path} ---")
        try:
            result = extract_metadata(path)
            for key, value in result.items():
                print(f"  {key}: {value}")
        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")