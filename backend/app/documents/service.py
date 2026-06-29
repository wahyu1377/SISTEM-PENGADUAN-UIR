"""
Documents service for knowledge base management.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import re

from app.core.database import Collections
from app.core.config import settings
from app.documents.schemas import DocumentCreate, DocumentUpdate, DocumentCategory
from app.complaints.rag_engine import RAGEngine

class DocumentService:
    """Service for managing knowledge base documents."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[Collections.documents]
        self.rag_engine = RAGEngine(db)

    async def create_document(
        self,
        document_data: DocumentCreate
    ) -> Dict[str, Any]:
        """Create a new document and generate embedding."""
        now = datetime.utcnow()

        # Split content into chunks
        chunks = self._split_into_chunks(document_data.content)

        # Try to generate embedding, skip if API unavailable
        embedding = None
        try:
            embedding = await self.rag_engine.get_embedding(document_data.content)
        except Exception as e:
            print(f"Warning: Could not generate embedding: {e}")

        document_doc = {
            "title": document_data.title,
            "content": document_data.content,
            "category": document_data.category.value,
            "source": document_data.source or "Manual Upload",
            "embedding": embedding,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "created_at": now,
            "updated_at": now
        }

        result = await self.collection.insert_one(document_doc)
        document_doc["_id"] = result.inserted_id

        return document_doc

    def _split_into_chunks(
        self,
        text: str,
        chunk_size: int = None,
        overlap: int = None
    ) -> List[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or settings.CHUNK_SIZE
        overlap = overlap or settings.CHUNK_OVERLAP

        # Simple sentence-based splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())

            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep overlap
                overlap_words = ' '.join(current_chunk).split()[-overlap:]
                current_chunk = [' '.join(overlap_words), sentence]
                current_length = len(overlap_words) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    async def get_document_by_id(
        self,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            document = await self.collection.find_one({"_id": ObjectId(document_id)})
            return document
        except:
            return None

    async def get_all_documents(
        self,
        page: int = 1,
        per_page: int = 10,
        category: Optional[DocumentCategory] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all documents with pagination."""
        query = {}
        if category:
            query["category"] = category.value

        total = await self.collection.count_documents(query)

        skip = (page - 1) * per_page
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)

        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            # Don't return embedding in list
            if "embedding" in doc:
                del doc["embedding"]
            documents.append(doc)

        return documents, total

    async def update_document(
        self,
        document_id: str,
        update_data: DocumentUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update a document."""
        try:
            update_dict = {k: v.value if hasattr(v, 'value') else v
                          for k, v in update_data.model_dump().items() if v is not None}

            if update_dict:
                # Regenerate embedding if content changed
                if "content" in update_dict:
                    update_dict["embedding"] = await self.rag_engine.get_embedding(update_dict["content"])
                    update_dict["chunks"] = self._split_into_chunks(update_dict["content"])
                    update_dict["chunk_count"] = len(update_dict["chunks"])

                update_dict["updated_at"] = datetime.utcnow()

                result = await self.collection.find_one_and_update(
                    {"_id": ObjectId(document_id)},
                    {"$set": update_dict},
                    return_document=True
                )
                return result

            return await self.get_document_by_id(document_id)
        except:
            return None

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except:
            return False

    async def upload_and_process_file(
        self,
        filename: str,
        content: str,
        category: DocumentCategory
    ) -> Dict[str, Any]:
        """Process uploaded file and add to knowledge base."""
        document = await self.create_document(DocumentCreate(
            title=filename,
            content=content,
            category=category,
            source=f"Uploaded: {filename}"
        ))

        return {
            "document_id": str(document["_id"]),
            "chunks_created": document.get("chunk_count", 0)
        }

    async def search_documents(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search documents by text."""
        cursor = self.collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)

        results = []
        async for doc in cursor:
            results.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", ""),
                "content": doc.get("content", "")[:200],
                "category": doc.get("category", ""),
                "source": doc.get("source", ""),
                "score": doc.get("score", 0)
            })

        return results

    async def get_statistics(self) -> Dict[str, Any]:
        """Get document statistics."""
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total_chunks": {"$sum": "$chunk_count"}
                }
            }
        ]

        stats = {}
        async for result in self.collection.aggregate(pipeline):
            stats[result["_id"]] = {
                "document_count": result["count"],
                "total_chunks": result.get("total_chunks", 0)
            }

        total_docs = await self.collection.count_documents({})

        return {
            "total_documents": total_docs,
            "by_category": stats
        }
