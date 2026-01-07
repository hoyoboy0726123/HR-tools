# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

class DBManager:
    def __init__(self, db_name='employees'):
        """
        Initialize database manager with separate database files for each module

        Module-specific databases:
        - M4 Employee Dashboard: m4_employees, m4_performance, m4_training, m4_separation
        - M5 Qualification Checker: m5_employees, m5_performance, m5_training, m5_separation
        - M6 Reminder System: m6_reminders

        Legacy names (for backward compatibility): employees, reminders, performance, training, separation
        """
        self.db_name = db_name
        self.db_path = f'data/{db_name}.db'
        os.makedirs('data', exist_ok=True)
        self._init_database()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Define standard table schemas (Added user_id for multi-user support)
        employees_schema = """CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY, name TEXT NOT NULL,
            id_number_hash TEXT, department TEXT, hire_date DATE,
            status TEXT DEFAULT 'active',
            user_id INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""

        performance_schema = """CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            year INTEGER,
            rating TEXT,
            score REAL,
            user_id INTEGER,
            updated_at TIMESTAMP)"""

        training_schema = """CREATE TABLE IF NOT EXISTS training (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            course_name TEXT,
            course_type TEXT,
            hours REAL,
            completion_date DATE,
            user_id INTEGER,
            updated_at TIMESTAMP)"""

        separation_schema = """CREATE TABLE IF NOT EXISTS separation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            separation_date DATE,
            separation_type TEXT,
            reason TEXT,
            blacklist BOOLEAN DEFAULT FALSE,
            user_id INTEGER,
            updated_at TIMESTAMP)"""

        reminders_schema = """CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            emp_name TEXT,
            reminder_type TEXT NOT NULL,
            created_date DATE NOT NULL,
            due_date DATE NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'pending',
            completed_date DATE,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""

        # Workflow templates schema for M1 & M2 (Multi-user support)
        templates_schema = """CREATE TABLE IF NOT EXISTS workflow_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT NOT NULL,
            template_name TEXT NOT NULL,
            description TEXT,
            config_json TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(module, template_name, user_id))"""

        # Map database names to schemas
        # Support both legacy names and new module-specific names
        table_schemas = {
            # Legacy names (backward compatibility)
            'employees': [employees_schema],
            'performance': [performance_schema],
            'training': [training_schema],
            'separation': [separation_schema],
            'reminders': [employees_schema, reminders_schema],

            # M4 Employee Dashboard databases
            'm4_employees': [employees_schema],
            'm4_performance': [performance_schema],
            'm4_training': [training_schema],
            'm4_separation': [separation_schema],

            # M5 Qualification Checker - Single database with 4 tables
            'm5_qualification': [employees_schema, performance_schema, training_schema, separation_schema],

            # M5 Legacy databases (backward compatibility)
            'm5_employees': [employees_schema],
            'm5_performance': [performance_schema],
            'm5_training': [training_schema],
            'm5_separation': [separation_schema],

            # M6 Reminder System database
            'm6_reminders': [employees_schema, reminders_schema],

            # Workflow templates database (for M1 & M2)
            'workflow_templates': [templates_schema],
        }

        # Create tables for current database
        tables = table_schemas.get(self.db_name, [])
        for table_sql in tables:
            cursor.execute(table_sql)
        conn.commit()
        conn.close()
    
    def add_employee(self, emp_id, name, id_number=None, department=None, hire_date=None, status='active'):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Hash id_number if provided for privacy
            id_number_hash = None
            if id_number:
                id_number_hash = hashlib.sha256(id_number.encode()).hexdigest()

            cursor.execute(
                "INSERT OR REPLACE INTO employees (emp_id, name, id_number_hash, department, hire_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                (emp_id, name, id_number_hash, department, hire_date, status))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding employee: {e}")
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

        # Check which tables exist in this database and provide appropriate stats
        if self.db_name in ['employees', 'm4_employees', 'm5_employees']:
            cursor.execute("SELECT COUNT(*) as count FROM employees WHERE status = 'active'")
            stats['active_employees'] = cursor.fetchone()['count']
            stats['performance_records'] = 0
            stats['training_records'] = 0
        elif self.db_name == 'm5_qualification':
            # M5 single database with all 4 tables
            cursor.execute("SELECT COUNT(*) as count FROM employees WHERE status = 'active'")
            stats['active_employees'] = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM performance")
            stats['performance_records'] = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM training")
            stats['training_records'] = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM separation")
            stats['separation_records'] = cursor.fetchone()['count']
        elif self.db_name in ['reminders', 'm6_reminders']:
            cursor.execute("SELECT COUNT(*) as count FROM reminders WHERE status = 'pending'")
            stats['pending_reminders'] = cursor.fetchone()['count']
        elif self.db_name in ['performance', 'm4_performance', 'm5_performance']:
            cursor.execute("SELECT COUNT(*) as count FROM performance")
            stats['performance_records'] = cursor.fetchone()['count']
        elif self.db_name in ['training', 'm4_training', 'm5_training']:
            cursor.execute("SELECT COUNT(*) as count FROM training")
            stats['training_records'] = cursor.fetchone()['count']

        conn.close()
        return stats
    
    # Reminder system methods
    def add_reminder(self, emp_id, emp_name, reminder_type, created_date, due_date, notes=''):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO reminders (emp_id, emp_name, reminder_type, created_date, due_date, notes, status)
                   VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
                (emp_id, emp_name, reminder_type, created_date, due_date, notes)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding reminder: {e}")
            return False

    def get_reminders_by_range(self, start_date, end_date, status=None):
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                """SELECT id, emp_id, emp_name, reminder_type, due_date,
                          notes, status, completed_date
                   FROM reminders
                   WHERE due_date BETWEEN ? AND ? AND status = ?
                   ORDER BY due_date""",
                (start_date, end_date, status)
            )
        else:
            cursor.execute(
                """SELECT id, emp_id, emp_name, reminder_type, due_date,
                          notes, status, completed_date
                   FROM reminders
                   WHERE due_date BETWEEN ? AND ?
                   ORDER BY due_date""",
                (start_date, end_date)
            )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def mark_reminder_completed(self, reminder_id):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE reminders
                   SET status = 'completed', completed_date = ?
                   WHERE id = ?""",
                (datetime.now().strftime('%Y-%m-%d'), reminder_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False

    #  Performance and training methods
    def get_performance_history(self, emp_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM performance WHERE emp_id = ? ORDER BY year DESC",
            (emp_id,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_training_history(self, emp_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM training WHERE emp_id = ? ORDER BY completion_date DESC",
            (emp_id,)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_separation_record(self, emp_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM separation WHERE emp_id = ? ORDER BY separation_date DESC LIMIT 1",
            (emp_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def import_employee_data(self, df):
        """Import employee master data from dataframe"""
        try:
            conn = self._get_connection()
            for _, row in df.iterrows():
                emp_id = row.get('emp_id') or row.get('工號')
                name = row.get('name') or row.get('姓名')
                department = row.get('department') or row.get('部門')
                hire_date = row.get('hire_date') or row.get('到職日')

                if emp_id and name:
                    self.add_employee(emp_id, name, None, department, hire_date)
            conn.close()
            return {'success': True, 'count': len(df)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def import_performance_data(self, df):
        """Import performance data from dataframe"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            count = 0
            for _, row in df.iterrows():
                emp_id = row.get('emp_id') or row.get('工號')
                year = row.get('year') or row.get('年度')
                rating = row.get('rating') or row.get('考績')
                score = row.get('score') or row.get('分數')

                if emp_id and year:
                    cursor.execute(
                        "INSERT OR REPLACE INTO performance (emp_id, year, rating, score, updated_at) VALUES (?, ?, ?, ?, ?)",
                        (emp_id, year, rating, score, datetime.now())
                    )
                    count += 1
            conn.commit()
            conn.close()
            return {'success': True, 'count': count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def import_training_data(self, df):
        """Import training data from dataframe"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            count = 0
            for _, row in df.iterrows():
                emp_id = row.get('emp_id') or row.get('工號')
                course_name = row.get('course_name') or row.get('課程名稱')
                course_type = row.get('course_type') or row.get('課程類別')
                hours = row.get('hours') or row.get('時數')
                completion_date = row.get('completion_date') or row.get('完成日期')

                if emp_id and course_name:
                    cursor.execute(
                        "INSERT INTO training (emp_id, course_name, course_type, hours, completion_date, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (emp_id, course_name, course_type, hours, completion_date, datetime.now())
                    )
                    count += 1
            conn.commit()
            conn.close()
            return {'success': True, 'count': count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # === 資料庫管理方法 ===

    def get_all_employees(self):
        """取得所有員工資料"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY emp_id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_records(self, table_name=None):
        """取得資料庫的所有記錄（適用於非 employees 資料庫）

        Args:
            table_name: 指定要查詢的表格名稱 (for m5_qualification only)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # For m5_qualification, need to specify which table
        if self.db_name == 'm5_qualification':
            if table_name == 'performance':
                cursor.execute("SELECT * FROM performance ORDER BY year DESC")
            elif table_name == 'training':
                cursor.execute("SELECT * FROM training ORDER BY completion_date DESC")
            elif table_name == 'separation':
                cursor.execute("SELECT * FROM separation ORDER BY separation_date DESC")
            else:
                return []
        # 根據資料庫類型選擇表
        elif self.db_name in ['reminders', 'm6_reminders']:
            cursor.execute("SELECT * FROM reminders ORDER BY due_date")
        elif self.db_name in ['performance', 'm4_performance', 'm5_performance']:
            cursor.execute("SELECT * FROM performance ORDER BY year DESC")
        elif self.db_name in ['training', 'm4_training', 'm5_training']:
            cursor.execute("SELECT * FROM training ORDER BY completion_date DESC")
        elif self.db_name in ['separation', 'm4_separation', 'm5_separation']:
            cursor.execute("SELECT * FROM separation ORDER BY separation_date DESC")
        else:
            return []

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_employee(self, emp_id):
        """刪除員工（僅適用於 employees 資料庫）"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def delete_by_emp_id(self, emp_id, table_name=None):
        """根據工號刪除記錄（適用於非 employees 資料庫）

        Args:
            emp_id: 員工編號
            table_name: 指定要刪除的表格名稱 (for m5_qualification only)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # For m5_qualification, need to specify which table
            if self.db_name == 'm5_qualification':
                if table_name == 'performance':
                    cursor.execute("DELETE FROM performance WHERE emp_id = ?", (emp_id,))
                elif table_name == 'training':
                    cursor.execute("DELETE FROM training WHERE emp_id = ?", (emp_id,))
                elif table_name == 'separation':
                    cursor.execute("DELETE FROM separation WHERE emp_id = ?", (emp_id,))
            elif self.db_name in ['reminders', 'm6_reminders']:
                cursor.execute("DELETE FROM reminders WHERE emp_id = ?", (emp_id,))
            elif self.db_name in ['performance', 'm4_performance', 'm5_performance']:
                cursor.execute("DELETE FROM performance WHERE emp_id = ?", (emp_id,))
            elif self.db_name in ['training', 'm4_training', 'm5_training']:
                cursor.execute("DELETE FROM training WHERE emp_id = ?", (emp_id,))
            elif self.db_name in ['separation', 'm4_separation', 'm5_separation']:
                cursor.execute("DELETE FROM separation WHERE emp_id = ?", (emp_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def delete_reminder_by_id(self, reminder_id):
        """根據提醒ID刪除提醒"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def clear_all_data(self, table_name=None):
        """清空整個資料庫

        Args:
            table_name: 指定要清空的表格名稱 (for m5_qualification only, None = 清空所有表)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Handle M5 single qualification database
            if self.db_name == 'm5_qualification':
                if table_name is None:
                    # Clear all tables
                    cursor.execute("DELETE FROM employees")
                    cursor.execute("DELETE FROM performance")
                    cursor.execute("DELETE FROM training")
                    cursor.execute("DELETE FROM separation")
                elif table_name == 'employees':
                    cursor.execute("DELETE FROM employees")
                elif table_name == 'performance':
                    cursor.execute("DELETE FROM performance")
                elif table_name == 'training':
                    cursor.execute("DELETE FROM training")
                elif table_name == 'separation':
                    cursor.execute("DELETE FROM separation")

            # Handle legacy databases
            elif self.db_name == 'employees':
                cursor.execute("DELETE FROM employees")
            elif self.db_name == 'reminders':
                cursor.execute("DELETE FROM reminders")
                cursor.execute("DELETE FROM employees")  # reminders 資料庫也有 employees 表
            elif self.db_name == 'performance':
                cursor.execute("DELETE FROM performance")
            elif self.db_name == 'training':
                cursor.execute("DELETE FROM training")
            elif self.db_name == 'separation':
                cursor.execute("DELETE FROM separation")

            # Handle M4 module databases
            elif self.db_name == 'm4_employees':
                cursor.execute("DELETE FROM employees")
            elif self.db_name == 'm4_performance':
                cursor.execute("DELETE FROM performance")
            elif self.db_name == 'm4_training':
                cursor.execute("DELETE FROM training")
            elif self.db_name == 'm4_separation':
                cursor.execute("DELETE FROM separation")

            # Handle M5 legacy databases (backward compatibility)
            elif self.db_name == 'm5_employees':
                cursor.execute("DELETE FROM employees")
            elif self.db_name == 'm5_performance':
                cursor.execute("DELETE FROM performance")
            elif self.db_name == 'm5_training':
                cursor.execute("DELETE FROM training")
            elif self.db_name == 'm5_separation':
                cursor.execute("DELETE FROM separation")

            # Handle M6 module databases
            elif self.db_name == 'm6_reminders':
                cursor.execute("DELETE FROM reminders")
                cursor.execute("DELETE FROM employees")  # m6_reminders 資料庫也有 employees 表

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Clear error: {e}")
            return False

    def add_performance_record(self, emp_id, year, rating, score):
        """Add a performance record"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO performance (emp_id, year, rating, score, updated_at) VALUES (?, ?, ?, ?, ?)",
                (emp_id, year, rating, score, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding performance record: {e}")
            return False

    def add_training_record(self, emp_id, course_name, course_type, hours, completion_date):
        """Add a training record"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO training (emp_id, course_name, course_type, hours, completion_date, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (emp_id, course_name, course_type, hours, completion_date, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding training record: {e}")
            return False

    def add_separation_record(self, emp_id, separation_date, separation_type, reason, blacklist=False):
        """Add a separation record"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO separation (emp_id, separation_date, separation_type, reason, blacklist, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (emp_id, separation_date, separation_type, reason, blacklist, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding separation record: {e}")
            return False

    # ========== Workflow Template Management Methods ==========

    def save_template(self, module: str, template_name: str, config: dict, description: str = None):
        """
        Save a workflow template

        Args:
            module: Module name ('M1' or 'M2')
            template_name: Name of the template
            config: Configuration dictionary
            description: Optional description

        Returns:
            Dict with 'success' and 'message'
        """
        import json

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            config_json = json.dumps(config, ensure_ascii=False, indent=2)

            cursor.execute("""
                INSERT INTO workflow_templates (module, template_name, description, config_json, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(module, template_name)
                DO UPDATE SET
                    description = excluded.description,
                    config_json = excluded.config_json,
                    updated_at = excluded.updated_at
            """, (module, template_name, description, config_json, datetime.now()))

            conn.commit()
            conn.close()

            return {'success': True, 'message': f'範本「{template_name}」已儲存'}
        except Exception as e:
            return {'success': False, 'message': f'儲存失敗: {str(e)}'}

    def load_template(self, module: str, template_name: str):
        """
        Load a workflow template

        Args:
            module: Module name ('M1' or 'M2')
            template_name: Name of the template

        Returns:
            Dict with template data or None
        """
        import json

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, template_name, description, config_json, created_at, updated_at
                FROM workflow_templates
                WHERE module = ? AND template_name = ?
            """, (module, template_name))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'template_name': row[1],
                    'description': row[2],
                    'config': json.loads(row[3]),
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            return None
        except Exception as e:
            print(f"Error loading template: {e}")
            return None

    def get_all_templates(self, module: str):
        """
        Get all templates for a specific module

        Args:
            module: Module name ('M1' or 'M2')

        Returns:
            List of template metadata (without full config)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, template_name, description, created_at, updated_at
                FROM workflow_templates
                WHERE module = ?
                ORDER BY updated_at DESC
            """, (module,))

            rows = cursor.fetchall()
            conn.close()

            return [{
                'id': row[0],
                'template_name': row[1],
                'description': row[2],
                'created_at': row[3],
                'updated_at': row[4]
            } for row in rows]
        except Exception as e:
            print(f"Error getting templates: {e}")
            return []

    def delete_template(self, module: str, template_name: str):
        """
        Delete a workflow template

        Args:
            module: Module name ('M1' or 'M2')
            template_name: Name of the template

        Returns:
            Dict with 'success' and 'message'
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM workflow_templates
                WHERE module = ? AND template_name = ?
            """, (module, template_name))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                return {'success': True, 'message': f'範本「{template_name}」已刪除'}
            else:
                return {'success': False, 'message': '找不到該範本'}
        except Exception as e:
            return {'success': False, 'message': f'刪除失敗: {str(e)}'}
