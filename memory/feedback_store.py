"""
Feedback Store
Persistiert Session Feedback in JSON und optionaler Chroma Collection.
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import chromadb

from models.schemas import SessionFeedback

# Feedback JSON Store Path
FEEDBACK_DIR = Path("./data/feedback")
FEEDBACK_FILE = FEEDBACK_DIR / "sessions.jsonl"

# Chroma
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma")


class FeedbackStore:
    """
    Speichert und verwaltet Session Feedback.
    
    - JSON-File für einfachen Zugriff
    - Optional Chroma Collection für spätere RAG/Learnings
    """

    def __init__(self, use_chroma: bool = True):
        """
        Initialisiert FeedbackStore.

        Args:
            use_chroma: Ob Feedback auch in Chroma gespeichert werden soll
        """
        self.use_chroma = use_chroma

        # Stelle sicher dass Feedback-Dir existiert
        FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

        # Chroma vorbereiten
        if use_chroma:
            os.makedirs(CHROMA_DB_DIR, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
            self.feedback_collection = self.chroma_client.get_or_create_collection(
                name="session_feedback",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.feedback_collection = None

    def save_feedback(self, feedback: SessionFeedback) -> None:
        """
        Speichert Feedback persistent.

        Args:
            feedback: SessionFeedback Objekt
        """

        # In JSON-File schreiben (append mode)
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(feedback.model_dump_json() + "\n")

        print(f"✓ Feedback gespeichert: {feedback.session_id}")

        # Optional: In Chroma speichern für Learnings
        if self.use_chroma and self.feedback_collection:
            self._save_to_chroma(feedback)

    def _save_to_chroma(self, feedback: SessionFeedback) -> None:
        """Speichert Feedback auch in Chroma."""
        try:
            import google.genai as genai

            # Embeddings für Feedback-Text
            feedback_text = f"Rating: {feedback.rating}/5. Helpful: {feedback.helpful}. Comment: {feedback.comment or 'N/A'}"

            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            embedding = client.models.embed_content(
                model="models/embedding-001",
                text=feedback_text
            )["embedding"]

            self.feedback_collection.add(
                ids=[feedback.session_id],
                documents=[feedback_text],
                embeddings=[embedding],
                metadatas={
                    "rating": feedback.rating,
                    "helpful": feedback.helpful,
                    "timestamp": feedback.timestamp.isoformat()
                }
            )
        except Exception as e:
            print(f"Warning: Chroma feedback save failed: {e}")

    def load_feedback_for_session(self, session_id: str) -> Optional[SessionFeedback]:
        """
        Lädt Feedback für eine bestimmte Session.

        Args:
            session_id: Session ID

        Returns:
            SessionFeedback oder None
        """
        if not FEEDBACK_FILE.exists():
            return None

        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            for line in f:
                feedback_data = json.loads(line)
                if feedback_data.get("session_id") == session_id:
                    return SessionFeedback(**feedback_data)

        return None

    def load_all_feedback(self, limit: int = 100) -> List[SessionFeedback]:
        """
        Lädt alle Feedbacks.

        Args:
            limit: Maximale Anzahl zu laden

        Returns:
            Liste von SessionFeedback
        """
        feedbacks = []

        if not FEEDBACK_FILE.exists():
            return feedbacks

        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                try:
                    feedback_data = json.loads(line)
                    feedbacks.append(SessionFeedback(**feedback_data))
                except Exception as e:
                    print(f"Warning: Could not parse feedback line: {e}")

        return feedbacks

    def get_feedback_stats(self) -> dict:
        """
        Gibt Statistiken über Feedbacks zurück.

        Returns:
            Dict mit Statistiken (avg_rating, helpful_count, etc.)
        """
        feedbacks = self.load_all_feedback(limit=1000)

        if not feedbacks:
            return {
                "total": 0,
                "average_rating": 0,
                "helpful_count": 0,
                "unhelpful_count": 0
            }

        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
        helpful_count = sum(1 for f in feedbacks if f.helpful)
        unhelpful_count = len(feedbacks) - helpful_count

        return {
            "total": len(feedbacks),
            "average_rating": round(avg_rating, 2),
            "helpful_count": helpful_count,
            "unhelpful_count": unhelpful_count,
            "helpful_percentage": round(100 * helpful_count / len(feedbacks), 1)
        }
