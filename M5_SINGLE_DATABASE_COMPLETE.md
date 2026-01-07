# M5 資格檢核器 - 單一資料庫架構完成報告

## 概述

根據使用者需求：「可以使用單一資料庫 但是前端視覺化檢視還是分開的 也就是個別看到獨立上傳的內容 也能刪除其中一個資料庫的內容或單一的內容」，已完成 M5 資格檢核器從多資料庫架構改為單一資料庫架構。

## 修改日期

2026-01-04

## 改動摘要

### 資料庫架構變更

**之前（多資料庫）：**
- `m5_employees.db` - 員工資料
- `m5_performance.db` - 績效資料
- `m5_training.db` - 訓練資料
- `m5_separation.db` - 離職資料

**現在（單一資料庫）：**
- `m5_qualification.db` - 包含 4 個表：
  - `employees` - 員工資料表
  - `performance` - 績效資料表
  - `training` - 訓練資料表
  - `separation` - 離職資料表

### 優點

1. **簡化管理**：只需管理一個資料庫檔案
2. **資料一致性**：所有資料在同一個檔案中，確保 ACID 特性
3. **備份方便**：只需備份一個檔案
4. **符合用戶需求**：前端仍然可以分開檢視和管理各個表

## 修改的檔案

### 1. `core/db_manager.py`

#### 修改內容：

**新增 m5_qualification 資料庫映射**（第 95-96 行）：
```python
# M5 Qualification Checker - Single database with 4 tables
'm5_qualification': [employees_schema, performance_schema, training_schema, separation_schema],
```

**更新 get_database_stats() 方法**（第 156-165 行）：
```python
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
```

**更新 get_all_records() 方法**（第 350-383 行）：
```python
def get_all_records(self, table_name=None):
    """取得資料庫的所有記錄（適用於非 employees 資料庫）

    Args:
        table_name: 指定要查詢的表格名稱 (for m5_qualification only)
    """
    # For m5_qualification, need to specify which table
    if self.db_name == 'm5_qualification':
        if table_name == 'performance':
            cursor.execute("SELECT * FROM performance ORDER BY year DESC")
        elif table_name == 'training':
            cursor.execute("SELECT * FROM training ORDER BY completion_date DESC")
        elif table_name == 'separation':
            cursor.execute("SELECT * FROM separation ORDER BY separation_date DESC")
```

**更新 delete_by_emp_id() 方法**（第 398-431 行）：
```python
def delete_by_emp_id(self, emp_id, table_name=None):
    """根據工號刪除記錄

    Args:
        emp_id: 員工編號
        table_name: 指定要刪除的表格名稱 (for m5_qualification only)
    """
    # For m5_qualification, need to specify which table
    if self.db_name == 'm5_qualification':
        if table_name == 'performance':
            cursor.execute("DELETE FROM performance WHERE emp_id = ?", (emp_id,))
        elif table_name == 'training':
            cursor.execute("DELETE FROM training WHERE emp_id = ?", (emp_id,))
        elif table_name == 'separation':
            cursor.execute("DELETE FROM separation WHERE emp_id = ?", (emp_id,))
```

**更新 clear_all_data() 方法**（第 446-516 行）：
```python
def clear_all_data(self, table_name=None):
    """清空整個資料庫

    Args:
        table_name: 指定要清空的表格名稱 (for m5_qualification only, None = 清空所有表)
    """
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
        # ... 其他表
```

### 2. `modules/m5_qualification_check.py`

#### 修改內容：

**更新資料庫初始化**（第 21-28 行）：
```python
def __init__(self):
    # 使用 M5 專用的單一資料庫 - 包含 4 個表 (employees, performance, training, separation)
    self.db = DBManager('m5_qualification')
    # 為了向後兼容和程式碼可讀性，保留這些別名
    self.db_employees = self.db
    self.db_performance = self.db
    self.db_training = self.db
    self.db_separation = self.db
```

