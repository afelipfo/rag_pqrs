from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TipoPQRS(str, Enum):
    PETICION = "peticion"
    QUEJA = "queja"
    RECLAMO = "reclamo"
    SUGERENCIA = "sugerencia"

class CategoriaPQRS(str, Enum):
    VIAS_PAVIMENTOS = "vias_pavimentos"
    ALUMBRADO_PUBLICO = "alumbrado_publico"
    ESPACIOS_PUBLICOS = "espacios_publicos"
    PUENTES_OBRAS_ARTE = "puentes_obras_arte"
    DRENAJES_ALCANTARILLADO = "drenajes_alcantarillado"
    SENALIZACION = "senalizacion"
    MANTENIMIENTO_GENERAL = "mantenimiento_general"
    OTROS = "otros"

class PQRSRequest(BaseModel):
    tipo: TipoPQRS = Field(..., description="Tipo de PQRS")
    categoria: Optional[CategoriaPQRS] = Field(None, description="Categoría de infraestructura")
    titulo: str = Field(..., min_length=5, max_length=200, description="Título de la PQRS")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada")
    ubicacion: Optional[str] = Field(None, description="Ubicación específica en Medellín")
    ciudadano_nombre: str = Field(..., description="Nombre del ciudadano")
    ciudadano_email: str = Field(..., description="Email del ciudadano")
    ciudadano_telefono: Optional[str] = Field(None, description="Teléfono del ciudadano")

class PQRSResponse(BaseModel):
    pqrs_id: str = Field(..., description="ID único de la PQRS")
    respuesta: str = Field(..., description="Respuesta generada por el sistema RAG")
    documentos_referencia: List[str] = Field(default=[], description="Documentos utilizados como referencia")
    confianza: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza de la respuesta")
    categoria_detectada: CategoriaPQRS = Field(..., description="Categoría detectada automáticamente")
    tiempo_respuesta: float = Field(..., description="Tiempo de procesamiento en segundos")
    recomendaciones: List[str] = Field(default=[], description="Recomendaciones adicionales")

class DocumentoBase(BaseModel):
    titulo: str = Field(..., description="Título del documento")
    contenido: str = Field(..., description="Contenido del documento")
    categoria: CategoriaPQRS = Field(..., description="Categoría del documento")
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    metadatos: dict = Field(default={}, description="Metadatos adicionales")

class ChatMessage(BaseModel):
    mensaje: str = Field(..., min_length=1, description="Mensaje del usuario")
    contexto: Optional[str] = Field(None, description="Contexto adicional")