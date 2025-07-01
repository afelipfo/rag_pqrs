import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.models import DocumentoBase, CategoriaPQRS

logger = logging.getLogger(__name__)

class SimpleTextSplitter:
    """Simple text splitter implementation"""
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "! ", "? ", " "]
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Find the best split point
            chunk_end = end
            for sep in self.separators:
                sep_pos = text.rfind(sep, start, end)
                if sep_pos != -1:
                    chunk_end = sep_pos + len(sep)
                    break
            
            chunks.append(text[start:chunk_end])
            start = chunk_end - self.chunk_overlap
            
            if start <= 0:
                start = chunk_end
        
        return chunks

class VectorStoreService:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embeddings_model = None
        self.text_splitter = SimpleTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self._initialize()
    
    def _initialize(self):
        """Inicializa la base de datos vectorial y el modelo de embeddings"""
        try:
            # Crear directorio si no existe
            os.makedirs(settings.chroma_db_path, exist_ok=True)
            
            # Inicializar ChromaDB
            self.client = chromadb.PersistentClient(
                path=settings.chroma_db_path,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Crear o obtener colección
            self.collection = self.client.get_or_create_collection(
                name="pqrs_infraestructura",
                metadata={"description": "Documentos de infraestructura para PQRS"}
            )
            
            # Inicializar modelo de embeddings
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Vector store inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando vector store: {e}")
            raise
    
    def add_document(self, documento: DocumentoBase) -> bool:
        """Añade un documento a la base de datos vectorial"""
        try:
            # Dividir documento en chunks
            chunks = self.text_splitter.split_text(documento.contenido)
            
            # Generar embeddings para cada chunk
            embeddings = self.embeddings_model.encode(chunks).tolist()
            
            # Preparar metadatos
            for i, chunk in enumerate(chunks):
                doc_id = f"{documento.titulo}_{i}"
                metadata = {
                    "titulo": documento.titulo,
                    "categoria": documento.categoria.value,
                    "chunk_index": i,
                    "fecha_creacion": documento.fecha_creacion.isoformat(),
                    **documento.metadatos
                }
                
                # Añadir a la colección
                self.collection.add(
                    embeddings=[embeddings[i]],
                    documents=[chunk],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            
            logger.info(f"Documento '{documento.titulo}' añadido con {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo documento: {e}")
            return False
    
    def search_similar(self, query: str, n_results: int = 5, categoria: Optional[CategoriaPQRS] = None) -> List[Dict[str, Any]]:
        """Busca documentos similares a la consulta"""
        try:
            # Generar embedding de la consulta
            query_embedding = self.embeddings_model.encode([query]).tolist()[0]
            
            # Preparar filtros
            where_filter = {}
            if categoria:
                where_filter["categoria"] = categoria.value
            
            # Realizar búsqueda
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Formatear resultados
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "documento": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similitud": 1 - results["distances"][0][i],  # Convertir distancia a similitud
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la colección"""
        try:
            count = self.collection.count()
            return {
                "total_documentos": count,
                "status": "activo" if count > 0 else "vacío"
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"total_documentos": 0, "status": "error"}
    
    def clear_collection(self) -> bool:
        """Limpia toda la colección"""
        try:
            # Obtener todos los IDs
            all_results = self.collection.get()
            if all_results["ids"]:
                self.collection.delete(ids=all_results["ids"])
            logger.info("Colección limpiada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error limpiando colección: {e}")
            return False

# Instancia global del servicio
vector_store = VectorStoreService()