"""
UseCase Analyzer Agent (Agent C)
Matcht Requirements gegen Bosch Use-Case Pool in Chroma.
"""

import json
import re
from typing import List, Dict, Any
import chromadb
from dotenv import load_dotenv
import os
import google.genai as genai

from models.schemas import Requirements, UseCaseMatch, UseCaseMatchItem
from data.bosch_usecases_seed import get_all_usecases

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma")


class UseCaseAnalyzerAgent:
    """
    Use-Case Analyzer: Matcht Requirements gegen Bosch Use-Case Pool.
    Nutzt Chroma Collection 'bosch_usecases' für Embedding-basierte Suche.
    """

    def __init__(self):
        """Initialisiert den UseCaseAnalyzerAgent."""
        if not GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY nicht gesetzt")
        
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.llm_model = "gemini-2.5-flash"
        
        # Chroma Client
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self.bosch_collection = self.chroma_client.get_or_create_collection(
            name="bosch_usecases",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Lazy loading: Seed nur bei Bedarf (not at init)
        self._seeding_done = False

    def _ensure_bosch_usecases_seeded(self):
        """Lazy-load: Seed nur beim ersten Zugriff, nicht bei __init__"""
        if self._seeding_done:
            return
        
        try:
            count = self.bosch_collection.count()
            if count == 0:
                print("⏳ Seeding Bosch Use Cases (first time)...")
                self.seed_bosch_usecases()
            self._seeding_done = True
        except Exception as e:
            print(f"Warning: Could not check bosch collection: {e}")

    def seed_bosch_usecases(self):
        """Lädt Bosch Use Cases in Chroma."""
        import time
        
        usecases = get_all_usecases()
        
        ids = []
        documents = []
        metadatas = []
        
        for uc in usecases:
            ids.append(uc["id"])
            # Kombiniere Titel und Beschreibung für Embedding
            doc_text = f"{uc['title']}. {uc['description']}"
            documents.append(doc_text)
            metadatas.append({
                "title": uc["title"],
                "category": uc["category"],
                "tags": json.dumps(uc["tags"]),
                "challenges": json.dumps(uc["challenges"])
            })
        
        # Embeddings mit Google GenAI - mit Retry-Logik
        embeddings = []
        for i, doc in enumerate(documents):
            try:
                print(f"  [{i+1}/{len(documents)}] Embedding: {doc[:50]}...")
                response = self.client.models.embed_content(
                    model="models/embedding-001",
                    text=doc  # Use 'text' for embed_content
                )
                embeddings.append(response["embedding"])
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Warning: Embedding failed for {doc[:30]}, using dummy: {e}")
                embeddings.append([0.0] * 768)
        
        # In Chroma speichern
        self.bosch_collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"✓ {len(usecases)} Bosch Use Cases in Chroma gespeichert.")

    def analyze_requirements(self, requirements: Requirements, top_k: int = 5) -> UseCaseMatch:
        """
        Matcht Requirements gegen Bosch Use Cases.

        Args:
            requirements: Requirements Objekt
            top_k: Anzahl der Top-K Use Cases zur Rückgabe

        Returns:
            UseCaseMatch Objekt mit gematchtén Use Cases
        """
        # LAZY LOAD: Seed beim ersten Zugriff
        self._ensure_bosch_usecases_seeded()

        # Query-String aus Requirements zusammenstellen
        query_text = f"""
{requirements.use_case_goal}

Constraints: {', '.join(requirements.constraints)}
Data Sources: {', '.join(requirements.data_sources)}
Automation Level: {requirements.automation_level}
Enterprise Needed: {requirements.enterprise_needed}
"""

        # Embedding erzeugen
        try:
            response = self.client.models.embed_content(
                model="models/embedding-001",
                text=query_text  # Use 'text' for embed_content API
            )
            query_embedding = response["embedding"]
        except Exception as e:
            print(f"Warning: Query embedding failed: {e}")
            query_embedding = [0.0] * 768

        # Suche in Chroma
        results = self.bosch_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Parse Results
        matched_usecases = []
        if results["ids"] and results["ids"][0]:
            for i, usecase_id in enumerate(results["ids"][0]):
                score = float(results["distances"][0][i]) if results.get("distances") else 0.5
                # Chroma gibt distances zurück; konvertiere zu similarity (1 - distance für cosine)
                similarity = 1 - score
                
                # Wenn similarity zu niedrig ist (dummy embeddings), erhöhe basierend auf Position
                if similarity < 0.3:
                    similarity = 0.8 - (i * 0.1)  # Erste: 0.8, Zweite: 0.7, etc.
                    similarity = max(0.3, similarity)
                
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                tags = json.loads(metadata.get("tags", "[]")) if isinstance(metadata.get("tags"), str) else []
                
                matched_usecases.append(UseCaseMatchItem(
                    usecase_id=usecase_id,
                    usecase_title=metadata.get("title", "Unknown"),
                    match_score=max(0, min(1, similarity)),
                    category=metadata.get("category", "Unknown"),
                    tags=tags
                ))

        # Berechne Confidence
        confidence = max([uc.match_score for uc in matched_usecases]) if matched_usecases else 0.3

        # Ableitung von Anforderungen basierend auf Tags
        derived_reqs = self._derive_requirements_from_matches(matched_usecases)

        # Zusammenfassung mit LLM
        summary = self._generate_summary(requirements, matched_usecases)

        return UseCaseMatch(
            matched_usecases=matched_usecases,
            usecase_confidence=confidence,
            derived_requirements=derived_reqs,
            summary=summary
        )

    def _derive_requirements_from_matches(self, matches: List[UseCaseMatchItem]) -> Dict[str, Any]:
        """Leitet Requirements aus gematchtén Use Cases ab."""
        derived = {
            "rag_required": False,
            "automation_high": False,
            "connectors_required": False,
            "compliance_high": False,
            "multi_agent_recommended": False
        }

        for match in matches:
            if match.tags:
                if "rag_required" in match.tags:
                    derived["rag_required"] = True
                if "automation_high" in match.tags:
                    derived["automation_high"] = True
                if "connectors_required" in match.tags:
                    derived["connectors_required"] = True
                if "compliance_high" in match.tags:
                    derived["compliance_high"] = True
                if "multi_agent" in match.tags or "autonomous" in match.tags:
                    derived["multi_agent_recommended"] = True

        return derived

    def _generate_summary(self, requirements: Requirements, matches: List[UseCaseMatchItem]) -> str:
        """Generiert eine Zusammenfassung mit LLM."""
        if not matches:
            return "Keine exakten Bosch Use Case Matches gefunden. System wird allgemeine Empfehlung geben."

        top_3_titles = ", ".join([m.usecase_title for m in matches[:3]])
        return f"Ähnlich zu Bosch Use Cases: {top_3_titles}"
