# 多用戶資料隔離實作說明

**日期**: 2026-01-05
**狀態**: 🚧 實作中

---

## 📋 實作概要

為 HR 資料處理工具添加多用戶支援，確保部署到雲端後，不同用戶的資料不會混在一起。

---

## 🎯 已完成的工作

### 1. 用戶認證系統 ✅

**檔案**: `core/user_manager.py`

**功能**:
- Email 驗證（無需密碼）
- 自動註冊新用戶 / 登入現有用戶
- Email 轉 Hash（SHA256，取前 16 位）
- 用戶資料儲存（users.db）

**資料表結構**:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    email_hash TEXT UNIQUE NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

---

### 2. 登入介面整合 ✅

**檔案**: `app.py`

**修改內容**:
- 在主應用程式前添加登入頁面
- Session state 管理：`logged_in`, `user_info`
- 側邊欄顯示用戶 Email 和登出按鈕
- 登出功能

**使用流程**:
1. 訪問應用程式 → 顯示登入頁面
2. 輸入 Email → 驗證格式
3. 註冊/登入成功 → 進入主應用程式
4. 側邊欄顯示用戶資訊

---

### 3. 資料庫遷移腳本 ✅

**檔案**: `core/db_migration.py`

**功能**:
- 為所有現有資料表添加 `user_id` 欄位
- 支援所有模組資料庫：
  - M4: m4_employees, m4_performance, m4_training, m4_separation
  - M5: m5_qualification
  - M6: m6_reminders
  - M1/M2: workflow_templates
- 驗證遷移結果

**執行方式**:
```bash
python -m core.db_migration
```

---

### 4. 多用戶資料庫管理器 ✅

**檔案**: `core/db_manager_multiuser.py`

**功能**:
- 繼承自 `DBManager`
- 所有查詢、插入、更新、刪除都支援 `user_id` 篩選
- 保持向後兼容（當 `user_id=None` 時，行為與原版相同）

**支援的方法**:
- `get_all_employees(user_id)` - 只返回該用戶的員工
- `search_employee(keyword, user_id)` - 只搜尋該用戶的員工
- `add_employee(..., user_id)` - 新增員工時標記 user_id
- `get_performance_history(emp_id, user_id)` - 只取該用戶的績效
- `get_training_history(emp_id, user_id)` - 只取該用戶的訓練
- `get_separation_record(emp_id, user_id)` - 只取該用戶的離職記錄
- `add_reminder(..., user_id)` - 新增提醒時標記 user_id
- `get_reminders_by_range(..., user_id)` - 只取該用戶的提醒
- `save_template(..., user_id)` - 儲存範本時標記 user_id
- `get_all_templates(module, user_id)` - 只取該用戶的範本
- 等等...

---

## 🚧 待完成的工作

### 1. 修改模組以使用多用戶 DBManager

需要修改的模組：

#### M4 - 員工查詢 ⏳
**檔案**: `modules/m4_employee_dashboard.py`

**需要做的事**:
1. 將 `DBManager` 替換為 `DBManagerMultiUser`
2. 初始化時傳入 `user_id`：
   ```python
   user_id = st.session_state.user_info['user_id']
   db_employees = DBManagerMultiUser('m4_employees', user_id=user_id)
   ```
3. 所有資料匯入時，自動加上 `user_id`

#### M5 - 資格檢核器 ⏳
**檔案**: `modules/m5_qualification_check.py`

**需要做的事**:
- 同 M4

#### M6 - 到期提醒 ⏳
**檔案**: `modules/m6_reminder_system.py`

**需要做的事**:
- 同 M4

#### M1 - 報表合併器 ⏳
**檔案**: `modules/m1_report_merger.py`

**需要做的事**:
- 修改範本儲存/載入，使用 `DBManagerMultiUser`
- 傳入 `user_id`

#### M2 - 資料清洗器 ⏳
**檔案**: `modules/m2_data_cleaner.py`

**需要做的事**:
- 同 M1

---

## 📝 實作步驟（下一步）

### 步驟 1: 執行資料庫遷移

```bash
# 執行遷移腳本，為所有資料表添加 user_id 欄位
python -m core.db_migration
```

**預期結果**:
- 所有現有資料表都會有 `user_id` 欄位
- 現有資料的 `user_id` 為 NULL（不影響現有功能）

---

### 步驟 2: 修改各模組

**修改模式**（以 M4 為例）:

**修改前**:
```python
from core.db_manager import DBManager

db_employees = DBManager('m4_employees')
all_employees = db_employees.get_all_employees()
```

