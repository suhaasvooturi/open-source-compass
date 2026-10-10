"""Semantic matching module supporting TF-IDF baseline and optional Sentence-Transformers."""

from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Check optional sentence-transformers availability
_SENTENCE_TRANSFORMERS_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer, util
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except (ImportError, Exception):
    _SENTENCE_TRANSFORMERS_AVAILABLE = False


class SemanticMatcher:
    """Computes semantic text similarity between developer profile and GitHub issues.

    Uses TF-IDF + Cosine Similarity by default.
    Optionally utilizes lightweight SentenceTransformer if available.
    """

    def __init__(self, use_transformer: bool = False, model_name: str = "all-MiniLM-L6-v2"):
        self.use_transformer = use_transformer and _SENTENCE_TRANSFORMERS_AVAILABLE
        self.model_name = model_name
        self._transformer_model = None
        self.engine_name = "TF-IDF + Cosine Similarity (Baseline)"

        if self.use_transformer:
            try:
                self._transformer_model = SentenceTransformer(model_name)
                self.engine_name = f"Sentence-Transformers ({model_name})"
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformer model: {e}. Falling back to TF-IDF.")
                self.use_transformer = False

    @staticmethod
    def is_transformer_available() -> bool:
        """Check if sentence-transformers is installed and usable."""
        return _SENTENCE_TRANSFORMERS_AVAILABLE

    def compute_similarity(self, query: str, document: str) -> float:
        """Compute similarity score in range [0.0, 1.0] between a profile query and issue text."""
        if not query.strip() or not document.strip():
            return 0.0

        if self.use_transformer and self._transformer_model is not None:
            try:
                emb_query = self._transformer_model.encode(query, convert_to_tensor=True)
                emb_doc = self._transformer_model.encode(document, convert_to_tensor=True)
                sim = util.cos_sim(emb_query, emb_doc).item()
                # Cosine similarity is in [-1, 1], normalize to [0, 1]
                return max(0.0, min(1.0, (sim + 1.0) / 2.0))
            except Exception:
                # Fall back to TF-IDF
                pass

        return self._compute_tfidf_similarity(query, document)

    def _compute_tfidf_similarity(self, query: str, document: str) -> float:
        """Fallback baseline using scikit-learn TF-IDF Vectorizer."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(stop_words="english", token_pattern=r"(?u)\b\w+\b")
            tfidf_matrix = vectorizer.fit_transform([query, document])
            score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(max(0.0, min(1.0, score)))
        except Exception:
            # Jaccard word-set fallback if vectorizer fails
            words_q = set(query.lower().split())
            words_d = set(document.lower().split())
            if not words_q or not words_d:
                return 0.0
            intersection = words_q.intersection(words_d)
            union = words_q.union(words_d)
            return float(len(intersection) / len(union)) if union else 0.0

    def compute_batch_similarities(self, query: str, documents: List[str]) -> List[float]:
        """Compute similarity scores for a list of issue documents."""
        if not documents:
            return []
        if not query.strip():
            return [0.0] * len(documents)

        if self.use_transformer and self._transformer_model is not None:
            try:
                emb_query = self._transformer_model.encode(query, convert_to_tensor=True)
                emb_docs = self._transformer_model.encode(documents, convert_to_tensor=True)
                sims = util.cos_sim(emb_query, emb_docs)[0].tolist()
                return [max(0.0, min(1.0, (s + 1.0) / 2.0)) for s in sims]
            except Exception:
                pass

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            corpus = [query] + documents
            vectorizer = TfidfVectorizer(stop_words="english", token_pattern=r"(?u)\b\w+\b")
            tfidf_matrix = vectorizer.fit_transform(corpus)
            sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            return [float(max(0.0, min(1.0, s))) for s in sims]
        except Exception:
            return [self.compute_similarity(query, doc) for doc in documents]
