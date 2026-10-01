import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("DB_PATH", "kisansaathi.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            crop TEXT NOT NULL,
            mandi TEXT,
            target_price REAL NOT NULL,
            condition TEXT DEFAULT 'above', -- 'above' or 'below'
            is_active INTEGER DEFAULT 1,
            triggered INTEGER DEFAULT 0,
            triggered_at TEXT,
            triggered_price REAL,
            created_at TEXT NOT NULL
        )
    """)

    # Query logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            language TEXT,
            intent TEXT,
            crop TEXT,
            mandi TEXT,
            reply TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Follow-up reminders table (Addendum 2)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            crop TEXT NOT NULL,
            issue_name TEXT,
            note TEXT,
            days INTEGER DEFAULT 3,
            due_date TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    # Crop history table (Opt-in only, no image stored, privacy compliant)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crop_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            crop TEXT,
            image_type TEXT,
            assessment TEXT,
            issue_name TEXT,
            confidence REAL,
            severity TEXT,
            produce_grade TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_reminder(user_id: str, crop: str, issue_name: Optional[str] = None, note: Optional[str] = None, days: int = 3) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow()
    created_at = now.isoformat()
    # Compute due date
    from datetime import timedelta
    due_date = (now + timedelta(days=days)).strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO reminders (user_id, crop, issue_name, note, days, due_date, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """, (user_id, crop, issue_name, note, days, due_date, created_at))
    reminder_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reminder_id


def get_user_reminders(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, crop, issue_name, note, days, due_date, is_active, created_at
        FROM reminders
        WHERE user_id = ? AND is_active = 1
        ORDER BY id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_reminder(reminder_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET is_active = 0 WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


def save_crop_history(user_id: str, crop: Optional[str], image_type: str, assessment: str, issue_name: Optional[str], confidence: float, severity: Optional[str], produce_grade: Optional[str]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO crop_history (user_id, crop, image_type, assessment, issue_name, confidence, severity, produce_grade, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, crop, image_type, assessment, issue_name, confidence, severity, produce_grade, created_at))
    history_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return history_id


def add_alert(user_id: str, crop: str, target_price: float, mandi: Optional[str] = None, condition: str = "above") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO alerts (user_id, crop, mandi, target_price, condition, is_active, triggered, created_at)
        VALUES (?, ?, ?, ?, ?, 1, 0, ?)
    """, (user_id, crop, mandi, target_price, condition, created_at))
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alert_id


def get_user_alerts(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, crop, mandi, target_price, condition, is_active, triggered, triggered_at, triggered_price, created_at
        FROM alerts
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_active_alerts() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, crop, mandi, target_price, condition, is_active, triggered, created_at
        FROM alerts
        WHERE is_active = 1 AND triggered = 0
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_alert_triggered(alert_id: int, current_price: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    triggered_at = datetime.utcnow().isoformat()
    cursor.execute("""
        UPDATE alerts
        SET triggered = 1, is_active = 0, triggered_at = ?, triggered_price = ?
        WHERE id = ?
    """, (triggered_at, current_price, alert_id))
    conn.commit()
    conn.close()


def log_query(user_id: str, message: str, reply: str, language: Optional[str] = None, intent: Optional[str] = None, crop: Optional[str] = None, mandi: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute("""
        INSERT INTO query_logs (user_id, message, language, intent, crop, mandi, reply, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, message, language, intent, crop, mandi, reply, created_at))
    conn.commit()
    conn.close()
