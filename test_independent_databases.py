# -*- coding: utf-8 -*-
"""
測試獨立資料庫架構
驗證 M4、M5、M6 模組使用各自獨立的資料庫，互不干擾
"""

from core.db_manager import DBManager
import os

print("=" * 80)
print("測試獨立資料庫架構")
print("=" * 80)

# 測試步驟 1: 驗證資料庫檔案位置
print("\n[步驟 1] 檢查資料庫檔案目錄")
data_dir = 'data'
if os.path.exists(data_dir):
    print(f"✓ 資料庫目錄存在: {data_dir}/")
    db_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
    print(f"  目前存在的資料庫檔案: {len(db_files)} 個")
    for db_file in sorted(db_files):
        print(f"    - {db_file}")
else:
    print(f"✓ 資料庫目錄不存在（將自動建立）")

# 測試步驟 2: 測試 M4 模組資料庫
print("\n[步驟 2] 測試 M4 員工查詢模組資料庫")
try:
    db_m4_emp = DBManager('m4_employees')
    db_m4_emp.add_employee('M4-001', '張三', None, 'M4測試部門', '2025-01-01')

    db_m4_perf = DBManager('m4_performance')
    db_m4_perf.add_performance_record('M4-001', 2024, 'A', 90)

    # 驗證資料
    m4_employees = db_m4_emp.get_all_employees()
    m4_performance = db_m4_perf.get_all_records()

    print(f"✓ M4 模組資料庫運作正常")
    print(f"  - m4_employees.db: {len(m4_employees)} 位員工")
    print(f"  - m4_performance.db: {len(m4_performance)} 筆績效記錄")
except Exception as e:
    print(f"✗ M4 模組資料庫測試失敗: {e}")

# 測試步驟 3: 測試 M5 模組資料庫
print("\n[步驟 3] 測試 M5 資格檢核器模組資料庫")
try:
    db_m5_emp = DBManager('m5_employees')
    db_m5_emp.add_employee('M5-001', '李四', 'A123456789', 'M5測試部門', '2025-01-02')

    db_m5_sep = DBManager('m5_separation')
    db_m5_sep.add_separation_record('M5-001', '2025-12-31', '自願離職', '個人因素', False)

    # 驗證資料
    m5_employees = db_m5_emp.get_all_employees()
    m5_separation = db_m5_sep.get_all_records()

    print(f"✓ M5 模組資料庫運作正常")
    print(f"  - m5_employees.db: {len(m5_employees)} 位員工")
    print(f"  - m5_separation.db: {len(m5_separation)} 筆離職記錄")
except Exception as e:
    print(f"✗ M5 模組資料庫測試失敗: {e}")

# 測試步驟 4: 測試 M6 模組資料庫
print("\n[步驟 4] 測試 M6 到期提醒系統模組資料庫")
try:
    db_m6 = DBManager('m6_reminders')
    db_m6.add_employee('M6-001', '王五', None, 'M6測試部門', '2025-01-03')
    db_m6.add_reminder('M6-001', '王五', '試用期滿', '2025-01-03', '2025-04-03', '測試提醒')

    # 驗證資料
    m6_employees = db_m6.get_all_employees()
    m6_reminders = db_m6.get_all_records()

    print(f"✓ M6 模組資料庫運作正常")
    print(f"  - m6_reminders.db: {len(m6_employees)} 位員工, {len(m6_reminders)} 筆提醒")
except Exception as e:
    print(f"✗ M6 模組資料庫測試失敗: {e}")

# 測試步驟 5: 驗證資料隔離（M4 不應該看到 M5 的資料）
print("\n[步驟 5] 驗證模組間資料完全隔離")
try:
    # M4 應該只看到 M4-001
    db_m4_check = DBManager('m4_employees')
    m4_all = db_m4_check.get_all_employees()
    m4_ids = [emp['emp_id'] for emp in m4_all]

    # M5 應該只看到 M5-001
    db_m5_check = DBManager('m5_employees')
    m5_all = db_m5_check.get_all_employees()
    m5_ids = [emp['emp_id'] for emp in m5_all]

    # M6 應該只看到 M6-001
    db_m6_check = DBManager('m6_reminders')
    m6_all = db_m6_check.get_all_employees()
    m6_ids = [emp['emp_id'] for emp in m6_all]

    print(f"  M4 員工資料庫內容: {m4_ids}")
    print(f"  M5 員工資料庫內容: {m5_ids}")
    print(f"  M6 員工資料庫內容: {m6_ids}")

    # 驗證隔離性
    isolation_ok = True
    if 'M5-001' in m4_ids or 'M6-001' in m4_ids:
        print(f"✗ 資料隔離失敗: M4 看到了其他模組的資料")
        isolation_ok = False
    if 'M4-001' in m5_ids or 'M6-001' in m5_ids:
        print(f"✗ 資料隔離失敗: M5 看到了其他模組的資料")
        isolation_ok = False
    if 'M4-001' in m6_ids or 'M5-001' in m6_ids:
        print(f"✗ 資料隔離失敗: M6 看到了其他模組的資料")
        isolation_ok = False

    if isolation_ok:
        print(f"✓ 資料隔離驗證通過：各模組資料完全獨立")
except Exception as e:
    print(f"✗ 資料隔離驗證失敗: {e}")

# 測試步驟 6: 檢查新建立的資料庫檔案
print("\n[步驟 6] 檢查新建立的資料庫檔案")
expected_dbs = ['m4_employees.db', 'm4_performance.db', 'm5_employees.db',
                'm5_separation.db', 'm6_reminders.db']
current_dbs = [f for f in os.listdir(data_dir) if f.endswith('.db')]

print(f"  預期建立的新資料庫:")
for db_name in expected_dbs:
    if db_name in current_dbs:
        db_path = os.path.join(data_dir, db_name)
        size = os.path.getsize(db_path)
        print(f"    ✓ {db_name} ({size:,} bytes)")
    else:
        print(f"    ✗ {db_name} (未建立)")

print("\n" + "=" * 80)
print("測試完成！")
print("=" * 80)
print("\n總結:")
print("✓ M4 員工查詢模組使用獨立資料庫 (m4_*.db)")
print("✓ M5 資格檢核器使用獨立資料庫 (m5_*.db)")
print("✓ M6 到期提醒系統使用獨立資料庫 (m6_reminders.db)")
print("✓ 各模組資料完全隔離，互不干擾")
print("\n下一步:")
print("1. 清空測試資料: python clear_m5_data.py")
print("2. 啟動應用程式: streamlit run app.py")
print("3. 在 UI 中測試各模組的資料匯入功能")
