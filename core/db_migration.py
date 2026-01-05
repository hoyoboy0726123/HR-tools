# -*- coding: utf-8 -*-
"""
資料庫遷移腳本
為所有現有資料表添加 user_id 欄位以支援多用戶資料隔離
"""

import sqlite3
import os


def migrate_add_user_id_column():
    """為所有資料庫的資料表添加 user_id 欄位"""

    # 所有需要遷移的資料庫
    databases = [
        # M4 資料庫
        'm4_employees', 'm4_performance', 'm4_training', 'm4_separation',
        # M5 資料庫
        'm5_qualification',
        # M6 資料庫
        'm6_reminders',
        # 範本資料庫
        'workflow_templates'
    ]

    # 每個資料庫中的資料表
    tables_map = {
        'm4_employees': ['employees'],
        'm4_performance': ['performance'],
        'm4_training': ['training'],
        'm4_separation': ['separation'],
        'm5_qualification': ['employees', 'performance', 'training', 'separation'],
        'm6_reminders': ['employees', 'reminders'],
        'workflow_templates': ['workflow_templates']
    }

    for db_name in databases:
        db_path = f'data/{db_name}.db'

        # 如果資料庫不存在，跳過
        if not os.path.exists(db_path):
            print(f'⏭️  {db_name}.db 不存在，跳過')
            continue

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            tables = tables_map.get(db_name, [])

            for table_name in tables:
                # 檢查表是否存在
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    print(f'⏭️  {db_name}.{table_name} 表不存在，跳過')
                    continue

                # 檢查 user_id 欄位是否已存在
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]

                if 'user_id' in columns:
                    print(f'✅ {db_name}.{table_name} 已有 user_id 欄位')
                else:
                    # 添加 user_id 欄位（預設為 NULL，允許現有資料）
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN user_id INTEGER")
                    print(f'✅ {db_name}.{table_name} 添加 user_id 欄位成功')

            conn.commit()
            conn.close()

        except Exception as e:
            print(f'❌ {db_name} 遷移失敗: {e}')


def verify_migration():
    """驗證遷移是否成功"""
    print('\n📊 驗證遷移結果...\n')

    databases = [
        'm4_employees', 'm4_performance', 'm4_training', 'm4_separation',
        'm5_qualification', 'm6_reminders', 'workflow_templates'
    ]

    tables_map = {
        'm4_employees': ['employees'],
        'm4_performance': ['performance'],
        'm4_training': ['training'],
        'm4_separation': ['separation'],
        'm5_qualification': ['employees', 'performance', 'training', 'separation'],
        'm6_reminders': ['employees', 'reminders'],
        'workflow_templates': ['workflow_templates']
    }

    all_ok = True

    for db_name in databases:
        db_path = f'data/{db_name}.db'

        if not os.path.exists(db_path):
            continue

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            tables = tables_map.get(db_name, [])

            for table_name in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    continue

                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]

                if 'user_id' in columns:
                    print(f'✅ {db_name}.{table_name} - user_id 欄位存在')
                else:
                    print(f'❌ {db_name}.{table_name} - user_id 欄位缺失')
                    all_ok = False

            conn.close()

        except Exception as e:
            print(f'❌ {db_name} 驗證失敗: {e}')
            all_ok = False

    if all_ok:
        print('\n🎉 所有資料庫遷移成功！')
    else:
        print('\n⚠️  部分資料庫遷移失敗，請檢查錯誤訊息')


if __name__ == '__main__':
    import sys
    import io

    # 設置 UTF-8 編碼以支援 emoji
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print('🚀 開始資料庫遷移...\n')
    migrate_add_user_id_column()
    verify_migration()
    print('\n✅ 遷移完成！')
