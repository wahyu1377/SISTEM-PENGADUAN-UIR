"""
RAG (Retrieval-Augmented Generation) Engine for complaint analysis.
Supports both OpenAI and Google Gemini APIs.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.core.database import Collections
from app.complaints.schemas import RAGAnalysisResult

# Try importing both AI providers
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class RAGEngine:
    """RAG Engine for analyzing complaints using AI and knowledge base."""

    def __init__(self, db):
        self.db = db
        self.collection = db[Collections.documents]
        self.use_gemini = GEMINI_AVAILABLE and settings.GEMINI_API_KEY
        self.use_openai = OPENAI_AVAILABLE and settings.OPENAI_API_KEY

        # Initialize Gemini if available
        if self.use_gemini:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
            print("Using Gemini AI for RAG")
        elif self.use_openai:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            print("Using OpenAI for RAG")
        else:
            print("WARNING: No AI provider configured for RAG")

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using available AI provider."""
        if self.use_gemini:
            try:
                return await self._get_gemini_embedding(text)
            except:
                return self._simple_embedding(text)
        elif self.use_openai:
            try:
                return await self._get_openai_embedding(text)
            except:
                return self._simple_embedding(text)
        else:
            # Return simple embedding for testing without AI
            return self._simple_embedding(text)

    async def _get_gemini_embedding(self, text: str) -> List[float]:
        """Get embedding using Gemini."""
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Gemini embedding error: {e}")
            # Fallback to simple hash-based embedding
            return self._simple_embedding(text)

    async def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding using OpenAI."""
        response = await self.openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    async def retrieve_relevant_documents(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from knowledge base using vector search."""
        try:
            # Get query embedding
            query_embedding = await self.get_embedding(query)

            # Use MongoDB Atlas vector search
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": 20,
                        "limit": top_k
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "title": 1,
                        "content": 1,
                        "category": 1,
                        "source": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]

            results = []
            async for doc in self.collection.aggregate(pipeline):
                results.append(doc)

            return results
        except Exception as e:
            print(f"Vector search error: {e}")
            # Fallback to text search
            return await self._text_search(query, top_k)

    async def _text_search(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Fallback text search when vector search is unavailable."""
        cursor = self.collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)

        results = []
        async for doc in cursor:
            results.append({
                "_id": doc["_id"],
                "title": doc.get("title", ""),
                "content": doc.get("content", ""),
                "category": doc.get("category", ""),
                "source": doc.get("source", ""),
                "score": doc.get("score", 0)
            })
        return results

    def _simple_embedding(self, text: str) -> List[float]:
        """Generate a simple hash-based embedding when no AI is available."""
        import hashlib
        # Create a pseudo-embedding based on text hash
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        # Generate embedding matching configured dimensions
        embedding = []
        dimensions = settings.EMBEDDING_DIMENSIONS
        for i in range(dimensions):
            seed = (hash_val + i * 31) % 1000
            embedding.append((seed % 200 - 100) / 100.0)
        return embedding

    def construct_analysis_prompt(
        self,
        complaint_text: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> str:
        """Construct prompt for LLM analysis with retrieved context."""
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            content = doc.get('content', '')[:500] if doc.get('content') else ''
            context_parts.append(
                f"[Dokumen {i}] {doc.get('title', 'Tanpa Judul')}\n"
                f"Sumber: {doc.get('source', 'Tidak diketahui')}\n"
                f"Konten: {content}..."
            )

        context = "\n\n".join(context_parts) if context_parts else "Tidak ada dokumen referensi yang relevan."

        prompt = f"""Anda adalah AI Analyst untuk Sistem Pengaduan Mahasiswa Universitas Islam Riau.

Tugas Anda adalah menganalisis pengaduan mahasiswa dan memberikan rekomendasi berdasarkan dokumen referensi resmi universitas.

## PENGADUAN YANG PERLU DIANALISIS:
{complaint_text}

## DOKUMEN REFERENSI:
{context}

## FORMAT OUTPUT (JSON):
{{
    "category": "Kategori pengaduan (Pilih dari: Akademik, Fasilitas Kampus, Perpustakaan, Teknologi Informasi, Administrasi, Keamanan & Keselamatan, Lainnya)",
    "priority": "Tingkat prioritas (high/medium/low)",
    "summary": "Ringkasan pengaduan dalam 2-3 kalimat",
    "recommended_unit": "Unit kerja yang direkomendasikan untuk menangani",
    "reason": "Alasan mengapa unit tersebut direkomendasikan (berdasarkan dokumen referensi)",
    "confidence_score": Nilai keyakinan (0.0 - 1.0)
}}

## CATATAN PENTING:
- Prioritas HIGH: Affects banyak mahasiswa, isu kesehatan/keselamatan
- Prioritas MEDIUM: Affects mahasiswa individu, tidak urgent
- Prioritas LOW: Pertanyaan umum, saran
- Jika confidence_score < 0.5, berarti analisis kurang yakin
- Jawaban hanya dalam format JSON, tanpa teks tambahan
"""
        return prompt

    async def analyze_complaint(
        self,
        title: str,
        description: str
    ) -> RAGAnalysisResult:
        """Analyze a complaint using RAG approach."""
        complaint_text = f"Judul: {title}\n\nDeskripsi: {description}"

        # Step 1: Retrieve relevant documents
        retrieved_docs = await self.retrieve_relevant_documents(
            complaint_text,
            top_k=settings.MAX_DOCUMENTS_RETRIEVED
        )

        # Step 2: Construct prompt with context
        prompt = self.construct_analysis_prompt(complaint_text, retrieved_docs)

        # Step 3: Generate analysis using LLM
        try:
            if self.use_gemini:
                return await self._analyze_with_gemini(prompt, description)
            elif self.use_openai:
                return await self._analyze_with_openai(prompt)
            else:
                # Fallback: Simple rule-based analysis
                return self._rule_based_analysis(title, description)
        except Exception as e:
            print(f"LLM Analysis error: {e}")
            return self._rule_based_analysis(title, description)

    async def _analyze_with_gemini(self, prompt: str, description: str) -> RAGAnalysisResult:
        """Analyze using Gemini API."""
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    'response_mime_type': 'application/json',
                }
            )

            # Parse JSON response
            response_text = response.text.strip()
            # Clean up if there's markdown code block
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            analysis_data = json.loads(response_text.strip())

            return RAGAnalysisResult(
                category=analysis_data.get("category", "Lainnya"),
                priority=analysis_data.get("priority", "medium"),
                summary=analysis_data.get("summary", ""),
                recommended_unit=analysis_data.get("recommended_unit", "Admin"),
                reason=analysis_data.get("reason", ""),
                confidence_score=float(analysis_data.get("confidence_score", 0.5))
            )
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            raise

    async def _analyze_with_openai(self, prompt: str) -> RAGAnalysisResult:
        """Analyze using OpenAI API."""
        response = await self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Anda adalah AI Analyst yang membantu menganalisis pengaduan mahasiswa. Selalu berikan jawaban dalam format JSON yang valid."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        analysis_text = response.choices[0].message.content
        analysis_data = json.loads(analysis_text)

        return RAGAnalysisResult(
            category=analysis_data.get("category", "Lainnya"),
            priority=analysis_data.get("priority", "medium"),
            summary=analysis_data.get("summary", ""),
            recommended_unit=analysis_data.get("recommended_unit", ""),
            reason=analysis_data.get("reason", ""),
            confidence_score=analysis_data.get("confidence_score", 0.5)
        )

    def _rule_based_analysis(self, title: str, description: str) -> RAGAnalysisResult:
        """Simple rule-based analysis when no AI is available."""
        text = (title + " " + description).lower()

        # Simple keyword matching
        if any(word in text for word in ['ac', 'ac:', 'pending', 'rusak', 'kondisi', 'ruangan', 'kursi', 'meja', 'lampu', 'toilet']):
            category = "Fasilitas Kampus"
            unit = "Bagian Umum & Fasilitas"
        elif any(word in text for word in ['wifi', 'internet', 'jaringan', 'komputer', 'lab', 'printer', 'sistem', 'website']):
            category = "Teknologi Informasi"
            unit = "Unit IT"
        elif any(word in text for word in ['buku', 'perpustakaan', 'pinjam', 'denda', 'ruang baca']):
            category = "Perpustakaan"
            unit = "Perpustakaan"
        elif any(word in text for word in ['nilai', 'dosen', 'ajar', 'ujian', 'jadwal', 'matakuliah', 'krs', 'irs']):
            category = "Akademik"
            unit = "Bagian Akademik"
        elif any(word in text for word in ['uang', 'ukt', 'pembayaran', 'beasiswa', 'bayar']):
            category = "Administrasi"
            unit = "Bagian Keuangan"
        elif any(word in text for word in ['keamanan', 'safety', 'keselamatan', 'kebakaran', 'darurat']):
            category = "Keamanan & Keselamatan"
            unit = "Tim K3 & Keamanan"
        else:
            category = "Lainnya"
            unit = "Admin"

        return RAGAnalysisResult(
            category=category,
            priority="medium",
            summary=description[:200] + "..." if len(description) > 200 else description,
            recommended_unit=unit,
            reason="Analisis berdasarkan kata kunci dalam pengaduan.",
            confidence_score=0.6
        )

    async def add_document(
        self,
        title: str,
        content: str,
        category: str,
        source: str = "Manual Upload"
    ) -> str:
        """Add a document to the knowledge base with embedding."""
        try:
            embedding = await self.get_embedding(content)
        except:
            embedding = None

        doc = {
            "title": title,
            "content": content,
            "category": category,
            "source": source,
            "embedding": embedding,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def process_document_file(
        self,
        filename: str,
        content: str,
        category: str
    ) -> str:
        """Process uploaded document file and add to knowledge base."""
        return await self.add_document(
            title=filename,
            content=content,
            category=category,
            source=f"Uploaded: {filename}"
        )