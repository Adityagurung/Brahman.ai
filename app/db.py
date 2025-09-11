# db.py - PostgreSQL Database Module for RAG (TIMEZONE FIXED)

import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any

# FIXED: Define the timezone for India (IST = UTC+5:30)
tz = ZoneInfo("Asia/Kolkata")

def get_db_connection():
    """Create database connection using environment variables"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "Bhramana"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin"),
        port=int(os.getenv("POSTGRES_PORT", 5432))
    )

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Drop existing tables
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")
            
            # Create conversations table
            cur.execute("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    search_type TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    eval_prompt_tokens INTEGER NOT NULL,
                    eval_completion_tokens INTEGER NOT NULL,
                    eval_total_tokens INTEGER NOT NULL,
                    openai_cost FLOAT NOT NULL,
                    search_results_count INTEGER DEFAULT 0,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
            # Create feedback table
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
            conn.commit()
            print("Database initialized successfully")
    finally:
        conn.close()

def save_conversation(
    conversation_id: str,
    question: str,
    answer_data: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> None:
    """
    Save conversation to database with proper timezone handling

    Args:
        conversation_id: Unique conversation identifier
        question: User question
        answer_data: Dictionary containing answer and metadata
        timestamp: Optional timestamp, defaults to now in IST
    """
    if timestamp is None:
        timestamp = datetime.now(tz)  # IST timezone
    
    print(f"💾 Saving conversation with IST timestamp: {timestamp}")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # FIXED: Removed COALESCE - use direct timestamp parameter
            cur.execute(
                """
                INSERT INTO conversations
                (id, question, answer, model_used, search_type, response_time, relevance,
                 relevance_explanation, prompt_tokens, completion_tokens, total_tokens,
                 eval_prompt_tokens, eval_completion_tokens, eval_total_tokens,
                 openai_cost, search_results_count, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    question,
                    answer_data["answer"],
                    answer_data["model_used"],
                    answer_data["search_type"],
                    answer_data["response_time"],
                    answer_data["relevance"],
                    answer_data["relevance_explanation"],
                    answer_data["prompt_tokens"],
                    answer_data["completion_tokens"],
                    answer_data["total_tokens"],
                    answer_data["eval_prompt_tokens"],
                    answer_data["eval_completion_tokens"],
                    answer_data["eval_total_tokens"],
                    answer_data["openai_cost"],
                    answer_data["search_results_count"],
                    timestamp,  # Direct IST timestamp (PostgreSQL converts to UTC automatically)
                )
            )
            conn.commit()
            print(f"✅ Conversation saved successfully")
    finally:
        conn.close()

def save_feedback(
    conversation_id: str,
    feedback: int,
    timestamp: Optional[datetime] = None
) -> None:
    """
    Save user feedback for a conversation with proper timezone handling

    Args:
        conversation_id: Conversation ID to associate feedback with
        feedback: 1 for thumbs up, -1 for thumbs down
        timestamp: Optional timestamp, defaults to now in IST
    """
    if timestamp is None:
        timestamp = datetime.now(tz)  # IST timezone
    
    print(f"👍 Saving feedback with IST timestamp: {timestamp}")
    print(f"🔗 Conversation ID: {conversation_id}, Feedback: {feedback}")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # FIXED: Removed COALESCE - use direct timestamp parameter
            cur.execute(
                "INSERT INTO feedback (conversation_id, feedback, timestamp) VALUES (%s, %s, %s)",
                (conversation_id, feedback, timestamp),
            )
            conn.commit()
            print(f"✅ Feedback saved successfully")
    finally:
        conn.close()

def get_recent_conversations(limit: int = 5, relevance: Optional[str] = None) -> List[Dict]:
    """
    Get recent conversations with optional relevance filter
    Timestamps are automatically converted to display timezone by psycopg2

    Args:
        limit: Maximum number of conversations to return
        relevance: Optional relevance filter ("RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT")

    Returns:
        List of conversation dictionaries with proper timezone display
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback,
                       c.timestamp AT TIME ZONE 'Asia/Kolkata' as timestamp_ist
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """
            if relevance:
                query += f" WHERE c.relevance = '{relevance}'"
            query += " ORDER BY c.timestamp DESC LIMIT %s"
            
            cur.execute(query, (limit,))
            results = cur.fetchall()
            
            # Convert to regular dict and add IST timestamp
            conversations = []
            for row in results:
                conv_dict = dict(row)
                # Convert UTC timestamp to IST for display
                if conv_dict['timestamp']:
                    conv_dict['timestamp_display'] = conv_dict['timestamp'].astimezone(tz)
                conversations.append(conv_dict)
                
            return conversations
    finally:
        conn.close()

def get_feedback_stats() -> Dict[str, int]:
    """
    Get feedback statistics

    Returns:
        Dictionary with thumbs_up and thumbs_down counts
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            result = cur.fetchone()
            return {
                'thumbs_up': result['thumbs_up'] or 0,
                'thumbs_down': result['thumbs_down'] or 0
            }
    finally:
        conn.close()

def get_model_usage_stats() -> List[Dict]:
    """Get model usage statistics for monitoring"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT
                    model_used,
                    COUNT(*) as usage_count,
                    AVG(response_time) as avg_response_time,
                    AVG(total_tokens) as avg_total_tokens,
                    SUM(openai_cost) as total_cost
                FROM conversations
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY model_used
                ORDER BY usage_count DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()

def get_search_type_stats() -> List[Dict]:
    """Get search type usage statistics"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT
                    search_type,
                    COUNT(*) as usage_count,
                    AVG(response_time) as avg_response_time,
                    AVG(search_results_count) as avg_results_count
                FROM conversations
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY search_type
                ORDER BY usage_count DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()

def get_relevance_stats() -> List[Dict]:
    """Get relevance distribution statistics"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT
                    relevance,
                    COUNT(*) as count,
                    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
                FROM conversations
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY relevance
                ORDER BY count DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()

def get_hourly_stats() -> List[Dict]:
    """Get hourly conversation statistics for the last 24 hours"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT
                    DATE_TRUNC('hour', timestamp AT TIME ZONE 'Asia/Kolkata') as hour_ist,
                    COUNT(*) as conversation_count,
                    AVG(response_time) as avg_response_time,
                    SUM(total_tokens) as total_tokens
                FROM conversations
                WHERE timestamp >= NOW() - INTERVAL '24 hours'
                GROUP BY DATE_TRUNC('hour', timestamp AT TIME ZONE 'Asia/Kolkata')
                ORDER BY hour_ist DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()

def get_total_conversations() -> int:
    """Get total number of conversations"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM conversations")
            return cur.fetchone()[0]
    finally:
        conn.close()

def get_avg_response_time() -> float:
    """Get average response time"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT AVG(response_time) FROM conversations")
            result = cur.fetchone()[0]
            return result or 0.0
    finally:
        conn.close()

def get_avg_relevance_score() -> str:
    """Get average relevance (most common relevance)"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT relevance, COUNT(*) as count
                FROM conversations
                GROUP BY relevance
                ORDER BY count DESC
                LIMIT 1
            """)
            result = cur.fetchone()
            return result[0] if result else "UNKNOWN"
    finally:
        conn.close()