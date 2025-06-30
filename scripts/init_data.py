#!/usr/bin/env python3
"""
Script para inicializar la base de datos vectorial con documentos de ejemplo.
Este script carga los documentos de muestra y los añade a ChromaDB.
"""

import os
import sys
import asyncio
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import DocumentoBase, CategoriaPQRS
from app.services.vector_store import vector_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sample_documents():
    """Carga documentos de ejemplo"""
    
    sample_docs = [
        {
            "file": "data/sample_documents/manual_infraestructura.txt",
            "titulo": "Manual de Procedimientos - Infraestructura",
            "categoria": CategoriaPQRS.MANTENIMIENTO_GENERAL,
            "metadatos": {
                "tipo": "manual",
                "fuente": "Secretaría de Infraestructura",
                "version": "2024.1"
            }
        },
        {
            "file": "data/sample_documents/faq_ciudadano.txt", 
            "titulo": "Preguntas Frecuentes - Ciudadanos",
            "categoria": CategoriaPQRS.MANTENIMIENTO_GENERAL,
            "metadatos": {
                "tipo": "faq",
                "fuente": "Atención al Ciudadano",
                "version": "2024.1"
            }
        }
    ]
    
    # Documentos específicos por categoría
    specific_docs = [
        {
            "titulo": "Guía de Reporte de Huecos",
            "contenido": """
GUÍA RÁPIDA: CÓMO REPORTAR HUECOS EN VÍAS

1. CANALES DE REPORTE:
   - Línea 123 (emergencias)
   - App MedellínMe Cuida
   - Portal web www.medellin.gov.co
   - PQRS presencial

2. INFORMACIÓN NECESARIA:
   - Ubicación exacta (dirección, barrio)
   - Tamaño aproximado del hueco
   - Nivel de peligrosidad
   - Foto si es posible

3. TIEMPOS DE RESPUESTA:
   - Vías principales: 72 horas
   - Vías secundarias: 7 días
   - Emergencias: 24 horas

4. SEGUIMIENTO:
   - Conserve el número de radicación
   - Consulte estado en línea
   - Llame si excede los tiempos

IMPORTANTE: Los huecos grandes en vías principales se consideran emergencias y deben reportarse inmediatamente al 123.
            """,
            "categoria": CategoriaPQRS.VIAS_PAVIMENTOS,
            "metadatos": {"tipo": "guia", "prioridad": "alta"}
        },
        {
            "titulo": "Procedimiento Luminarias Dañadas",
            "contenido": """
PROCEDIMIENTO: REPORTE DE LUMINARIAS DAÑADAS

TIPOS DE DAÑOS COMUNES:
- Bombilla fundida o parpadeante
- Poste inclinado o dañado
- Cables sueltos o expuestos
- Luminaria apagada en horario nocturno

CÓMO REPORTAR:
1. Identifique la ubicación exacta
2. Tome nota del número de poste (si visible)
3. Describa el tipo de daño
4. Indique si representa peligro inmediato

CANALES:
- Línea 123 (para emergencias eléctricas)
- EPM: 4444115
- App MedellínMe Cuida
- PQRS Secretaría de Infraestructura

TIEMPOS:
- Zonas céntricas: 48 horas
- Zonas periféricas: 96 horas  
- Emergencias eléctricas: 12 horas

EMERGENCIAS: Cables caídos o sueltos requieren atención inmediata. Llame al 123 y manténgase alejado del área.
            """,
            "categoria": CategoriaPQRS.ALUMBRADO_PUBLICO,
            "metadatos": {"tipo": "procedimiento", "urgencia": "media"}
        },
        {
            "titulo": "Mantenimiento de Parques y Zonas Verdes",
            "contenido": """
MANTENIMIENTO DE PARQUES - INFORMACIÓN CIUDADANA

ACTIVIDADES REGULARES:
- Corte de césped cada 15 días
- Poda de árboles según cronograma técnico
- Mantenimiento de juegos infantiles
- Limpieza de senderos y mobiliario
- Revisión de sistemas de riego

QUÉ PUEDEN REPORTAR LOS CIUDADANOS:
- Juegos infantiles dañados o peligrosos
- Bancas deterioradas
- Problemas de iluminación
- Daños en senderos
- Árboles que requieren poda
- Problemas con vegetación

PROGRAMA "ADOPTA UN PARQUE":
- Participación comunitaria en cuidado
- Capacitación en mantenimiento básico
- Suministro de herramientas
- Acompañamiento técnico

REPORTES:
- Use App MedellínMe Cuida
- PQRS en línea o presencial
- Línea 385 5555

La comunidad es clave en el cuidado de los espacios públicos. Su reporte oportuno ayuda a mantener parques seguros y agradables.
            """,
            "categoria": CategoriaPQRS.ESPACIOS_PUBLICOS,
            "metadatos": {"tipo": "informativo", "programa": "adopta_parque"}
        },
        {
            "titulo": "Prevención de Inundaciones - Drenajes",
            "contenido": """
PREVENCIÓN DE INUNDACIONES - CUIDADO DE DRENAJES

CAUSAS COMUNES DE INUNDACIONES:
- Sumideros tapados por basura
- Obstrucción de canales y quebradas
- Inadecuado mantenimiento de alcantarillas
- Construcciones que bloquean drenajes naturales

RESPONSABILIDADES CIUDADANAS:
- No arrojar basura a sumideros
- No verter aceites o químicos al drenaje
- Reportar obstrucciones inmediatamente
- Mantener limpios los frentes de las casas

CÓMO REPORTAR PROBLEMAS DE DRENAJE:
- Sumideros tapados
- Canales obstruidos
- Inundaciones recurrentes
- Daños en infraestructura de drenaje

TEMPORADA DE LLUVIAS:
- Mantenimiento preventivo intensivo
- Limpieza programada de sumideros
- Monitoreo de puntos críticos
- Brigadas de emergencia

EMERGENCIAS:
- Inundaciones activas: Línea 123
- Situaciones no urgentes: PQRS

RECUERDE: La prevención es responsabilidad de todos. Un sumidero limpio puede evitar inundaciones en su barrio.
            """,
            "categoria": CategoriaPQRS.DRENAJES_ALCANTARILLADO,
            "metadatos": {"tipo": "preventivo", "temporada": "lluvias"}
        },
        {
            "titulo": "Señalización Vial - Mantenimiento y Solicitudes",
            "contenido": """
SEÑALIZACIÓN VIAL - INFORMACIÓN PARA CIUDADANOS

TIPOS DE SEÑALIZACIÓN:
- Señales verticales (informativas, preventivas, reglamentarias)
- Demarcación horizontal (cebras, carriles, flechas)
- Señales de nomenclatura (nombres de calles)
- Semáforos y dispositivos electrónicos

PROBLEMAS COMUNES:
- Señales vandalizadas o deterioradas
- Demarcación borrada o poco visible
- Señales tapadas por vegetación
- Nomenclatura incorrecta o faltante

CÓMO SOLICITAR NUEVA SEÑALIZACIÓN:
1. Identifique la necesidad específica
2. Justifique la solicitud (seguridad, flujo vehicular)
3. Proporcione ubicación exacta
4. Presente PQRS con esta información

MANTENIMIENTO PROGRAMADO:
- Repintado anual de demarcación
- Revisión trimestral de señales
- Reemplazo según vida útil
- Actualización por cambios viales

REPORTES URGENTES:
- Señales críticas caídas o dañadas
- Semáforos intermitentes o apagados
- Demarcación peligrosamente borrada

La señalización adecuada es fundamental para la seguridad vial. Su reporte ayuda a mantener las vías seguras para todos.
            """,
            "categoria": CategoriaPQRS.SENALIZACION,
            "metadatos": {"tipo": "informativo", "seguridad": "vial"}
        }
    ]
    
    return sample_docs, specific_docs

