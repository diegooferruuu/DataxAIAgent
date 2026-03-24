import os
from google import genai
from dotenv import load_dotenv

# 1. Cargar el archivo .env
load_dotenv()

# 2. Verificar si la llave se está leyendo bien en Python
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: No se encontró la variable GEMINI_API_KEY en tu archivo .env.")
    print("Asegúrate de que el archivo se llame exactamente '.env' y esté en la raíz del proyecto.")
    exit()

try:
    # 3. Inicializar el cliente con la nueva librería
    client = genai.Client(api_key=api_key)
    print("🔄 Conectando con los servidores de Google...\n")
    
    print("📋 Modelos disponibles para tu API Key:")
    
    # 4. Obtener e imprimir la lista
    for model in client.models.list():
        # Filtramos un poco para que sea más fácil de leer
        if "flash" in model.name.lower() or "pro" in model.name.lower():
            print(f" 🟢 {model.name}")
            
    print("\n✅ ¡Diagnóstico completado! Si ves la lista arriba, tu nueva API Key funciona perfecto.")

except Exception as e:
    print(f"\n❌ ERROR de conexión o autenticación:")
    print(str(e))
    print("\n💡 Recuerda: Ve a Google AI Studio, genera una llave NUEVA, pégala en tu .env y guarda el archivo.")