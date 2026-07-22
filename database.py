# database.py
# ----------------------------------------------------------------------
# Multi-User SQLite wrapper for storing user groups and announcements.
# Each user has their own groups and announcement history.
# ----------------------------------------------------------------------

import sqlite3
from typing import List, Tuple

DB_NAME = "bot.db"


def init_db() -> None:
    """Create tables for multi-user support."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # User groups - each user can have multiple groups
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, chat_id)
        )
        """
    )
    
    # User announcements history
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            msg_type TEXT NOT NULL,
            text_content TEXT,
            photo_id TEXT,
            caption TEXT,
            success_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            total_groups INTEGER DEFAULT 0,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    conn.commit()
    conn.close()


# ==================== USER GROUPS ====================

def add_group(user_id: int, chat_id: int, title: str) -> None:
    """Add a group for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_groups (user_id, chat_id, title) VALUES (?, ?, ?)
        ON CONFLICT(user_id, chat_id) DO UPDATE SET title = excluded.title
        """,
        (user_id, chat_id, title),
    )
    conn.commit()
    conn.close()


def remove_group(user_id: int, chat_id: int) -> None:
    """Remove a group for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_groups WHERE user_id = ? AND chat_id = ?",
        (user_id, chat_id),
    )
    conn.commit()
    conn.close()


def get_user_groups(user_id: int) -> List[Tuple[int, int, str]]:
    """Return all groups for a specific user as (id, chat_id, title) tuples."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, chat_id, title FROM user_groups WHERE user_id = ? ORDER BY title COLLATE NOCASE",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def group_exists(user_id: int, chat_id: int) -> bool:
    """Check if a group exists for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM user_groups WHERE user_id = ? AND chat_id = ?",
        (user_id, chat_id),
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


# ==================== ANNOUNCEMENTS HISTORY ====================

def save_announcement(user_id: int, msg_type: str, text_content: str, photo_id: str,
                     caption: str, success_count: int, failed_count: int, total_groups: int) -> None:
    """Save announcement history."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO announcements 
        (user_id, msg_type, text_content, photo_id, caption, success_count, failed_count, total_groups)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, msg_type, text_content, photo_id, caption, success_count, failed_count, total_groups),
    )
    conn.commit()
    conn.close()


def get_announcement_stats(user_id: int) -> dict:
    """Get total announcements stats for a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*), SUM(success_count), SUM(failed_count), SUM(total_groups)
        FROM announcements WHERE user_id = ?
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    
    if row[0] == 0:
        return {"total_announcements": 0, "total_success": 0, "total_failed": 0, "total_groups": 0}
    
    return {
        "total_announcements": row[0],
        "total_success": row[1] or 0,
        "total_failed": row[2] or 0,
        "total_groups": row[3] or 0,
    }
