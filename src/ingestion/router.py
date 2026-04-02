
def route_file(file_path: str, metadata: dict) -> str:
    """
    Decide qué hacer según el tipo de archivo y metadata.
    """
    extension = metadata["extension"]
    
    if extension == ".pdf":
        return "vision_extraction" 
    elif extension in [".xlsx", ".xlsm"]:
        return "tabular_extraction"
    elif extension == ".csv":
        return "csv_loading" 
    else:
        return "unsupported"