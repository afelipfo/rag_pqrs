#!/usr/bin/env python3
"""
Script de instalación para el Sistema RAG PQRS
Compatible con Python 3.12
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e.stderr}")
        return False

def main():
    print("🚀 Instalando Sistema RAG PQRS - Infraestructura Medellín")
    print("=" * 60)
    
    # Verificar versión de Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"📋 Python version detectada: {python_version}")
    
    # Lista de comandos de instalación
    install_commands = [
        ("pip install --upgrade pip", "Actualizando pip"),
        ("pip install setuptools>=68.0.0 wheel>=0.40.0", "Instalando herramientas básicas"),
    ]
    
    # Para Python 3.12, añadir setuptools-scm
    if sys.version_info.major == 3 and sys.version_info.minor >= 12:
        install_commands.append(
            ("pip install setuptools-scm", "Instalando dependencias para Python 3.12")
        )
    
    # Dependencias principales
    install_commands.extend([
        ("pip install fastapi uvicorn[standard] pydantic python-multipart", 
         "Instalando framework web"),
        ("pip install openai tiktoken", "Instalando cliente OpenAI"),
        ("pip install chromadb", "Instalando base de datos vectorial"),
        ("pip install sentence-transformers", "Instalando modelos de embeddings"),
        ("pip install pandas numpy", "Instalando librerías de datos"),
        ("pip install jinja2 aiofiles", "Instalando dependencias web"),
        ("pip install python-dotenv requests", "Instalando utilidades"),
    ])
    
    # Ejecutar instalaciones
    failed_commands = []
    for command, description in install_commands:
        if not run_command(command, description):
            failed_commands.append(description)
    
    # Dependencias opcionales (pueden fallar sin problemas)
    optional_commands = [
        ("pip install python-docx", "Instalando soporte para documentos Word"),
        ("pip install PyPDF2", "Instalando soporte para PDF"),
    ]
    
    print("\n📋 Instalando dependencias opcionales...")
    for command, description in optional_commands:
        run_command(command, description)
    
    print("\n" + "=" * 60)
    if failed_commands:
        print("⚠️  Algunas dependencias fallaron:")
        for failed in failed_commands:
            print(f"   - {failed}")
        print("\n📝 Puedes intentar instalarlas manualmente más tarde.")
    else:
        print("✅ ¡Todas las dependencias se instalaron correctamente!")
    
    print("\n📝 Próximos pasos:")
    print("1. Copiar .env.example a .env:")
    print("   cp .env.example .env")
    print("2. Editar .env y configurar OPENAI_API_KEY")
    print("3. Inicializar base de datos:")
    print("   python scripts/init_data.py")
    print("4. Ejecutar aplicación:")
    print("   python -m app.main")
    print("\n🌐 La aplicación estará disponible en: http://localhost:8000")

if __name__ == "__main__":
    main()