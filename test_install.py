#!/usr/bin/env python3
"""
Script de prueba para verificar la instalación del Sistema RAG PQRS
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Prueba importar un módulo"""
    display_name = package_name or module_name
    try:
        importlib.import_module(module_name)
        print(f"✅ {display_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - ERROR: {e}")
        return False

def main():
    print("🧪 Verificando instalación del Sistema RAG PQRS")
    print("=" * 50)
    
    # Lista de módulos a verificar
    modules_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("openai", "OpenAI"),
        ("tiktoken", "TikToken"),
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("jinja2", "Jinja2"),
        ("aiofiles", "AioFiles"),
        ("dotenv", "Python-dotenv"),
        ("requests", "Requests"),
    ]
    
    # Verificar Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"🐍 Python version: {python_version}")
    print()
    
    # Probar imports
    successful_imports = 0
    total_imports = len(modules_to_test)
    
    for module, display_name in modules_to_test:
        if test_import(module, display_name):
            successful_imports += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado: {successful_imports}/{total_imports} módulos importados correctamente")
    
    if successful_imports == total_imports:
        print("🎉 ¡Todas las dependencias están instaladas correctamente!")
        print("\n📝 Próximos pasos:")
        print("1. Configurar archivo .env con tu OPENAI_API_KEY")
        print("2. Ejecutar: python scripts/init_data.py")
        print("3. Ejecutar: python -m app.main")
        return True
    else:
        print("⚠️  Algunas dependencias faltan. Revisa los errores anteriores.")
        print("\n🔧 Para corregir, ejecuta:")
        print("   python install.py")
        return False

def test_app_structure():
    """Verifica que la estructura de la app esté correcta"""
    print("\n🔍 Verificando estructura de la aplicación...")
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/models.py",
        "app/api/routes.py",
        "app/services/vector_store.py",
        "app/services/llm_service.py",
        "templates/base.html",
        "templates/index.html",
        "static/css/style.css",
        "static/js/app.js",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ Estructura de archivos correcta")
        return True

if __name__ == "__main__":
    import os
    
    # Verificar imports
    imports_ok = main()
    
    # Verificar estructura
    structure_ok = test_app_structure()
    
    if imports_ok and structure_ok:
        print("\n🚀 Sistema listo para ejecutar!")
        sys.exit(0)
    else:
        print("\n⚠️  Sistema necesita correcciones antes de ejecutar")
        sys.exit(1)