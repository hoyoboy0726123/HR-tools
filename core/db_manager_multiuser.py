# -*- coding: utf-8 -*-
"""
DBManager 多用戶支援擴展
為 DBManager 添加 user_id 篩選功能
"""

from core.db_manager import DBManager as BaseDBManager


class DBManagerMultiUser(BaseDBManager):
    """支援多用戶資料隔離的 DBManager"""

    def __init__(self, db_name='employees', user_id=None):
        super().__init__(db_name)
        self.user_id = user_id

    # ========== 員工相關方法（加入 user_id 篩選） ==========

    def add_employee(self, emp_id, name, id_number=None, department=None, hire_date=None, status='active', user_id=None):
        """新增員工（支援 user_id）"""
        try:
            import hashlib
            from datetime import datetime

            conn = self._get_connection()
            cursor = conn.cursor()

            # Hash id_number if provided for privacy
            id_number_hash = None
            if id_number:
                id_number_hash = hashlib.sha256(id_number.encode()).hexdigest()

            # 使用傳入的 user_id 或實例的 user_id
            uid = user_id if user_id is not None else self.user_id

            cursor.execute(
                "INSERT OR REPLACE INTO employees (emp_id, name, id_number_hash, department, hire_date, status, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (emp_id, name, id_number_hash, department, hire_date, status, uid))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding employee: {e}")
            return False

    def get_all_employees(self, user_id=None):
        """取得所有員工資料（依 user_id 篩選）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        uid = user_id if user_id is not None else self.user_id

        if uid is not None:
            cursor.execute("SELECT * FROM employees WHERE user_id = ? ORDER BY emp_id", (uid,))
        else:
            cursor.execute("SELECT * FROM employees ORDER BY emp_id")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def search_employee(self, keyword, user_id=None):
        """搜尋員工（依 user_id 篩選）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        uid = user_id if user_id is not None else self.user_id

        if uid is not None:
            cursor.execute(
                "SELECT emp_id, name, department, hire_date, status FROM employees WHERE (emp_id LIKE ? OR name LIKE ?) AND user_id = ?",
                (f'%{keyword}%', f'%{keyword}%', uid))
        else:
            cursor.execute(
                "SELECT emp_id, name, department, hire_date, status FROM employees WHERE emp_id LIKE ? OR name LIKE ?",
                (f'%{keyword}%', f'%{keyword}%'))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def delete_employee(self, emp_id, user_id=None):
        """刪除員工（依 user_id 篩選，確保只刪除自己的資料）"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            if uid is not None:
                cursor.execute("DELETE FROM employees WHERE emp_id = ? AND user_id = ?", (emp_id, uid))
            else:
                cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    # ========== 績效相關方法（加入 user_id 篩選） ==========

    def get_performance_history(self, emp_id, user_id=None):
        """取得績效歷程（依 user_id 篩選）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        uid = user_id if user_id is not None else self.user_id

        if uid is not None:
            cursor.execute(
                "SELECT * FROM performance WHERE emp_id = ? AND user_id = ? ORDER BY year DESC",
                (emp_id, uid)
            )
        else:
            cursor.execute(
                "SELECT * FROM performance WHERE emp_id = ? ORDER BY year DESC",
                (emp_id,)
            )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def add_performance_record(self, emp_id, year, rating, score, user_id=None):
        """新增績效記錄（支援 user_id）"""
        try:
            from datetime import datetime
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            cursor.execute(
                "INSERT INTO performance (emp_id, year, rating, score, user_id, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (emp_id, year, rating, score, uid, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding performance record: {e}")
            return False

    def import_performance_data(self, df, user_id=None):
        """匯入績效資料（支援 user_id）"""
        try:
            from datetime import datetime
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            count = 0
            for _, row in df.iterrows():
                emp_id = row.get('emp_id') or row.get('工號')
                year = row.get('year') or row.get('年度')
                rating = row.get('rating') or row.get('考績')
                score = row.get('score') or row.get('分數')

                if emp_id and year:
                    cursor.execute(
                        "INSERT OR REPLACE INTO performance (emp_id, year, rating, score, user_id, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (emp_id, year, rating, score, uid, datetime.now())
                    )
                    count += 1
            conn.commit()
            conn.close()
            return {'success': True, 'count': count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========== 訓練相關方法（加入 user_id 篩選） ==========

    def get_training_history(self, emp_id, user_id=None):
        """取得訓練歷程（依 user_id 篩選）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        uid = user_id if user_id is not None else self.user_id

        if uid is not None:
            cursor.execute(
                "SELECT * FROM training WHERE emp_id = ? AND user_id = ? ORDER BY completion_date DESC",
                (emp_id, uid)
            )
        else:
            cursor.execute(
                "SELECT * FROM training WHERE emp_id = ? ORDER BY completion_date DESC",
                (emp_id,)
            )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def add_training_record(self, emp_id, course_name, course_type, hours, completion_date, user_id=None):
        """新增訓練記錄（支援 user_id）"""
        try:
            from datetime import datetime
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            cursor.execute(
                "INSERT INTO training (emp_id, course_name, course_type, hours, completion_date, user_id, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (emp_id, course_name, course_type, hours, completion_date, uid, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding training record: {e}")
            return False

    def import_training_data(self, df, user_id=None):
        """匯入訓練資料（支援 user_id）"""
        try:
            from datetime import datetime
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            count = 0
            for _, row in df.iterrows():
                emp_id = row.get('emp_id') or row.get('工號')
                course_name = row.get('course_name') or row.get('課程名稱')
                course_type = row.get('course_type') or row.get('課程類別')
                hours = row.get('hours') or row.get('時數')
                completion_date = row.get('completion_date') or row.get('完成日期')

                if emp_id and course_name:
                    cursor.execute(
                        "INSERT INTO training (emp_id, course_name, course_type, hours, completion_date, user_id, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (emp_id, course_name, course_type, hours, completion_date, uid, datetime.now())
                    )
                    count += 1
            conn.commit()
            conn.close()
            return {'success': True, 'count': count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========== 離職相關方法（加入 user_id 篩選） ==========

    def get_separation_record(self, emp_id, user_id=None):
        """取得離職記錄（依 user_id 篩選）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        uid = user_id if user_id is not None else self.user_id

        if uid is not None:
            cursor.execute(
                "SELECT * FROM separation WHERE emp_id = ? AND user_id = ? ORDER BY separation_date DESC LIMIT 1",
                (emp_id, uid)
            )
        else:
            cursor.execute(
                "SELECT * FROM separation WHERE emp_id = ? ORDER BY separation_date DESC LIMIT 1",
                (emp_id,)
            )

        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def add_separation_record(self, emp_id, separation_date, separation_type, reason, blacklist=False, user_id=None):
        """新增離職記錄（支援 user_id）"""
        try:
            from datetime import datetime
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            cursor.execute(
                "INSERT INTO separation (emp_id, separation_date, separation_type, reason, blacklist, user_id, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (emp_id, separation_date, separation_type, reason, blacklist, uid, datetime.now())
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding separation record: {e}")
            return False

    # ========== 提醒相關方法（加入 user_id 篩選） ==========

    def add_reminder(self, emp_id, emp_name, reminder_type, created_date, due_date, notes='', user_id=None):
        """新增提醒（支援 user_id）"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            cursor.execute(
                """INSERT INTO reminders (emp_id, emp_name, reminder_type, created_date, due_date, notes, status, user_id)
                   VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
                (emp_id, emp_name, reminder_type, created_date, due_date, notes, uid)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding reminder: {e}")
            return False

    def get_reminders_by_range(self, start_date, end_date, status=None, user_id=None):
        """取得指定日期範圍的提醒（依 user_id 篩選）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        uid = user_id if user_id is not None else self.user_id

        if uid is not None:
            if status:
                cursor.execute(
                    """SELECT id, emp_id, emp_name, reminder_type, due_date,
                              notes, status, completed_date
                       FROM reminders
                       WHERE due_date BETWEEN ? AND ? AND status = ? AND user_id = ?
                       ORDER BY due_date""",
                    (start_date, end_date, status, uid)
                )
            else:
                cursor.execute(
                    """SELECT id, emp_id, emp_name, reminder_type, due_date,
                              notes, status, completed_date
                       FROM reminders
                       WHERE due_date BETWEEN ? AND ? AND user_id = ?
                       ORDER BY due_date""",
                    (start_date, end_date, uid)
                )
        else:
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

    def get_all_records(self, table_name=None, user_id=None):
        """取得所有記錄（依 user_id 篩選）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        uid = user_id if user_id is not None else self.user_id

        # For m5_qualification, need to specify which table
        if self.db_name == 'm5_qualification':
            if table_name == 'performance':
                if uid is not None:
                    cursor.execute("SELECT * FROM performance WHERE user_id = ? ORDER BY year DESC", (uid,))
                else:
                    cursor.execute("SELECT * FROM performance ORDER BY year DESC")
            elif table_name == 'training':
                if uid is not None:
                    cursor.execute("SELECT * FROM training WHERE user_id = ? ORDER BY completion_date DESC", (uid,))
                else:
                    cursor.execute("SELECT * FROM training ORDER BY completion_date DESC")
            elif table_name == 'separation':
                if uid is not None:
                    cursor.execute("SELECT * FROM separation WHERE user_id = ? ORDER BY separation_date DESC", (uid,))
                else:
                    cursor.execute("SELECT * FROM separation ORDER BY separation_date DESC")
            else:
                return []
        # 根據資料庫類型選擇表
        elif self.db_name in ['reminders', 'm6_reminders']:
            if uid is not None:
                cursor.execute("SELECT * FROM reminders WHERE user_id = ? ORDER BY due_date", (uid,))
            else:
                cursor.execute("SELECT * FROM reminders ORDER BY due_date")
        elif self.db_name in ['performance', 'm4_performance', 'm5_performance']:
            if uid is not None:
                cursor.execute("SELECT * FROM performance WHERE user_id = ? ORDER BY year DESC", (uid,))
            else:
                cursor.execute("SELECT * FROM performance ORDER BY year DESC")
        elif self.db_name in ['training', 'm4_training', 'm5_training']:
            if uid is not None:
                cursor.execute("SELECT * FROM training WHERE user_id = ? ORDER BY completion_date DESC", (uid,))
            else:
                cursor.execute("SELECT * FROM training ORDER BY completion_date DESC")
        elif self.db_name in ['separation', 'm4_separation', 'm5_separation']:
            if uid is not None:
                cursor.execute("SELECT * FROM separation WHERE user_id = ? ORDER BY separation_date DESC", (uid,))
            else:
                cursor.execute("SELECT * FROM separation ORDER BY separation_date DESC")
        else:
            return []

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ========== 範本相關方法（加入 user_id 篩選） ==========

    def save_template(self, module: str, template_name: str, config: dict, description: str = None, user_id=None):
        """儲存範本（支援 user_id）"""
        import json
        from datetime import datetime

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 確保 uid 存在
            uid = user_id if user_id is not None else self.user_id
            
            # 如果 uid 還是 None，嘗試從 session_state 拿
            if uid is None:
                try:
                    import streamlit as st
                    if 'user_info' in st.session_state:
                        uid = st.session_state.user_info.get('user_id')
                except:
                    pass

            config_json = json.dumps(config, ensure_ascii=False, indent=2)

            cursor.execute("""
                INSERT INTO workflow_templates (module, template_name, description, config_json, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(module, template_name, user_id)
                DO UPDATE SET
                    description = excluded.description,
                    config_json = excluded.config_json,
                    updated_at = excluded.updated_at
            """, (module, template_name, description, config_json, uid, datetime.now()))

            conn.commit()
            conn.close()

            return {'success': True, 'message': f'範本「{template_name}」已儲存'}
        except Exception as e:
            print(f"❌ Save Template Error: {str(e)}")
            return {'success': False, 'message': f'儲存失敗: {str(e)}'}

    def get_all_templates(self, module: str, user_id=None):
        """取得所有範本（依 user_id 篩選）"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id
            
            # 如果 uid 為 None 且在 Streamlit 環境，嘗試自動補齊
            if uid is None:
                try:
                    import streamlit as st
                    if 'user_info' in st.session_state:
                        uid = st.session_state.user_info.get('user_id')
                except:
                    pass

            if uid is not None:
                cursor.execute("""
                    SELECT id, template_name, description, created_at, updated_at
                    FROM workflow_templates
                    WHERE module = ? AND (user_id = ? OR user_id IS NULL)
                    ORDER BY updated_at DESC
                """, (module, uid))
            else:
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

    def load_template(self, module: str, template_name: str, user_id=None):
        """載入範本（依 user_id 篩選）"""
        import json

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id
            
            if uid is None:
                try:
                    import streamlit as st
                    if 'user_info' in st.session_state:
                        uid = st.session_state.user_info.get('user_id')
                except:
                    pass

            if uid is not None:
                cursor.execute("""
                    SELECT id, template_name, description, config_json, created_at, updated_at
                    FROM workflow_templates
                    WHERE module = ? AND template_name = ? AND (user_id = ? OR user_id IS NULL)
                """, (module, template_name, uid))
            else:
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

    def delete_template(self, module: str, template_name: str, user_id=None):
        """刪除範本（依 user_id 篩選，確保只刪除自己的範本）"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            uid = user_id if user_id is not None else self.user_id

            if uid is not None:
                cursor.execute("""
                    DELETE FROM workflow_templates
                    WHERE module = ? AND template_name = ? AND user_id = ?
                """, (module, template_name, uid))
            else:
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
