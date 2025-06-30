from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import logging
from typing import List
from app.models import PQRSRequest, PQRSResponse, ChatMessage, DocumentoBase, CategoriaPQRS
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/pqrs/submit", response_model=PQRSResponse)
async def submit_pqrs(pqrs: PQRSRequest):
    """Procesa una nueva PQRS y genera respuesta automática"""
    try:
        logger.info(f"Procesando nueva PQRS: {pqrs.titulo}")
        
        # Generar respuesta usando RAG
        response = llm_service.generate_pqrs_response(pqrs)
        
        logger.info(f"PQRS procesada exitosamente: {response.pqrs_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error procesando PQRS: {e}")
        raise HTTPException(status_code=500, detail="Error interno procesando la PQRS")

@router.post("/chat")
async def chat_with_assistant(message: ChatMessage):
    """Chat interactivo con el asistente de infraestructura"""
    try:
        response = llm_service.chat_response(message.mensaje, message.contexto)
        return {"respuesta": response}
        
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        raise HTTPException(status_code=500, detail="Error en el chat")

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    titulo: str = None,
    categoria: CategoriaPQRS = CategoriaPQRS.OTROS
):
    """Sube un nuevo documento a la base de conocimiento"""
    try:
        # Leer contenido del archivo
        content = await file.read()
        
        # Procesar según tipo de archivo
        if file.filename.endswith('.txt'):
            contenido = content.decode('utf-8')
        else:
            # Para otros tipos, usar el nombre del archivo como indicador
            contenido = f"Archivo: {file.filename}\nTipo: {file.content_type}\nTamaño: {len(content)} bytes"
        
        # Crear documento
        documento = DocumentoBase(
            titulo=titulo or file.filename,
            contenido=contenido,
            categoria=categoria,
            metadatos={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            }
        )
        
        # Añadir a la base vectorial
        success = vector_store.add_document(documento)
        
        if success:
            return {"mensaje": "Documento subido exitosamente", "titulo": documento.titulo}
        else:
            raise HTTPException(status_code=500, detail="Error añadiendo documento")
            
    except Exception as e:
        logger.error(f"Error subiendo documento: {e}")
        raise HTTPException(status_code=500, detail="Error subiendo documento")

@router.get("/documents/stats")
async def get_documents_stats():
    """Obtiene estadísticas de los documentos en la base de conocimiento"""
    try:
        stats = vector_store.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo estadísticas")

@router.post("/documents/search")
async def search_documents(query: str, categoria: CategoriaPQRS = None, limit: int = 5):
    """Busca documentos similares en la base de conocimiento"""
    try:
        results = vector_store.search_similar(
            query=query,
            n_results=limit,
            categoria=categoria
        )
        
        return {
            "query": query,
            "resultados": len(results),
            "documentos": results
        }
        
    except Exception as e:
        logger.error(f"Error buscando documentos: {e}")
        raise HTTPException(status_code=500, detail="Error en búsqueda")

@router.delete("/documents/clear")
async def clear_documents():
    """Limpia todos los documentos de la base de conocimiento"""
    try:
        success = vector_store.clear_collection()
        if success:
            return {"mensaje": "Base de conocimiento limpiada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error limpiando documentos")
            
    except Exception as e:
        logger.error(f"Error limpiando documentos: {e}")
        raise HTTPException(status_code=500, detail="Error limpiando documentos")

@router.get("/categories")
async def get_categories():
    """Obtiene las categorías disponibles para PQRS"""
    return {
        "categorias": [
            {
                "valor": cat.value,
                "nombre": cat.value.replace('_', ' ').title(),
                "descripcion": _get_category_description(cat)
            }
            for cat in CategoriaPQRS
        ]
    }

def _get_category_description(categoria: CategoriaPQRS) -> str:
    """Obtiene descripción de cada categoría"""
    descriptions = {
        CategoriaPQRS.VIAS_PAVIMENTOS: "Problemas con vías, pavimentos, huecos y bachaches",
        CategoriaPQRS.ALUMBRADO_PUBLICO: "Problemas con luminarias, postes de luz e iluminación",
        CategoriaPQRS.ESPACIOS_PUBLICOS: "Parques, plazas, andenes y mobiliario urbano",
        CategoriaPQRS.PUENTES_OBRAS_ARTE: "Puentes, túneles y obras de infraestructura mayor",
        CategoriaPQRS.DRENAJES_ALCANTARILLADO: "Sistemas de drenaje, alcantarillado e inundaciones",
        CategoriaPQRS.SENALIZACION: "Señales de tránsito y demarcación vial",
        CategoriaPQRS.MANTENIMIENTO_GENERAL: "Mantenimiento general de infraestructura",
        CategoriaPQRS.OTROS: "Otros temas relacionados con infraestructura"
    }
    return descriptions.get(categoria, "Sin descripción")

@router.get("/health")
async def health_check():
    """Endpoint de verificación de salud del sistema"""
    try:
        # Verificar base vectorial
        stats = vector_store.get_collection_stats()
        
        return {
            "status": "ok",
            "vector_store": stats,
            "mensaje": "Sistema RAG PQRS funcionando correctamente"
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "error",
            "mensaje": "Error en verificación de salud"
        }