**修改後**:
```python
from core.db_manager_multiuser import DBManagerMultiUser

# 取得當前登入用戶的 user_id
user_id = st.session_state.user_info['user_id']

# 使用多用戶版本的 DBManager
db_employees = DBManagerMultiUser('m4_employees', user_id=user_id)

# 所有查詢都會自動篩選該用戶的資料
all_employees = db_employees.get_all_employees()
```

---

### 步驟 3: 測試多用戶資料隔離

**測試腳本**: `TEST_LOGIN_SYSTEM.md` → 測試 10

**測試步驟**:
1. 使用 Email `user1@test.com` 登入
2. 在「員工查詢」中匯入測試資料
3. 登出
4. 使用 Email `user2@test.com` 登入
5. 確認看不到 user1 的資料 ✓

---

## 🔧 技術細節

### 資料庫架構變更

**所有資料表都添加 `user_id` 欄位**:

```sql
-- 員工表
ALTER TABLE employees ADD COLUMN user_id INTEGER;

-- 績效表
ALTER TABLE performance ADD COLUMN user_id INTEGER;

-- 訓練表
ALTER TABLE training ADD COLUMN user_id INTEGER;

-- 離職表
ALTER TABLE separation ADD COLUMN user_id INTEGER;

-- 提醒表
ALTER TABLE reminders ADD COLUMN user_id INTEGER;

-- 範本表
ALTER TABLE workflow_templates ADD COLUMN user_id INTEGER;
```

### 查詢邏輯變更

**修改前**:
```sql
SELECT * FROM employees WHERE emp_id = 'E001';
```

**修改後**:
```sql
SELECT * FROM employees WHERE emp_id = 'E001' AND user_id = 123;
```

**好處**:
- 同一個工號（E001）可以存在於不同用戶的資料中
- 不同用戶之間完全隔離
- 資料庫層面的安全保障

---

## 🎨 設計決策

### 為什麼用 `user_id` 而不是 `email_hash`？

**選擇 `user_id`（整數）**:
- ✅ 索引效能更好
- ✅ 儲存空間更小
- ✅ 查詢速度更快
- ✅ 符合關聯式資料庫設計規範

**不用 `email_hash`（16 字元字串）**:
- ❌ 每次查詢都要比對字串
- ❌ 佔用更多儲存空間
- ❌ 索引效能較差

**關聯方式**:
```
users.id (PRIMARY KEY) → employees.user_id (FOREIGN KEY)
```

### 為什麼創建 `DBManagerMultiUser` 而不是直接修改 `DBManager`？

**優點**:
- ✅ 保持向後兼容性
- ✅ 現有程式碼不受影響
- ✅ 可以逐步遷移各模組
- ✅ 測試更安全

**替代方案**:
- ❌ 直接修改 `DBManager` 可能破壞現有功能
- ❌ 需要同時修改所有模組（風險高）

---

## ✅ 測試檢查清單

### 登入系統測試
- [ ] 新用戶註冊成功
- [ ] 現有用戶登入成功
- [ ] Email 格式驗證正確
- [ ] 登出功能正常

### 資料隔離測試
- [ ] M4 員工查詢：不同用戶看不到彼此資料
- [ ] M5 資格檢核器：不同用戶看不到彼此資料
- [ ] M6 到期提醒：不同用戶看不到彼此資料
- [ ] M1 範本：不同用戶看不到彼此範本
- [ ] M2 範本：不同用戶看不到彼此範本

### 功能完整性測試
- [ ] 匯入資料正常
- [ ] 查詢資料正常
- [ ] 匯出資料正常
- [ ] 批次操作正常

---

## 🚀 部署注意事項

### 首次部署（新用戶）
1. 用戶訪問應用程式
2. 輸入 Email 註冊
3. 開始使用，所有資料自動標記 user_id

### 現有資料處理
- 現有資料的 `user_id` 為 NULL
- 不影響本地測試
- 部署到雲端後，從乾淨資料庫開始

### 資料庫遷移
- 執行 `core/db_migration.py`
- 為所有表添加 `user_id` 欄位
- 不會刪除任何現有資料

---

## 📚 相關文件

- `TEST_LOGIN_SYSTEM.md` - 登入系統測試指南
- `core/user_manager.py` - 用戶管理器實作
- `core/db_manager_multiuser.py` - 多用戶資料庫管理器
- `core/db_migration.py` - 資料庫遷移腳本

---

**下一步**: 修改各模組以使用 `DBManagerMultiUser`
