import sqlite3
import json
from datetime import datetime
import os

DB_FILE = 'resumes.db'

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            json_path TEXT,
            pdf_path TEXT,
            resume_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_resume(resume_data, json_path, pdf_path, ip_address=None):
    """Save resume information to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO resumes (name, email, phone, json_path, pdf_path, resume_data, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_data.get('name', ''),
        resume_data.get('email', ''),
        resume_data.get('phone', ''),
        json_path,
        pdf_path,
        json.dumps(resume_data),
        ip_address
    ))
    
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    
    return resume_id

def get_resume_stats():
    """Get statistics about generated resumes"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM resumes')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT email) FROM resumes WHERE email != ""')
    unique_users = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM resumes 
        GROUP BY DATE(created_at) 
        ORDER BY date DESC 
        LIMIT 7
    ''')
    daily_stats = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_resumes': total,
        'unique_users': unique_users,
        'daily_stats': daily_stats
    }

def get_all_resumes(limit=100):
    """Get recent resumes"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, email, phone, created_at, pdf_path
        FROM resumes
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    resumes = cursor.fetchall()
    conn.close()
    
    return resumes

def export_all_data():
    """Export all resume data for backup"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM resumes')
    all_data = cursor.fetchall()
    
    conn.close()
    return all_data
