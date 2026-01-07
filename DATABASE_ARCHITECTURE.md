# HR Data Tool - Database Architecture

## 資料庫架構說明

### 新架構特點 (Phase 4 - 完全獨立架構)

為了確保不同模組的資料完全獨立、互不干擾，我們採用**模組專屬資料庫架構**。

**設計原則：**
- 每個模組使用自己專屬的資料庫檔案
- 不同模組之間零共享、零干擾
- 適合示範案例，可獨立部署各模組

### 資料庫檔案列表

所有資料庫檔案位於 `data/` 目錄：

#### M4 員工查詢模組 (Employee Dashboard)
1. **m4_employees.db** - 員工基本資料
   - `employees` 表：工號、姓名、部門、到職日等
2. **m4_performance.db** - 績效資料
   - `performance` 表：年度、評等、分數
3. **m4_training.db** - 訓練資料
   - `training` 表：課程名稱、類別、時數、完成日期
4. **m4_separation.db** - 離職資料
   - `separation` 表：離職日期、類型、原因、黑名單

#### M5 資格檢核器 (Qualification Checker)
1. **m5_employees.db** - 員工基本資料
   - `employees` 表：工號、姓名、身分證字號雜湊、部門、到職日等
2. **m5_performance.db** - 績效資料
   - `performance` 表：年度、評等、分數
3. **m5_training.db** - 訓練資料
   - `training` 表：課程名稱、類別、時數、完成日期
4. **m5_separation.db** - 離職資料
   - `separation` 表：離職日期、類型、原因、黑名單

#### M6 到期提醒系統 (Reminder System)
1. **m6_reminders.db** - 提醒系統資料庫（包含兩個表）
   - `employees` 表：員工基本資料（方便查詢）
   - `reminders` 表：提醒事項（試用期滿、合約到期等）

### 使用方式

```python
from core.db_manager import DBManager

# M4 員工查詢模組
db_m4_employees = DBManager('m4_employees')
db_m4_performance = DBManager('m4_performance')

# M5 資格檢核器
db_m5_employees = DBManager('m5_employees')
db_m5_separation = DBManager('m5_separation')

# M6 到期提醒系統
db_m6_reminders = DBManager('m6_reminders')

# 使用方法
employees = db_m4_employees.search_employee('John')
reminders = db_m6_reminders.get_reminders_by_range('2026-01-01', '2026-03-31')
```

### 向後兼容

DBManager 仍支援舊的命名方式（employees, performance, training, separation, reminders），以保持向後兼容性。

### 模組獨立性保證

**完全隔離的好處：**
- ✅ M4、M5、M6 各自擁有獨立資料庫
- ✅ 互不干擾、互不影響
- ✅ 可獨立測試、獨立部署
- ✅ 適合示範與教學用途

### 測試資料

測試檔案位於 `test_data/`：

- `test_m6_new_hires_2025Q4.xlsx` - 2025年Q4新進人員（12筆）
  - 10月到職 → 試用期滿：2026/01
  - 11月到職 → 試用期滿：2026/02
  - 12月到職 → 試用期滿：2026/03

## 功能特點

### 到期提醒系統

1. **自動計算到期日**
   - 選擇員工後，系統自動讀取到職日
   - 根據試用期月數自動計算試用期滿日
   - 可手動調整到期日

2. **智慧提醒檢視**
   - 🔴 已逾期：到期日已過
   - 🟡 即將到期：7天內到期
   - 🟢 未來提醒：7天後才到期

3. **批次匯入**
   - 支援 Excel/CSV 檔案
   - 自動識別中英文欄位名稱
   - 同時建立員工資料和提醒事項
   - 顯示詳細錯誤訊息

## 重要提醒

- ⚠️ 不同資料庫之間的資料是獨立的
- ⚠️ 刪除 `employees.db` 不會影響 `reminders.db` 中的資料
- ⚠️ 批次匯入時會同時更新兩個資料庫
