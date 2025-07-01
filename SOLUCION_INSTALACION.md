# Solución de Instalación - Sistema RAG PQRS

## Problemas Resueltos

### 1. Error de Python 3.13 y distutils
**Problema**: `ModuleNotFoundError: No module named 'distutils'`

**Causa**: Python 3.13 no incluye `distutils` por defecto y algunas versiones específicas en requirements.txt causaban conflictos.

**Solución aplicada**:
```bash
# Instalar herramientas del sistema necesarias
sudo apt update
sudo apt install -y python3-venv python3-dev python3-pip

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Ejecutar script de instalación automática
python install.py
```

### 2. Error de pydantic-settings
**Problema**: `BaseSettings` movido a paquete separado en Pydantic 2.x

**Solución aplicada**:
```bash
pip install pydantic-settings
```

### 3. Error de LangChain no instalado
**Problema**: `ModuleNotFoundError: No module named 'langchain'`

**Solución aplicada**: Implementamos una clase `SimpleTextSplitter` personalizada que reemplaza la funcionalidad de LangChain sin requerir la dependencia:

```python
class SimpleTextSplitter:
    """Simple text splitter implementation"""
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "! ", "? ", " "]
    
    def split_text(self, text: str) -> List[str]:
        # Implementación de división de texto sin LangChain
```

## Estado Final del Sistema

### ✅ Dependencias Instaladas
- FastAPI 
- Uvicorn
- Pydantic + pydantic-settings
- OpenAI
- ChromaDB
- Sentence Transformers
- NumPy, Pandas
- Jinja2, AioFiles
- Python-dotenv

### ✅ Base de Datos Inicializada
- **Total documentos**: 28 chunks
- **Modelo de embeddings**: all-MiniLM-L6-v2
- **Base de datos**: ChromaDB
- **Estado**: Activo y funcionando

### ✅ Archivos de Configuración
- `.env` configurado (sin OpenAI API key por ahora)
- Base de datos vectorial inicializada
- Documentos de ejemplo cargados

## Comandos para Ejecutar

### Activar entorno virtual
```bash
source venv/bin/activate
```

### Ejecutar aplicación
```bash
# Opción 1: Usando el módulo principal
python -m app.main

# Opción 2: Usando script simplificado
python start_app.py

# Opción 3: Directo con uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Verificar instalación
```bash
python test_install.py
```

### Reinicializar base de datos
```bash
python scripts/init_data.py
```

## Funcionalidades Disponibles

### 🔍 Sin OpenAI API Key
- Formulario PQRS funcional (clasificación básica)
- Búsqueda vectorial en documentos
- Panel administrativo para subir documentos
- API endpoints básicos

### 🤖 Con OpenAI API Key (opcional)
- Respuestas automáticas inteligentes
- Clasificación avanzada de PQRS
- Chat interactivo con asistente virtual
- Generación de respuestas contextuales

## URLs de Acceso

- **Aplicación principal**: http://localhost:8000
- **Panel administrativo**: http://localhost:8000/admin
- **Documentación API**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## Estructura de Archivos Críticos

```
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── config.py            # Configuración con variables de entorno
│   ├── models.py            # Modelos Pydantic
│   ├── services/
│   │   ├── vector_store.py  # Servicio ChromaDB (sin LangChain)
│   │   └── llm_service.py   # Servicio LLM para OpenAI
│   └── api/
│       └── routes.py        # Endpoints API
├── data/                    # Documentos de ejemplo
├── chroma_db/              # Base de datos vectorial
├── venv/                   # Entorno virtual
├── .env                    # Variables de entorno
└── start_app.py           # Script de inicio simplificado
```

## Resolución de Problemas Futuros

### Si ChromaDB no inicia
```bash
rm -rf chroma_db/
python scripts/init_data.py
```

### Si faltan dependencias
```bash
python install.py
```

### Si hay conflictos de versiones
```bash
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
python install.py
```

## Notas Importantes

1. **Python 3.13**: Totalmente compatible después de las correcciones
2. **Sin LangChain**: Implementación propia más liviana
3. **ChromaDB**: Funciona correctamente con embeddings locales
4. **OpenAI opcional**: Sistema funciona sin API key (modo básico)
5. **Sentence Transformers**: Modelo se descarga automáticamente en primera ejecución

## Próximos Pasos Recomendados

1. **Configurar OpenAI API Key** en `.env` para funcionalidades avanzadas
2. **Agregar más documentos** en el panel administrativo
3. **Personalizar categorías PQRS** según necesidades específicas
4. **Configurar dominio y SSL** para producción
5. **Implementar autenticación** para panel administrativo

---

**Sistema RAG PQRS - Infraestructura Medellín**  
*Instalación completada exitosamente* ✅