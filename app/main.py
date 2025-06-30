import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema RAG para atender PQRS de la Secretaría de Infraestructura de Medellín",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de API
app.include_router(router, prefix="/api/v1", tags=["PQRS RAG API"])

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal del sistema"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.app_name,
        "app_version": settings.app_version
    })

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    """Panel de administración"""
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "app_name": settings.app_name
    })

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio de la aplicación"""
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info("Sistema RAG PQRS listo para recibir solicitudes")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre de la aplicación"""
    logger.info("Cerrando aplicación...")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )