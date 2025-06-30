#!/bin/bash

echo "🚀 Instalando Sistema RAG PQRS - Infraestructura Medellín"
echo "============================================================="

# Verificar Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "📋 Python version detectada: $python_version"

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip setuptools wheel

# Para Python 3.12, instalar setuptools-scm que incluye distutils
if [[ $python_version == 3.12* ]]; then
    echo "🔧 Instalando dependencias para Python 3.12..."
    pip install setuptools-scm
fi

# Instalar dependencias básicas primero
echo "📚 Instalando dependencias básicas..."
pip install setuptools>=68.0.0 wheel>=0.40.0

# Instalar dependencias core
echo "🛠️  Instalando dependencias principales..."
pip install fastapi uvicorn[standard] pydantic python-multipart

# Instalar AI/ML dependencies
echo "🤖 Instalando dependencias de IA..."
pip install openai tiktoken

# Instalar vector database
echo "🔍 Instalando base de datos vectorial..."
pip install chromadb sentence-transformers

# Instalar data processing
echo "📊 Instalando librerías de procesamiento..."
pip install pandas numpy

# Instalar web dependencies
echo "🌐 Instalando dependencias web..."
pip install jinja2 aiofiles

# Instalar utilities
echo "⚙️  Instalando utilidades..."
pip install python-dotenv requests

# Instalar dependencias opcionales
echo "📋 Instalando dependencias opcionales..."
pip install python-docx PyPDF2 || echo "⚠️  Algunas dependencias opcionales no se pudieron instalar"

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "📝 Próximos pasos:"
echo "1. Copiar .env.example a .env y configurar OPENAI_API_KEY"
echo "2. Ejecutar: python scripts/init_data.py"
echo "3. Ejecutar: python -m app.main"
echo ""
echo "🌐 La aplicación estará disponible en: http://localhost:8000"