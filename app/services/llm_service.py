import logging
import time
from typing import List, Dict, Any, Optional
import openai
from app.config import settings
from app.models import PQRSRequest, PQRSResponse, CategoriaPQRS
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-3.5-turbo"
        
    def classify_pqrs(self, titulo: str, descripcion: str) -> CategoriaPQRS:
        """Clasifica automáticamente una PQRS según su contenido"""
        try:
            prompt = f"""
            Analiza el siguiente título y descripción de una PQRS relacionada con infraestructura urbana de Medellín:
            
            Título: {titulo}
            Descripción: {descripcion}
            
            Clasifica esta PQRS en una de las siguientes categorías:
            - vias_pavimentos: Problemas con vías, pavimentos, huecos, bachaches
            - alumbrado_publico: Problemas con luminarias, postes de luz, iluminación
            - espacios_publicos: Parques, plazas, andenes, mobiliario urbano
            - puentes_obras_arte: Puentes, túneles, obras de infraestructura mayor
            - drenajes_alcantarillado: Sistemas de drenaje, alcantarillado, inundaciones
            - senalizacion: Señales de tránsito, demarcación vial
            - mantenimiento_general: Mantenimiento general de infraestructura
            - otros: Cualquier otro tema de infraestructura
            
            Responde únicamente con el nombre de la categoría (sin comillas):
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            categoria_text = response.choices[0].message.content.strip().lower()
            
            # Mapear respuesta a enum
            categoria_map = {
                "vias_pavimentos": CategoriaPQRS.VIAS_PAVIMENTOS,
                "alumbrado_publico": CategoriaPQRS.ALUMBRADO_PUBLICO,
                "espacios_publicos": CategoriaPQRS.ESPACIOS_PUBLICOS,
                "puentes_obras_arte": CategoriaPQRS.PUENTES_OBRAS_ARTE,
                "drenajes_alcantarillado": CategoriaPQRS.DRENAJES_ALCANTARILLADO,
                "senalizacion": CategoriaPQRS.SENALIZACION,
                "mantenimiento_general": CategoriaPQRS.MANTENIMIENTO_GENERAL,
                "otros": CategoriaPQRS.OTROS
            }
            
            return categoria_map.get(categoria_text, CategoriaPQRS.OTROS)
            
        except Exception as e:
            logger.error(f"Error clasificando PQRS: {e}")
            return CategoriaPQRS.OTROS
    
    def generate_pqrs_response(self, pqrs: PQRSRequest) -> PQRSResponse:
        """Genera una respuesta completa para una PQRS usando RAG"""
        start_time = time.time()
        
        try:
            # 1. Clasificar automáticamente si no se proporcionó categoría
            categoria_detectada = pqrs.categoria or self.classify_pqrs(pqrs.titulo, pqrs.descripcion)
            
            # 2. Buscar documentos relevantes
            query = f"{pqrs.titulo} {pqrs.descripcion}"
            documentos_relevantes = vector_store.search_similar(
                query=query,
                n_results=5,
                categoria=categoria_detectada
            )
            
            # 3. Preparar contexto
            contexto_docs = "\n\n".join([
                f"Documento: {doc['metadata']['titulo']}\nContenido: {doc['documento']}"
                for doc in documentos_relevantes
            ])
            
            # 4. Generar respuesta usando LLM
            respuesta = self._generate_response_with_context(pqrs, contexto_docs, categoria_detectada)
            
            # 5. Generar recomendaciones
            recomendaciones = self._generate_recommendations(pqrs, categoria_detectada)
            
            # 6. Calcular tiempo de respuesta
            tiempo_respuesta = time.time() - start_time
            
            # 7. Calcular confianza basada en similitud de documentos
            confianza = self._calculate_confidence(documentos_relevantes)
            
            return PQRSResponse(
                pqrs_id=f"PQRS_{int(time.time())}",
                respuesta=respuesta,
                documentos_referencia=[doc['metadata']['titulo'] for doc in documentos_relevantes],
                confianza=confianza,
                categoria_detectada=categoria_detectada,
                tiempo_respuesta=tiempo_respuesta,
                recomendaciones=recomendaciones
            )
            
        except Exception as e:
            logger.error(f"Error generando respuesta PQRS: {e}")
            # Respuesta de fallback
            return PQRSResponse(
                pqrs_id=f"PQRS_ERROR_{int(time.time())}",
                respuesta="Lo sentimos, hubo un error procesando su solicitud. Por favor contacte directamente a la Secretaría de Infraestructura.",
                documentos_referencia=[],
                confianza=0.0,
                categoria_detectada=CategoriaPQRS.OTROS,
                tiempo_respuesta=time.time() - start_time,
                recomendaciones=["Contactar directamente a la Secretaría de Infraestructura"]
            )
    
    def _generate_response_with_context(self, pqrs: PQRSRequest, contexto: str, categoria: CategoriaPQRS) -> str:
        """Genera respuesta usando el contexto de documentos relevantes"""
        tipo_str = {
            "peticion": "petición",
            "queja": "queja", 
            "reclamo": "reclamo",
            "sugerencia": "sugerencia"
        }.get(pqrs.tipo.value, "solicitud")
        
        prompt = f"""
        Eres un asistente especializado de la Secretaría de Infraestructura de la Alcaldía de Medellín.
        Debes responder a una {tipo_str} de un ciudadano de manera profesional, empática y útil.
        
        INFORMACIÓN DE LA {tipo_str.upper()}:
        - Tipo: {tipo_str}
        - Categoría: {categoria.value.replace('_', ' ').title()}
        - Título: {pqrs.titulo}
        - Descripción: {pqrs.descripcion}
        - Ubicación: {pqrs.ubicacion or "No especificada"}
        - Ciudadano: {pqrs.ciudadano_nombre}
        
        CONTEXTO DE DOCUMENTOS RELEVANTES:
        {contexto}
        
        INSTRUCCIONES:
        1. Saluda al ciudadano por su nombre de manera cordial
        2. Reconoce su {tipo_str} y agradece su participación ciudadana
        3. Proporciona información específica basada en los documentos de contexto
        4. Si es una queja o reclamo, muestra empatía y explica los procedimientos
        5. Si es una petición, explica el proceso y tiempos estimados
        6. Si es una sugerencia, agradece la propuesta y explica cómo se evalúa
        7. Proporciona información de contacto para seguimiento
        8. Mantén un tono profesional pero cercano
        9. No inventes información que no esté en el contexto
        
        Respuesta:
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_recommendations(self, pqrs: PQRSRequest, categoria: CategoriaPQRS) -> List[str]:
        """Genera recomendaciones específicas según la categoría"""
        base_recommendations = [
            "Conserve el número de radicación para futuras consultas",
            "Puede hacer seguimiento a través del portal web de la Alcaldía",
            "En caso de emergencia, contacte la línea 123"
        ]
        
        category_recommendations = {
            CategoriaPQRS.VIAS_PAVIMENTOS: [
                "Reporte huecos grandes que representen peligro inmediatamente",
                "Proporcione fotos si es posible para acelerar la evaluación"
            ],
            CategoriaPQRS.ALUMBRADO_PUBLICO: [
                "Reporte luminarias dañadas para mejorar la seguridad",
                "En caso de cables caídos, mantenga distancia y reporte inmediatamente"
            ],
            CategoriaPQRS.ESPACIOS_PUBLICOS: [
                "Participe en jornadas comunitarias de mejoramiento",
                "Reporte vandalismo para mantenimiento preventivo"
            ]
        }
        
        specific_recs = category_recommendations.get(categoria, [])
        return base_recommendations + specific_recs
    
    def _calculate_confidence(self, documentos: List[Dict[str, Any]]) -> float:
        """Calcula el nivel de confianza basado en la similitud de documentos"""
        if not documentos:
            return 0.0
        
        # Promedio de similitudes
        similitudes = [doc['similitud'] for doc in documentos]
        promedio_similitud = sum(similitudes) / len(similitudes)
        
        # Ajustar confianza (mínimo 0.3, máximo 0.95)
        confianza = max(0.3, min(0.95, promedio_similitud))
        
        return round(confianza, 2)
    
    def chat_response(self, mensaje: str, contexto: Optional[str] = None) -> str:
        """Genera respuesta para chat general sobre infraestructura"""
        try:
            # Buscar documentos relevantes
            documentos_relevantes = vector_store.search_similar(mensaje, n_results=3)
            
            contexto_docs = "\n\n".join([
                f"Documento: {doc['metadata']['titulo']}\nContenido: {doc['documento']}"
                for doc in documentos_relevantes
            ])
            
            prompt = f"""
            Eres un asistente de la Secretaría de Infraestructura de Medellín.
            Responde de manera útil y profesional a la pregunta del ciudadano.
            
            Pregunta: {mensaje}
            
            Contexto adicional: {contexto or "No disponible"}
            
            Información relevante:
            {contexto_docs}
            
            Proporciona una respuesta útil, concisa y basada en la información disponible.
            Si no tienes información suficiente, recomienda contactar directamente a la Secretaría.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error en chat response: {e}")
            return "Lo siento, no puedo procesar tu consulta en este momento. Por favor contacta directamente a la Secretaría de Infraestructura."

# Instancia global del servicio
llm_service = LLMService()