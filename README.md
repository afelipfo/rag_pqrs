# Sistema RAG PQRS - Secretaría de Infraestructura Medellín

Sistema inteligente de Retrieval-Augmented Generation (RAG) para atender Peticiones, Quejas, Reclamos y Sugerencias relacionadas con la infraestructura urbana de Medellín.

## 🌟 Características Principales

- **🤖 Respuestas Inteligentes**: Sistema RAG que combina búsqueda vectorial con modelos de lenguaje
- **📋 Gestión PQRS**: Procesamiento automático de peticiones ciudadanas
- **💬 Chat Interactivo**: Asistente virtual especializado en infraestructura
- **📊 Panel Administrativo**: Gestión de documentos y estadísticas del sistema
- **🔍 Búsqueda Vectorial**: Base de conocimiento con ChromaDB
- **📱 Interfaz Moderna**: Frontend responsive con Bootstrap 5

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **ChromaDB**: Base de datos vectorial para embeddings
- **OpenAI GPT**: Modelo de lenguaje para generación de respuestas
- **Sentence Transformers**: Generación de embeddings
- **LangChain**: Framework para aplicaciones LLM

### Frontend
- **HTML5/CSS3/JavaScript**: Frontend moderno
- **Bootstrap 5**: Framework CSS responsivo
- **Font Awesome**: Iconografía
- **Jinja2**: Motor de templates

### Datos y ML
- **SentenceTransformers**: Modelo all-MiniLM-L6-v2 para embeddings
- **Búsqueda de Similitud**: Cosine similarity
- **Clasificación Automática**: Categorización de PQRS por IA

## 📁 Estructura del Proyecto

```
pqrs-rag-system/
├── app/                          # Aplicación principal
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada FastAPI
│   ├── config.py                 # Configuración
│   ├── models.py                 # Modelos Pydantic
│   ├── api/                      # Rutas de API
│   │   ├── __init__.py
│   │   └── routes.py
│   └── services/                 # Servicios de negocio
│       ├── __init__.py
│       ├── vector_store.py       # Servicio ChromaDB
│       └── llm_service.py        # Servicio LLM/RAG
├── templates/                    # Templates HTML
│   ├── base.html
│   ├── index.html
│   └── admin.html
├── static/                       # Archivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       ├── pqrs.js
│       ├── chat.js
│       └── admin.js
├── data/                         # Datos y documentos
│   └── sample_documents/
│       ├── manual_infraestructura.txt
│       └── faq_ciudadano.txt
├── scripts/                      # Scripts de utilidad
│   └── init_data.py              # Inicialización de datos
├── requirements.txt              # Dependencias Python
├── .env.example                  # Variables de entorno ejemplo
└── README.md                     # Este archivo
```

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd pqrs-rag-system
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

**Opción A: Script de instalación automática (Recomendado)**
```bash
python install.py
```

**Opción B: Instalación manual por pasos**
```bash
# Actualizar pip y herramientas básicas
pip install --upgrade pip setuptools wheel

# Para Python 3.12, instalar dependencias adicionales
pip install setuptools-scm

# Instalar dependencias principales
pip install fastapi uvicorn[standard] pydantic python-multipart
pip install openai tiktoken
pip install chromadb sentence-transformers
pip install pandas numpy jinja2 aiofiles python-dotenv requests
```

**Opción C: Usando requirements (puede fallar en Python 3.12)**
```bash
pip install -r requirements-minimal.txt
```

### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Editar `.env` con sus configuraciones:

```env
OPENAI_API_KEY=tu_clave_openai_aqui
CHROMA_DB_PATH=./data/vectordb
APP_NAME="RAG PQRS Secretaría de Infraestructura"
DEBUG=True
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### 5. Inicializar Base de Datos

```bash
python scripts/init_data.py
```

### 6. Ejecutar la Aplicación

```bash
python -m app.main
```

La aplicación estará disponible en: `http://localhost:8000`

## 📖 Uso del Sistema

### Portal Ciudadano