**更新資料庫管理 Tab**（第 632-653 行）：
```python
# 選擇要管理的資料庫
db_type = st.selectbox("選擇資料庫", [
    "員工資料 (employees)",
    "績效資料 (performance)",
    "訓練資料 (training)",
    "離職資料 (separation)"
])

# 使用單一資料庫 m5_qualification，根據選擇載入對應的表
db = st.session_state.checker.db  # Single database for all tables

if "員工資料" in db_type:
    table_name = "employees"
    all_data = db.get_all_employees()
elif "績效資料" in db_type:
    table_name = "performance"
    all_data = db.get_all_records(table_name='performance')
elif "訓練資料" in db_type:
    table_name = "training"
    all_data = db.get_all_records(table_name='training')
else:  # 離職資料
    table_name = "separation"
    all_data = db.get_all_records(table_name='separation')
```

**更新清空操作**（第 673 行）：
```python
db.clear_all_data(table_name=table_name)
```

**更新刪除操作**（第 718 行）：
```python
db.delete_by_emp_id(emp_id_to_delete, table_name=table_name)
```

### 3. `clear_m5_data.py`

#### 完全重寫：

```python
# Clear M5 single qualification database (contains all 4 tables)
print("\nClearing m5_qualification.db (all tables)...")
try:
    db = DBManager('m5_qualification')

    # Clear all tables in the single database
    tables = ['employees', 'performance', 'training', 'separation']
    for table in tables:
        print(f"  Clearing {table} table...")
        result = db.clear_all_data(table_name=table)
        if result:
            print(f"    + Successfully cleared {table} table")
```

### 4. 新增測試腳本 `test_m5_single_db.py`

建立完整的測試腳本驗證：
- 資料庫初始化
- 4 個表的資料新增
- 資料檢索（含 table_name 參數）
- 資料庫統計
- 表特定刪除操作
- 表特定清空操作

## 測試驗證

### 執行測試腳本

```bash
python test_m5_single_db.py
```

### 測試結果

```
================================================================================
Testing M5 Single Database Architecture
================================================================================

[Test 1] Initializing m5_qualification database...
  OK: Database initialized

[Test 2] Adding test employee...
  OK: Employee added to employees table

[Test 3] Adding test performance record...
  OK: Performance record added to performance table

[Test 4] Adding test training record...
  OK: Training record added to training table

[Test 5] Adding test separation record...
  OK: Separation record added to separation table

[Test 6] Verifying data retrieval...
  Employees table: 1 records
  Performance table: 1 records
  Training table: 1 records
  Separation table: 1 records
  OK: All tables contain expected data

[Test 7] Testing database stats...
  Stats: {'active_employees': 1, 'performance_records': 1, 'training_records': 1, 'separation_records': 1}
  OK: Database stats working correctly

[Test 8] Testing table-specific delete...
  OK: Performance record deleted (employees table unaffected)

[Test 9] Testing table-specific clear...
  OK: Training table cleared (other tables unaffected)

[Test 10] Cleaning up test data...
  OK: All test data cleared

================================================================================
Test Complete!
================================================================================
```

✅ **所有測試通過！**

## 向後兼容性

### 保留的舊資料庫支援

`core/db_manager.py` 仍然支援舊的多資料庫命名方式：
```python
# M5 Legacy databases (backward compatibility)
'm5_employees': [employees_schema],
'm5_performance': [performance_schema],
'm5_training': [training_schema],
'm5_separation': [separation_schema],
```

這意味著：
- 舊的資料庫檔案（如果存在）仍然可以使用
- 舊的測試腳本不會出錯
- 平滑過渡，無破壞性變更

## 使用指南

### 啟動應用程式

```bash
streamlit run app.py
```

### 資料匯入流程

1. 進入「📋 資格檢核」模組
2. 切換到「📥 資料匯入」tab
3. 依序上傳：
   - 員工資料 (test_m5_employee_master.xlsx)
   - 離職記錄 (test_m5_separation.xlsx)
   - 績效資料 (test_m5_performance.xlsx)
   - 訓練記錄 (test_m5_training.xlsx)

