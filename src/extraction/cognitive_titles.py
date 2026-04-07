import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import json

load_dotenv()

# ==========================================
# Step 1: Output Validation Schema (Pydantic)
# ==========================================
class ExtractedTitles(BaseModel):
    table_titles: list[str] = Field(
        ..., 
        description="Exact titles of the numerical data tables found. Returns empty list if none."
    )
    analysis_justification: str | None = Field(
        None, 
        description="Short reason why these were selected over chart titles or headers."
    )

# ==========================================
# Step 2: Configure the New AI Client
# ==========================================
# Create client with API key (can be passed as parameter or from environment)
# client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ==========================================
# Step 3: The Cognitive Prompt
# ==========================================
COGNITIVE_PROMPT = """
You are an expert Document Analysis Agent specializing in insurance and financial reports.

**INPUT:**
You will receive an image or a PDF page of a financial report. This document may contain general headers, descriptive text, numerical tables, charts, and graphs.

**YOUR TASK:**
Locate all visible structural tables containing rows and columns of *numerical* data. Extract the precise title that corresponds to each *numerical table* found.

**STRICT RULES:**
1. **FOCUS ONLY ON TABLES:** Extract titles *only* if they directly reference a grid/structure containing numbers.
2. **IGNORE CHARTS:** If you see a chart, graph, or visualization with a title like 'Evolución de Primas' or similar, you MUST ignore it. Do not extract it.
3. **IGNORE HEADERS:** Do not extract general section headers like 'RESUMEN EJECUTIVO GENERAL', 'BOLETÍN', page numbers, or dates, unless they are the *only* title for a table.
4. **RECONSTRUCT TITLES:** If a table title is split across multiple lines, reconstruct it into a single clean line.
"""

# ==========================================
# Step 4: The Execution Function
# ==========================================
def extract_report_titles_cognitively(file_path: str, api_key: Optional[str] = None) -> ExtractedTitles:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"[COGNITIVE] Analyzing: {file_path} for numerical table titles...")
    
    # Use provided API key or fall back to environment variable
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        env_key = os.environ.get("GEMINI_API_KEY")
        if not env_key:
            raise ValueError("No API key provided and GEMINI_API_KEY not found in environment")
        client = genai.Client(api_key=env_key)

    sample_file = client.files.upload(file=file_path)

    try:
        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": [
        #                 {"type": "text", "text": COGNITIVE_PROMPT},
        #                 {
        #                     "type": "image_url",
        #                     "image_url": {
        #                         "url": f"data:image/png;base64,{base64_image}"
        #                     }
        #                 }
        #             ]
        #         }
        #     ],
        #     temperature=0.7
        # )
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[sample_file, COGNITIVE_PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedTitles,
            ),
        )
        
        client.files.delete(name=sample_file.name)
        
        return ExtractedTitles(**json.loads(response.text))

    except Exception as e:
        print(f"  --> Unexpected Error: {e}")
        return ExtractedTitles(table_titles=[], analysis_justification=f"General error: {str(e)}")

# ==========================================
# Bloque de prueba local
# ==========================================
if __name__ == "__main__":
    screenshots = [
        "data/raw/prueba1.png",
        "data/raw/prueba2.png"
    ]

    print("--- Iniciando prueba con imágenes (Nuevo SDK) ---")
    for shot in screenshots:
        print(f"\nProcesando: {shot}...")
        if os.path.exists(shot):
            result = extract_report_titles_cognitively(shot)
            print(f"Títulos encontrados: {result.table_titles}")
            print(f"Razonamiento: {result.analysis_justification}")
        else:
            print(f"Error: No se encontró la imagen en {shot}")