1. **Acceder a la Página Principal**: `http://localhost:8000`
2. **Enviar PQRS**: 
   - Completar formulario con tipo, título, descripción
   - El sistema clasificará automáticamente la categoría
   - Recibir respuesta inmediata basada en documentos oficiales
3. **Chat Interactivo**:
   - Hacer preguntas sobre infraestructura
   - Obtener respuestas contextualizadas

### Panel Administrativo

1. **Acceder**: `http://localhost:8000/admin`
2. **Subir Documentos**:
   - Cargar archivos TXT, PDF, DOCX
   - Categorizar por tipo de infraestructura
   - Los documentos se procesan automáticamente
3. **Buscar Documentos**:
   - Realizar búsquedas en la base de conocimiento
   - Ver similarity scores
4. **Gestionar Base**:
   - Ver estadísticas del sistema
   - Limpiar base de datos si es necesario

## 🔧 API Endpoints

### PQRS
- `POST /api/v1/pqrs/submit` - Enviar nueva PQRS
- `GET /api/v1/categories` - Obtener categorías disponibles

### Chat
- `POST /api/v1/chat` - Chat con asistente virtual

### Documentos
- `POST /api/v1/documents/upload` - Subir documento
- `POST /api/v1/documents/search` - Buscar documentos
- `GET /api/v1/documents/stats` - Estadísticas
- `DELETE /api/v1/documents/clear` - Limpiar base

### Sistema
- `GET /api/v1/health` - Estado del sistema

## 💡 Características del Sistema RAG

### Clasificación Automática
El sistema clasifica automáticamente las PQRS en categorías:
- **Vías y Pavimentos**: Huecos, pavimentación, bacheo
- **Alumbrado Público**: Luminarias, postes, cables
- **Espacios Públicos**: Parques, mobiliario urbano
- **Puentes y Obras**: Infraestructura mayor
- **Drenajes**: Sumideros, alcantarillado, inundaciones
- **Señalización**: Señales viales, demarcación
- **Mantenimiento General**: Otros temas

### Búsqueda Vectorial
- Utiliza embeddings de Sentence Transformers
- Búsqueda por similitud coseno
- Resultados rankeados por relevancia
- Filtrado por categorías

### Generación de Respuestas
- Contexto basado en documentos oficiales
- Respuestas personalizadas por ciudadano
- Recomendaciones específicas por categoría
- Métricas de confianza

## 📊 Datos de Ejemplo

El sistema incluye documentos de muestra:

1. **Manual de Procedimientos**: Guías oficiales de la Secretaría
2. **Preguntas Frecuentes**: Respuestas a consultas comunes
3. **Guías Específicas**: Procedimientos por categoría
4. **Información de Contacto**: Canales oficiales

## 🔒 Seguridad y Privacidad

- Validación de entrada en formularios
- Sanitización de datos HTML
- Logging de actividades
- Variables de entorno para configuración sensible

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Notas de Desarrollo

### Agregar Nuevas Categorías
1. Actualizar enum `CategoriaPQRS` en `models.py`
2. Añadir descripción en `routes.py`
3. Actualizar lógica de clasificación en `llm_service.py`

### Añadir Documentos
1. Usar panel administrativo para subir archivos
2. O ejecutar script personalizado similar a `init_data.py`

### Personalizar Respuestas
- Modificar prompts en `llm_service.py`
- Ajustar parámetros del modelo (temperatura, max_tokens)
- Actualizar lógica de recomendaciones

## 🐛 Solución de Problemas

### Error de OpenAI API
- Verificar que `OPENAI_API_KEY` esté configurada
- Comprobar cuota y límites de la API

### Error ChromaDB
- Verificar permisos en directorio `CHROMA_DB_PATH`
- Reinstalar dependencias si es necesario

### Error de Embeddings
- Verificar conexión a internet para descargar modelo
- Limpiar cache de transformers si es necesario

## 📞 Soporte

Para soporte técnico:
- Crear issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar logs de la aplicación

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

**Desarrollado para la Secretaría de Infraestructura - Alcaldía de Medellín**

Sistema RAG PQRS v1.0.0 - Mejorando la atención ciudadana con Inteligencia Artificial 🤖