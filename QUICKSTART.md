# 快速開始指南

## Phase 1 核心基礎已完成！

本專案 Phase 1 的核心架構已經建立完成，包含：

### ✅ 已實作功能

1. **資料庫管理系統** (core/db_manager.py)
   - 完整的 SQLite 資料庫架構
   - 員工、績效、訓練、離職、提醒等表格
   - 豐富的查詢與操作 API

2. **資料處理引擎** (core/data_processor.py)
   - 動態欄位偵測
   - 多種資料清洗操作
   - 操作歷史追蹤

3. **欄位智能比對** (core/column_matcher.py)
   - 模糊字串比對
   - HR 常見欄位標準化
   - 跨檔案欄位映射

4. **檔案處理工具** (utils/file_handler.py)
   - Excel/CSV 讀寫
   - 多檔案合併
   - 自動編碼偵測

5. **Streamlit GUI** (app.py)
   - 首頁儀表板
   - 員工查詢介面
   - 模組化設計

## 立即開始使用

### 步驟 1: 安裝依賴

```bash
pip install -r requirements.txt
```

主要依賴套件：
- streamlit (GUI 框架)
- pandas (資料處理)
- openpyxl (Excel 支援)

### 步驟 2: 啟動應用程式

```bash
streamlit run app.py
```

應用程式將自動在瀏覽器開啟 (http://localhost:8501)

### 步驟 3: 探索功能

1. **首頁**: 查看資料庫統計資訊
2. **員工查詢**: 搜尋並查看員工完整資訊
3. **報表合併器**: (開發中，顯示功能說明)
4. **資料清洗器**: (開發中，顯示功能說明)

## 使用測試資料

測試資料位於 `tests/test_data/` 目錄，包含：

- test_m4_employee_master.xlsx - 員工主檔
- test_m4_performance.xlsx - 績效資料
- test_m4_training.xlsx - 訓練紀錄
- test_m1_report_A/B/C.xlsx - 報表合併測試資料
- test_m2_dirty_data.xlsx - 資料清洗測試資料

## 核心 API 使用範例

### 1. 資料庫操作

```python
from core.db_manager import DBManager

# 初始化資料庫
db = DBManager()

# 新增員工
db.add_employee('E001', '張三', 'A123456789', '資訊部', '2023-01-15')

# 搜尋員工
results = db.search_employee('張三')

# 新增績效紀錄
db.add_performance('E001', 2023, 'A', 95.5)

# 取得績效歷程
history = db.get_performance_history('E001')
```

### 2. 欄位比對

```python
from core.column_matcher import ColumnMatcher

matcher = ColumnMatcher(threshold=0.6)

# 找出相似欄位
col1 = ['員工編號', '姓名', '部門']
col2 = ['EmpID', 'Name', 'Dept']
matches = matcher.find_similar_columns(col1, col2)

# 建議標準名稱
standard = matcher.suggest_standard_name(['員工編號', 'EmpID', '工號'])
# 回傳: '工號'
```

### 3. 資料清洗

```python
from core.data_processor import DataProcessor
import pandas as pd

df = pd.read_excel('data.xlsx')
processor = DataProcessor(df)

# 去除空白
processor.apply_cleaning_step({
    'action': 'trim_whitespace',
    'column': '姓名'
})

# 統一日期格式
processor.apply_cleaning_step({
    'action': 'unify_date_format',
    'column': '到職日',
    'format': '%Y-%m-%d'
})

# 移除重複值
processor.apply_cleaning_step({
    'action': 'remove_duplicates',
    'subset': ['員工編號']
})

# 取得處理後資料
result_df = processor.df
```

### 4. 檔案處理

```python
from utils.file_handler import FileHandler

# 載入檔案
df = FileHandler.load_file('data.xlsx')

# 載入多個檔案
dataframes = FileHandler.load_multiple_files([
    'file1.xlsx',
    'file2.xlsx'
])

# 合併 DataFrames
merged = FileHandler.merge_dataframes(
    dataframes,
    method='concat'
)

# 儲存結果
FileHandler.save_to_excel(merged, 'output.xlsx')
```

## 資料庫結構

### 員工主檔 (employees)
- emp_id: 工號 (主鍵)
- name: 姓名
- department: 部門
- hire_date: 到職日
- status: 狀態 (active/separated)

### 績效紀錄 (performance)
- emp_id: 工號
- year: 年度
- rating: 評等 (A/B+/B/C)
- score: 分數

### 訓練紀錄 (training)
- emp_id: 工號
- course_name: 課程名稱
- course_type: 類型 (必修/選修)
- hours: 時數
- completion_date: 完訓日期

### 提醒事項 (reminders)
- emp_id: 工號
- reminder_type: 類型 (試用期滿/合約到期等)
- due_date: 到期日
- status: 狀態 (pending/completed)

## 下一步開發

Phase 1 核心基礎已完成，可以開始開發：

1. **Phase 2**: 報表合併器完整實作
2. **Phase 3**: 資料清洗器 GUI
3. **Phase 4**: 員工資料匯入功能
4. **Phase 5**: AI 資格檢核

## 需要協助？

- 查看 README.md 了解完整專案資訊
- 查看 SDD_HR_Data_Processing_Tool.md 了解詳細設計規格
- 檢查 tests/test_data/ 目錄中的測試資料格式

---

**版本**: 1.0 - Phase 1  
**建立日期**: 2025-01-02