### 資料庫管理

1. 切換到「🗄️ 資料庫管理」tab
2. 使用下拉選單選擇要管理的表：
   - 員工資料 (employees)
   - 績效資料 (performance)
   - 訓練資料 (training)
   - 離職資料 (separation)
3. 可執行操作：
   - 檢視資料
   - 清空特定表
   - 匯出備份
   - 依工號刪除記錄

### 清空測試資料

```bash
# 清空所有 M5 資料
python clear_m5_data.py
```

## 技術細節

### 資料庫檔案位置

```
data/
├── m5_qualification.db     (NEW - 單一資料庫，包含 4 個表)
├── m5_employees.db         (OLD - 向後兼容)
├── m5_performance.db       (OLD - 向後兼容)
├── m5_training.db          (OLD - 向後兼容)
└── m5_separation.db        (OLD - 向後兼容)
```

### SQLite 資料庫架構

```sql
-- m5_qualification.db 包含以下 4 個表：

CREATE TABLE employees (
    emp_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    id_number_hash TEXT,
    department TEXT,
    hire_date DATE,
    status TEXT DEFAULT 'active',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    year INTEGER,
    rating TEXT,
    score REAL,
    updated_at TIMESTAMP
);

CREATE TABLE training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    course_name TEXT,
    course_type TEXT,
    hours REAL,
    completion_date DATE,
    updated_at TIMESTAMP
);

CREATE TABLE separation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    separation_date DATE,
    separation_type TEXT,
    reason TEXT,
    blacklist BOOLEAN DEFAULT 0,
    updated_at TIMESTAMP
);
```

## API 變更

### DBManager 新增參數

以下方法新增了 `table_name` 可選參數（僅用於 m5_qualification）：

1. **get_all_records(table_name=None)**
   - 用途：指定要查詢的表
   - 範例：`db.get_all_records(table_name='performance')`

2. **delete_by_emp_id(emp_id, table_name=None)**
   - 用途：指定要從哪個表刪除
   - 範例：`db.delete_by_emp_id('E001', table_name='training')`

3. **clear_all_data(table_name=None)**
   - 用途：指定要清空的表（None = 清空所有表）
   - 範例：`db.clear_all_data(table_name='separation')`

## 總結

### 完成項目

✅ 將 M5 從 4 個獨立資料庫改為單一資料庫
✅ 更新所有資料庫操作方法支援 table_name 參數
✅ 更新前端 UI 支援單一資料庫架構
✅ 更新清空腳本 (clear_m5_data.py)
✅ 建立完整測試腳本驗證功能
✅ 保持向後兼容性
✅ 所有測試通過

### 效益

1. **簡化管理**：從 4 個檔案減少到 1 個檔案
2. **資料一致性**：單一資料庫確保 ACID 特性
3. **前端靈活性**：仍然可以分開檢視和管理各個表
4. **備份方便**：只需備份 m5_qualification.db
5. **效能提升**：關聯查詢更快（同一檔案）

### 下一步建議

1. **測試 Streamlit UI**
   ```bash
   streamlit run app.py
   ```
   - 測試資料匯入
   - 測試資格檢核
   - 測試資料庫管理

2. **清理舊資料庫**（可選）
   ```bash
   # 如果確認不再需要舊資料庫
   rm data/m5_employees.db
   rm data/m5_performance.db
   rm data/m5_training.db
   rm data/m5_separation.db
   ```

3. **更新文件**
   - 更新 M5_TEST_GUIDE.md
   - 更新 M5_QUICK_START.md
   - 更新 DATABASE_ARCHITECTURE.md

**重構完成日期：** 2026-01-04

**修改檔案數：** 3 個核心檔案
**新增檔案數：** 1 個測試腳本 + 1 個文件

**測試狀態：** ✅ 全部通過
