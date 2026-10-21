#!/usr/bin/env python3
"""
SQLite database layer for logging user interactions and ratings.
Provides persistent storage for evaluation, continuous improvement, and TAM research.
"""

import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.configs.settings import settings
from src.core.exceptions import DatabaseError
from src.core.logger import logger


class DatabaseManager:
    """Manages SQLite storage for chat interactions and feedback ratings."""


    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            data_dir = settings.BASE_DIR / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "zedchatbot.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a connection configured for dictionary row access."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes database tables if they do not exist."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS interactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            channel TEXT NOT NULL,
                            country TEXT NOT NULL,
                            user_query TEXT NOT NULL,
                            detected_language TEXT NOT NULL,
                            retrieved_sources TEXT,
                            response TEXT,
                            response_time_ms INTEGER DEFAULT 0,
                            rating INTEGER DEFAULT NULL,
                            feedback_comment TEXT DEFAULT NULL
                        )
                        """
                    )
                    cursor.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_interactions_country 
                        ON interactions(country)
                        """
                    )
                    cursor.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_interactions_channel 
                        ON interactions(channel)
                        """
                    )
                    cursor.execute(
                        """
                        CREATE INDEX IF NOT EXISTS idx_interactions_timestamp 
                        ON interactions(timestamp)
                        """
                    )
                    conn.commit()
                    logger.info(f"Database initialized at {self.db_path}")
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")

    def ping(self) -> bool:
        """Verifies database connectivity and responsiveness."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    row = cursor.fetchone()
                    return row is not None and row[0] == 1
            except Exception as e:
                logger.error(f"Database ping failed: {e}")
                return False

    def log_interaction(
        self,
        channel: str,
        country: str,
        user_query: str,
        detected_language: str,
        retrieved_sources: List[str],
        response: str,
        response_time_ms: int = 0,
    ) -> Optional[int]:
        """
        Logs a user query and the generated reply.
        Returns the inserted interaction ID.
        """
        sources_json = json.dumps(retrieved_sources or [])
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO interactions (
                            channel, country, user_query, detected_language,
                            retrieved_sources, response, response_time_ms
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            channel,
                            country.lower(),
                            user_query,
                            detected_language,
                            sources_json,
                            response,
                            response_time_ms,
                        ),
                    )
                    conn.commit()
                    interaction_id = cursor.lastrowid
                    logger.debug(f"Interaction logged with ID: {interaction_id}")
                    return interaction_id
            except Exception as e:
                logger.error(f"Failed to log interaction: {e}")
                return None

    def record_feedback(
        self,
        interaction_id: int,
        rating: int,
        feedback_comment: Optional[str] = None,
    ) -> bool:
        """
        Records user feedback rating (e.g. 1 to 5, or 1/-1) and optional comment.
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE interactions
                        SET rating = ?, feedback_comment = ?
                        WHERE id = ?
                        """,
                        (rating, feedback_comment, interaction_id),
                    )
                    conn.commit()
                    rows_affected = cursor.rowcount
                    if rows_affected > 0:
                        logger.info(
                            f"Feedback recorded for interaction #{interaction_id}: rating={rating}"
                        )
                        return True
                    else:
                        logger.warning(
                            f"Interaction ID #{interaction_id} not found for feedback."
                        )
                        return False
            except Exception as e:
                logger.error(f"Failed to record feedback for #{interaction_id}: {e}")
                raise DatabaseError(f"Database error while recording feedback: {e}") from e

    def get_interactions(
        self,
        limit: int = 50,
        offset: int = 0,
        country: Optional[str] = None,
        channel: Optional[str] = None,
        language: Optional[str] = None,
        rating: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns a filtered, paginated page of interactions plus the total
        number of rows matching the filters. Used by the admin telemetry view.

        `rating` accepts 'rated', 'unrated', or a numeric value ('1'..'5').
        """
        conditions: List[str] = []
        params: List[Any] = []

        if country:
            conditions.append("country = ?")
            params.append(country.strip().lower())
        if channel:
            conditions.append("channel = ?")
            params.append(channel.strip().lower())
        if language:
            conditions.append("detected_language = ?")
            params.append(language.strip().lower())
        if rating:
            r = str(rating).strip().lower()
            if r == "rated":
                conditions.append("rating IS NOT NULL")
            elif r == "unrated":
                conditions.append("rating IS NULL")
            elif r.isdigit():
                conditions.append("rating >= ?")
                params.append(int(r))
        if search:
            like = f"%{search.strip()}%"
            conditions.append("(user_query LIKE ? OR response LIKE ?)")
            params.extend([like, like])

        where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"SELECT COUNT(*) AS total FROM interactions {where_clause}",
                        params,
                    )
                    total = cursor.fetchone()["total"]

                    cursor.execute(
                        f"""
                        SELECT id, timestamp, channel, country, user_query,
                               detected_language, retrieved_sources, response,
                               response_time_ms, rating, feedback_comment
                        FROM interactions
                        {where_clause}
                        ORDER BY id DESC
                        LIMIT ? OFFSET ?
                        """,
                        params + [limit, offset],
                    )
                    items = []
                    for row in cursor.fetchall():
                        item = dict(row)
                        try:
                            item["retrieved_sources"] = json.loads(
                                item.get("retrieved_sources") or "[]"
                            )
                        except Exception:
                            item["retrieved_sources"] = []
                        items.append(item)

                    return {
                        "total": total,
                        "count": len(items),
                        "limit": limit,
                        "offset": offset,
                        "items": items,
                    }
            except Exception as e:
                logger.error(f"Failed to fetch interactions: {e}")
                return {
                    "total": 0,
                    "count": 0,
                    "limit": limit,
                    "offset": offset,
                    "items": [],
                }

    def get_recent_interactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent interactions."""
        return self.get_interactions(limit=limit)["items"]

    def get_stats(self) -> Dict[str, Any]:
        """Returns aggregated statistics for evaluation."""
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) AS total FROM interactions")
                    total = cursor.fetchone()["total"]

                    cursor.execute(
                        """
                        SELECT country, COUNT(*) as count 
                        FROM interactions 
                        GROUP BY country
                        """
                    )
                    by_country = {row["country"]: row["count"] for row in cursor.fetchall()}

                    cursor.execute(
                        """
                        SELECT channel, COUNT(*) as count 
                        FROM interactions 
                        GROUP BY channel
                        """
                    )
                    by_channel = {row["channel"]: row["count"] for row in cursor.fetchall()}

                    cursor.execute(
                        """
                        SELECT detected_language, COUNT(*) as count 
                        FROM interactions 
                        GROUP BY detected_language
                        """
                    )
                    by_lang = {
                        row["detected_language"]: row["count"] for row in cursor.fetchall()
                    }

                    cursor.execute(
                        """
                        SELECT AVG(response_time_ms) as avg_latency,
                               AVG(rating) as avg_rating,
                               COUNT(rating) as rated_count
                        FROM interactions
                        """
                    )
                    row = cursor.fetchone()
                    avg_latency = row["avg_latency"] or 0.0
                    avg_rating = row["avg_rating"] or 0.0
                    rated_count = row["rated_count"] or 0

                    return {
                        "total_interactions": total,
                        "by_country": by_country,
                        "by_channel": by_channel,
                        "by_language": by_lang,
                        "average_latency_ms": round(avg_latency, 2),
                        "average_rating": round(avg_rating, 2),
                        "rated_count": rated_count,
                    }
            except Exception as e:
                logger.error(f"Failed to compute stats: {e}")
                return {"total_interactions": 0}


# Global singleton instance
db = DatabaseManager()