async def init_database():
    """Inicializa la base de datos con documentos de ejemplo"""
    
    logger.info("🚀 Iniciando carga de documentos de ejemplo...")
    
    try:
        # Cargar documentos de archivos
        sample_docs, specific_docs = load_sample_documents()
        
        # Procesar archivos
        for doc_info in sample_docs:
            file_path = doc_info["file"]
            
            if os.path.exists(file_path):
                logger.info(f"📄 Cargando {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                documento = DocumentoBase(
                    titulo=doc_info["titulo"],
                    contenido=contenido,
                    categoria=doc_info["categoria"],
                    metadatos=doc_info["metadatos"]
                )
                
                success = vector_store.add_document(documento)
                if success:
                    logger.info(f"✅ Documento '{documento.titulo}' añadido exitosamente")
                else:
                    logger.error(f"❌ Error añadiendo '{documento.titulo}'")
            else:
                logger.warning(f"⚠️  Archivo no encontrado: {file_path}")
        
        # Procesar documentos específicos
        for doc_data in specific_docs:
            logger.info(f"📝 Creando documento: {doc_data['titulo']}")
            
            documento = DocumentoBase(
                titulo=doc_data["titulo"],
                contenido=doc_data["contenido"],
                categoria=doc_data["categoria"],
                metadatos=doc_data["metadatos"]
            )
            
            success = vector_store.add_document(documento)
            if success:
                logger.info(f"✅ Documento '{documento.titulo}' añadido exitosamente")
            else:
                logger.error(f"❌ Error añadiendo '{documento.titulo}'")
        
        # Obtener estadísticas finales
        stats = vector_store.get_collection_stats()
        logger.info(f"📊 Base de datos inicializada:")
        logger.info(f"   - Total documentos: {stats['total_documentos']}")
        logger.info(f"   - Estado: {stats['status']}")
        
        logger.info("🎉 Inicialización completada exitosamente!")
        
    except Exception as e:
        logger.error(f"💥 Error durante la inicialización: {e}")
        raise

def main():
    """Función principal"""
    try:
        # Ejecutar inicialización
        asyncio.run(init_database())
        
    except KeyboardInterrupt:
        logger.info("⏹️  Inicialización cancelada por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()