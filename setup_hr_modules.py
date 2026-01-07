
# setup_hr_modules.py
# Run this to rebuild all core modules

import os

def create_db_manager():
    code = '''# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

class DBManager:
    def __init__(self, db_path='data/hr_database.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tables creation (simplified for space)
        tables = [
            """CREATE TABLE IF NOT EXISTS employees (
                emp_id TEXT PRIMARY KEY, name TEXT NOT NULL,
                id_number_hash TEXT, department TEXT, hire_date DATE,
                status TEXT DEFAULT 'active',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
        ]
        for table_sql in tables:
            cursor.execute(table_sql)
        conn.commit()
        conn.close()
    
    def add_employee(self, emp_id, name, id_number=None, department=None, hire_date=None):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO employees (emp_id, name, department, hire_date) VALUES (?, ?, ?, ?)",
                (emp_id, name, department, hire_date))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def search_employee(self, keyword):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT emp_id, name, department, hire_date, status FROM employees WHERE emp_id LIKE ? OR name LIKE ?",
            (f'%{keyword}%', f'%{keyword}%'))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_database_stats(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) as count FROM employees WHERE status = 'active'")
        stats['active_employees'] = cursor.fetchone()['count']
        stats['performance_records'] = 0
        stats['training_records'] = 0
        stats['pending_reminders'] = 0
        conn.close()
        return stats
    
    # Minimal implementations for other methods
    def get_performance_history(self, emp_id):
        return []
    
    def get_training_history(self, emp_id):
        return []
'''
    with open('core/db_manager.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Created core/db_manager.py")

def create_column_matcher():
    code = '''# -*- coding: utf-8 -*-
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional

class ColumnMatcher:
    def __init__(self, threshold=0.6):
        self.threshold = threshold
    
    def find_similar_columns(self, col1_list, col2_list):
        matches = {}
        for col1 in col1_list:
            best_match = None
            best_score = 0
            for col2 in col2_list:
                score = SequenceMatcher(None, col1.lower(), col2.lower()).ratio()
                if score > best_score and score >= self.threshold:
                    best_score = score
                    best_match = col2
            if best_match:
                matches[col1] = (best_match, best_score)
        return matches
    
    def suggest_standard_name(self, column_names):
        return column_names[0] if column_names else None
'''
    with open('core/column_matcher.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Created core/column_matcher.py")

def create_data_processor():
    code = '''# -*- coding: utf-8 -*-
import pandas as pd
from typing import List, Dict
from datetime import datetime

class DataProcessor:
    def __init__(self, df):
        self.df = df.copy()
        self.original_df = df.copy()
        self.history = []
    
    def apply_cleaning_step(self, step):
        action = step['action']
        column = step.get('column')
        
        if action == 'trim_whitespace' and column:
            self.df[column] = self.df[column].astype(str).str.strip()
        elif action == 'unify_date_format' and column:
            fmt = step.get('format', '%Y-%m-%d')
            self.df[column] = pd.to_datetime(self.df[column], errors='coerce').dt.strftime(fmt)
        elif action == 'remove_duplicates':
            subset = step.get('subset')
            keep = step.get('keep', 'first')
            self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        
        return self.df
'''
    with open('core/data_processor.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Created core/data_processor.py")

def create_file_handler():
    code = '''# -*- coding: utf-8 -*-
import pandas as pd
import os

class FileHandler:
    @staticmethod
    def load_file(file_path, **kwargs):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, **kwargs)
        elif ext == '.csv':
            try:
                return pd.read_csv(file_path, encoding='utf-8', **kwargs)
            except UnicodeDecodeError:
                return pd.read_csv(file_path, encoding='big5', **kwargs)
        raise ValueError(f"Unsupported file type: {ext}")
'''
    with open('utils/file_handler.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Created utils/file_handler.py")

# Run all
if __name__ == '__main__':
    print("Setting up HR Tool modules...")
    create_db_manager()
    create_column_matcher()
    create_data_processor()
    create_file_handler()
    print("\\nAll modules created successfully!")
