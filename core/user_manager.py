# -*- coding: utf-8 -*-
"""
用戶管理系統
使用 Email 作為唯一識別，不需要密碼
"""

import re
import hashlib
from datetime import datetime
from typing import Optional, Dict
from core.db_manager import DBManager


class UserManager:
    """簡單的用戶管理系統"""

    def __init__(self):
        """初始化用戶管理器"""
        self.db = DBManager('users')
        self._ensure_users_table()

    def _ensure_users_table(self):
        """確保用戶表存在"""
        conn = self.db._get_connection()
        cursor = conn.cursor()

        # 創建用戶表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                email_hash TEXT UNIQUE NOT NULL,
                display_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        驗證 Email 格式

        Args:
            email: 要驗證的 email

        Returns:
            bool: Email 格式是否正確
        """
        # 基本的 email 格式驗證
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None

    @staticmethod
    def hash_email(email: str) -> str:
        """
        將 Email 轉換為 Hash（用於資料庫隔離）

        Args:
            email: 用戶 email

        Returns:
            str: Email 的 SHA256 hash
        """
        return hashlib.sha256(email.lower().strip().encode()).hexdigest()[:16]

    def register_or_login(self, email: str) -> Dict:
        """
        註冊或登入用戶

        Args:
            email: 用戶 email

        Returns:
            dict: 包含 success, message, user_id, email_hash 的字典
        """
        # 驗證 email 格式
        if not self.validate_email(email):
            return {
                'success': False,
                'message': '❌ Email 格式不正確，請輸入有效的 Email 地址（例如：user@example.com）'
            }

        email = email.lower().strip()
        email_hash = self.hash_email(email)

        conn = self.db._get_connection()
        cursor = conn.cursor()

        try:
            # 檢查用戶是否已存在
            cursor.execute("SELECT id, email, created_at FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user:
                # 用戶已存在，更新最後登入時間
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE email = ?",
                    (datetime.now(), email)
                )
                conn.commit()

                return {
                    'success': True,
                    'message': f'✅ 歡迎回來！您已成功登入',
                    'user_id': user['id'],
                    'email': user['email'],
                    'email_hash': email_hash,
                    'is_new_user': False
                }
            else:
                # 新用戶，創建帳號
                cursor.execute(
                    "INSERT INTO users (email, email_hash, last_login) VALUES (?, ?, ?)",
                    (email, email_hash, datetime.now())
                )
                conn.commit()

                user_id = cursor.lastrowid

                return {
                    'success': True,
                    'message': f'🎉 帳號創建成功！歡迎使用 HR 資料處理工具',
                    'user_id': user_id,
                    'email': email,
                    'email_hash': email_hash,
                    'is_new_user': True
                }

        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'message': f'❌ 登入失敗：{str(e)}'
            }
        finally:
            conn.close()

    def get_user_info(self, email: str) -> Optional[Dict]:
        """
        獲取用戶資訊

        Args:
            email: 用戶 email

        Returns:
            dict or None: 用戶資訊
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, email, email_hash, created_at, last_login FROM users WHERE email = ?",
            (email.lower().strip(),)
        )
        user = cursor.fetchone()

        conn.close()

        if user:
            return dict(user)
        return None

    def get_all_users_count(self) -> int:
        """
        獲取總用戶數

        Returns:
            int: 用戶總數
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()

        conn.close()

        return result['count'] if result else 0

    def logout(self) -> Dict:
        """
        登出（清除 session）

        Returns:
            dict: 包含 success 和 message
        """
        return {
            'success': True,
            'message': '✅ 已成功登出'
        }
