# Software Design Document (SDD)
# HR 資料處理工具平台

**版本**: 1.0  
**日期**: 2025-01-02  
**目標開發工具**: Claude Code  

---

## 1. 專案概述

### 1.1 專案目標
開發一個統一的 HR 資料處理平台，解決 HR 人員日常工作中「小但頻繁、耗時耗力」的資料處理痛點。

### 1.2 核心設計原則
1. **節省 API 成本**: 能用純 Python 規則解決的，絕不呼叫 AI
2. **範本化設計**: 所有設定可儲存為範本，重複使用
3. **混合式 AI**: 僅在複雜判斷時才呼叫 Gemini API
4. **本地優先**: 企業敏感資料不上傳雲端，使用本地 SQLite

### 1.3 目標使用者
ASUS HR 部門人員，具備基本 Excel 操作能力，無需程式背景。

---

## 2. 系統架構

### 2.1 整體架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                         Streamlit GUI                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 報表合併 │ │ 資料清洗 │ │ 流程範本 │ │ 員工查詢 │           │
│  │  模組    │ │  模組    │ │  模組    │ │ Dashboard│           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│  ┌──────────┐ ┌──────────┐                                      │
│  │ 資格檢核 │ │ 到期提醒 │                                      │
│  │  模組    │ │  模組    │                                      │
│  └──────────┘ └──────────┘                                      │
├─────────────────────────────────────────────────────────────────┤
│                      Core Services Layer                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ DataProcessor  │  │ ColumnMatcher  │  │ RuleEngine     │    │
│  │ (pandas)       │  │ (difflib)      │  │ (條件判斷)     │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ SQLite DB      │  │ JSON Config    │  │ File I/O       │    │
│  │ (員工資料)     │  │ (範本/設定)    │  │ (Excel/CSV)    │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                      AI Layer (Optional)                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Gemini API Client (僅在需要時呼叫)                      │    │
│  │ - 複雜資格判斷                                          │    │
│  │ - 自然語言查詢 (選用)                                   │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 目錄結構

```
hr_data_tool/
├── app.py                      # Streamlit 主程式入口
├── requirements.txt            # Python 依賴
├── config/
│   ├── settings.json           # 全域設定
│   └── api_config.json         # Gemini API 設定 (gitignore)
├── data/
│   ├── hr_database.db          # SQLite 資料庫
│   └── templates/              # 使用者範本
│       ├── column_mappings/    # 欄位映射範本
│       ├── workflows/          # 處理流程範本
│       └── rules/              # 規則範本
├── modules/
│   ├── __init__.py
│   ├── m1_report_merger.py     # 模組1: 報表合併
│   ├── m2_data_cleaner.py      # 模組2: 資料清洗
│   ├── m3_workflow_builder.py  # 模組3: 流程範本
│   ├── m4_employee_dashboard.py # 模組4: 員工查詢
│   ├── m5_qualification_check.py # 模組5: 資格檢核
│   └── m6_reminder_system.py   # 模組6: 到期提醒
├── core/
│   ├── __init__.py
│   ├── data_processor.py       # 資料處理核心
│   ├── column_matcher.py       # 欄位智能比對
│   ├── rule_engine.py          # 規則引擎
│   ├── db_manager.py           # SQLite 管理
│   └── ai_client.py            # Gemini API 封裝
├── utils/
│   ├── __init__.py
│   ├── file_handler.py         # 檔案讀寫
│   ├── validators.py           # 資料驗證
│   └── formatters.py           # 格式化工具
└── tests/
    ├── test_data/              # 測試資料 (Excel 檔案)
    └── test_modules.py         # 單元測試
```

---

## 3. 功能模組詳細設計

### 3.1 模組1: 報表合併器 (Report Merger)

**解決問題**: 8張報表欄位不統一，需整合成一張

#### 3.1.1 功能需求
- 支援多檔案上傳 (Excel/CSV)
- 自動偵測相似欄位名稱 (fuzzy matching)
- 視覺化欄位對應介面 (拖拉式)
- 儲存/載入欄位映射範本
- 合併方式選擇 (垂直堆疊/水平合併/依 Key 合併)
- 重複值處理選項

#### 3.1.2 核心邏輯

```python
# core/column_matcher.py
from difflib import SequenceMatcher

class ColumnMatcher:
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
    
    def find_similar_columns(self, col1_list: list, col2_list: list) -> dict:
        """
        找出兩份報表中相似的欄位
        回傳: {col1_name: (col2_name, similarity_score)}
        """
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
    
    def suggest_standard_name(self, column_names: list) -> str:
        """
        根據常見 HR 欄位名稱，建議標準化名稱
        """
        standard_mappings = {
            '工號': ['員工編號', 'EmpID', 'ID', '工號', '編號', 'EmployeeID'],
            '姓名': ['姓名', 'Name', '員工姓名', 'EmpName'],
            '部門': ['部門', 'Dept', 'Department', '部門名稱', '單位'],
            '到職日': ['到職日', '報到日', 'HireDate', '入職日期'],
            # ... 更多標準欄位
        }
        for standard, variants in standard_mappings.items():
            for name in column_names:
                if any(v.lower() in name.lower() for v in variants):
                    return standard
        return column_names[0]  # 預設用第一個
```

#### 3.1.3 UI 設計

```python
# modules/m1_report_merger.py
import streamlit as st
import pandas as pd
from core.column_matcher import ColumnMatcher

def render():
    st.header("📊 報表合併器")
    
    # Step 1: 上傳檔案
    uploaded_files = st.file_uploader(
        "上傳報表 (可多選)", 
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Step 2: 讀取並顯示各檔案欄位
        dataframes = {}
        for f in uploaded_files:
            df = pd.read_excel(f) if f.name.endswith(('xlsx', 'xls')) else pd.read_csv(f)
            dataframes[f.name] = df
            st.write(f"**{f.name}**: {len(df)} 筆, 欄位: {list(df.columns)}")
        
        # Step 3: 欄位映射設定
        st.subheader("欄位對應設定")
        
        # 載入/儲存範本
        col1, col2 = st.columns(2)
        with col1:
            template_name = st.text_input("範本名稱")
        with col2:
            if st.button("儲存範本"):
                # 儲存映射設定到 JSON
                pass
        
        # 自動建議 + 手動調整
        matcher = ColumnMatcher()
        # ... 顯示映射表格，讓使用者調整
        
        # Step 4: 合併選項
        merge_method = st.radio(
            "合併方式",
            ["垂直堆疊 (Union)", "依 Key 合併 (Join)", "水平串接 (Concat)"]
        )
        
        if merge_method == "依 Key 合併 (Join)":
            key_column = st.selectbox("選擇合併 Key", options=["工號", "姓名", "身分證字號"])
            join_type = st.selectbox("Join 類型", options=["inner", "outer", "left", "right"])
        
        # Step 5: 執行合併
        if st.button("🔄 執行合併", type="primary"):
            # 執行合併邏輯
            result_df = merge_dataframes(dataframes, mapping, merge_method)
            st.success(f"合併完成! 共 {len(result_df)} 筆資料")
            
            # 預覽結果
            st.dataframe(result_df.head(20))
            
            # 下載按鈕
            st.download_button(
                "💾 下載合併結果",
                data=result_df.to_excel(index=False),
                file_name="merged_report.xlsx"
            )
```

#### 3.1.4 AI 使用: ❌ 不需要
純 Python 規則即可處理。

---

### 3.2 模組2: 資料清洗器 (Data Cleaner)

**解決問題**: Raw Data 梳理成可用資訊，公式/VBA 遇新欄位會出錯

#### 3.2.1 功能需求
- 動態欄位偵測 (用特徵而非位置)
- 資料類型自動識別與轉換
- 常見清洗操作 (去空白/日期統一/重複值處理)
- 清洗步驟可視化 & 可回溯
- 儲存為清洗範本

#### 3.2.2 核心邏輯

```python
# core/data_processor.py
import pandas as pd
from typing import List, Dict, Callable

class DataProcessor:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.history = []  # 操作歷史，支援回溯
    
    def find_column_by_keywords(self, keywords: List[str]) -> str:
        """動態尋找欄位，不依賴固定位置"""
        for col in self.df.columns:
            col_lower = str(col).lower()
            if any(kw.lower() in col_lower for kw in keywords):
                return col
        return None
    
    def detect_column_type(self, column: str) -> str:
        """偵測欄位資料類型"""
        sample = self.df[column].dropna().head(100)
        
        # 嘗試日期
        try:
            pd.to_datetime(sample)
            return 'datetime'
        except:
            pass
        
        # 嘗試數字
        try:
            pd.to_numeric(sample)
            return 'numeric'
        except:
            pass
        
        return 'string'
    
    def apply_cleaning_step(self, step: Dict):
        """執行單一清洗步驟"""
        action = step['action']
        column = step.get('column')
        
        # 記錄歷史
        self.history.append({
            'step': step,
            'before_shape': self.df.shape
        })
        
        if action == 'trim_whitespace':
            self.df[column] = self.df[column].astype(str).str.strip()
        
        elif action == 'unify_date_format':
            target_format = step.get('format', '%Y-%m-%d')
            self.df[column] = pd.to_datetime(self.df[column]).dt.strftime(target_format)
        
        elif action == 'remove_duplicates':
            subset = step.get('subset', None)
            keep = step.get('keep', 'first')
            self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        
        elif action == 'fill_na':
            fill_value = step.get('value', '')
            self.df[column] = self.df[column].fillna(fill_value)
        
        elif action == 'split_column':
            delimiter = step.get('delimiter', ',')
            new_columns = step.get('new_columns', [])
            splits = self.df[column].str.split(delimiter, expand=True)
            for i, new_col in enumerate(new_columns):
                if i < splits.shape[1]:
                    self.df[new_col] = splits[i]
        
        elif action == 'rename_column':
            new_name = step.get('new_name')
            self.df = self.df.rename(columns={column: new_name})
        
        return self.df
    
    def undo(self):
        """回溯上一步操作"""
        if self.history:
            # 實際實作需要儲存 snapshot 或反向操作
            pass
```

#### 3.2.3 UI 設計

```python
# modules/m2_data_cleaner.py
import streamlit as st

def render():
    st.header("🧹 資料清洗器")
    
    uploaded_file = st.file_uploader("上傳原始資料", type=['xlsx', 'csv'])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        processor = DataProcessor(df)
        
        # 顯示資料預覽 & 欄位資訊
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("資料預覽")
            st.dataframe(df.head(10))
        
        with col2:
            st.subheader("欄位分析")
            for col in df.columns:
                dtype = processor.detect_column_type(col)
                null_count = df[col].isna().sum()
                st.write(f"**{col}**: {dtype}, 空值: {null_count}")
        
        # 清洗步驟設定
        st.subheader("清洗步驟")
        
        step_type = st.selectbox("選擇操作", [
            "去除前後空白", "統一日期格式", "移除重複值",
            "填入空值", "分割欄位", "重新命名欄位",
            "轉換資料類型", "條件篩選"
        ])
        
        # 根據選擇顯示對應設定
        if step_type == "去除前後空白":
            target_col = st.selectbox("選擇欄位", df.columns)
            if st.button("➕ 加入步驟"):
                st.session_state.cleaning_steps.append({
                    'action': 'trim_whitespace',
                    'column': target_col
                })
        
        # ... 其他步驟設定
        
        # 顯示已加入的步驟
        st.subheader("待執行步驟")
        for i, step in enumerate(st.session_state.get('cleaning_steps', [])):
            st.write(f"{i+1}. {step}")
        
        # 執行清洗
        if st.button("🚀 執行清洗", type="primary"):
            for step in st.session_state.cleaning_steps:
                processor.apply_cleaning_step(step)
            
            st.success("清洗完成!")
            st.dataframe(processor.df.head(20))
```

#### 3.2.4 AI 使用: ❌ 不需要

---

### 3.3 模組3: 流程範本系統 (Workflow Builder)

**解決問題**: 資料比對、整合的重複性工作，報表拆分後需合併

#### 3.3.1 功能需求
- 視覺化流程建構 (Step-by-Step)
- 儲存/載入流程範本
- 一鍵執行已儲存流程
- 支援排程執行 (選用)
- 流程執行日誌

#### 3.3.2 資料結構

```json
// data/templates/workflows/monthly_report_flow.json
{
  "flow_id": "flow_001",
  "flow_name": "月報整合流程",
  "description": "每月整合各部門完訓報表",
  "created_at": "2025-01-02",
  "steps": [
    {
      "step_id": 1,
      "action": "import",
      "config": {
        "source_type": "folder",
        "path": "C:/HR_Reports/2025/Jan",
        "file_pattern": "*.xlsx"
      }
    },
    {
      "step_id": 2,
      "action": "apply_column_mapping",
      "config": {
        "template_name": "training_report_mapping"
      }
    },
    {
      "step_id": 3,
      "action": "merge",
      "config": {
        "method": "union",
        "remove_duplicates": true,
        "duplicate_key": "工號"
      }
    },
    {
      "step_id": 4,
      "action": "calculate",
      "config": {
        "new_column": "完訓率",
        "formula": "完訓時數 / 應完訓時數 * 100"
      }
    },
    {
      "step_id": 5,
      "action": "export",
      "config": {
        "filename": "完訓報表彙總_{date}.xlsx",
        "path": "C:/HR_Reports/Output"
      }
    }
  ]
}
```

#### 3.3.3 AI 使用: ❌ 不需要

---

### 3.4 模組4: 員工查詢 Dashboard (Employee Dashboard)

**解決問題**: 查詢員工歷程需跨系統、複製貼上才能有全貌

#### 3.4.1 功能需求
- 整合多資料源到本地 SQLite
- 以工號為 Key 串接所有資料
- 單一查詢介面顯示完整資訊
- 支援模糊搜尋 (姓名/工號)
- 資料定期匯入機制

#### 3.4.2 資料庫 Schema

```sql
-- core/db_manager.py 會建立以下表格

-- 員工主檔
CREATE TABLE employees (
    emp_id TEXT PRIMARY KEY,      -- 工號
    name TEXT NOT NULL,
    id_number TEXT,               -- 身分證字號 (加密儲存)
    department TEXT,
    hire_date DATE,
    status TEXT,                  -- 在職/離職
    updated_at TIMESTAMP
);

-- 績效紀錄
CREATE TABLE performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    year INTEGER,
    rating TEXT,                  -- A/B+/B/C
    score REAL,
    updated_at TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 訓練紀錄
CREATE TABLE training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    course_name TEXT,
    course_type TEXT,             -- 必修/選修
    hours REAL,
    completion_date DATE,
    updated_at TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 離職紀錄 (用於回任判斷)
CREATE TABLE separation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    separation_date DATE,
    separation_type TEXT,         -- 自願離職/資遣/退休
    reason TEXT,
    blacklist BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

-- 資料匯入日誌
CREATE TABLE import_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT,
    import_date TIMESTAMP,
    record_count INTEGER,
    status TEXT
);
```

#### 3.4.3 UI 設計

```python
# modules/m4_employee_dashboard.py
import streamlit as st
from core.db_manager import DBManager

def render():
    st.header("👤 員工資料查詢")
    
    db = DBManager()
    
    # 搜尋區
    search_input = st.text_input("🔍 輸入工號或姓名")
    
    if search_input:
        employees = db.search_employee(search_input)
        
        if employees:
            selected = st.selectbox(
                "選擇員工",
                options=employees,
                format_func=lambda x: f"{x['emp_id']} - {x['name']} ({x['department']})"
            )
            
            if selected:
                emp_id = selected['emp_id']
                
                # 基本資料卡
                st.subheader("📋 基本資料")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("工號", emp_id)
                with col2:
                    st.metric("姓名", selected['name'])
                with col3:
                    st.metric("部門", selected['department'])
                
                st.write(f"到職日: {selected['hire_date']} | 狀態: {selected['status']}")
                
                # 績效歷程
                st.subheader("📈 績效歷程")
                perf_records = db.get_performance_history(emp_id)
                if perf_records:
                    perf_df = pd.DataFrame(perf_records)
                    st.dataframe(perf_df, hide_index=True)
                else:
                    st.info("無績效紀錄")
                
                # 訓練紀錄
                st.subheader("🎓 訓練紀錄")
                training_records = db.get_training_history(emp_id)
                if training_records:
                    total_hours = sum(r['hours'] for r in training_records)
                    st.metric("總完訓時數", f"{total_hours} 小時")
                    st.dataframe(pd.DataFrame(training_records), hide_index=True)
                
                # 離職紀錄 (若有)
                sep_record = db.get_separation_record(emp_id)
                if sep_record:
                    st.subheader("🚪 離職紀錄")
                    st.warning(f"離職日期: {sep_record['separation_date']}, 原因: {sep_record['reason']}")
                    if sep_record['blacklist']:
                        st.error("⚠️ 此員工已列入黑名單")
        else:
            st.warning("查無此員工")
    
    # 側邊欄: 資料匯入
    with st.sidebar:
        st.subheader("📥 資料匯入")
        
        import_type = st.selectbox("選擇匯入類型", [
            "員工主檔 (SAP)", "績效資料", "訓練紀錄", "離職紀錄"
        ])
        
        upload = st.file_uploader("上傳檔案", type=['xlsx', 'csv'])
        
        if upload and st.button("執行匯入"):
            # 執行匯入邏輯
            result = db.import_data(import_type, upload)
            st.success(f"匯入完成! 共 {result['count']} 筆")
```

#### 3.4.4 AI 使用: ❌ 不需要

---

### 3.5 模組5: 資格檢核器 (Qualification Checker)

**解決問題**: 離職回任資格需比對多系統資料（人才網、HCP、SAP、黑名單）

#### 3.5.1 功能需求
- 輸入姓名/身分證進行檢核
- 自動執行規則檢核 (Python)
- 複雜/例外情況呼叫 AI 綜合判斷
- 產生檢核報告 (可匯出)

#### 3.5.2 檢核流程

```
輸入: 姓名 + 身分證字號
        │
        ▼
┌───────────────────┐
│ Step 1: 黑名單比對 │ ◄── Python 規則
└───────────────────┘
        │ 若在黑名單 → 直接拒絕
        ▼
┌───────────────────┐
│ Step 2: HCP 在職查 │ ◄── Python 規則
└───────────────────┘
        │ 若其他公司在職 → 標記警示
        ▼
┌───────────────────┐
│ Step 3: 歷史績效查 │ ◄── Python 規則
└───────────────────┘
        │ 提取考績紀錄
        ▼
┌───────────────────┐
│ Step 4: 離職原因查 │ ◄── Python 規則
└───────────────────┘
        │
        ▼
┌───────────────────────────────┐
│ Step 5: 綜合判斷              │
│ ┌─────────────────────────┐  │
│ │ 規則明確? (全部 PASS)   │  │
│ └─────────────────────────┘  │
│      │ Yes          │ No     │
│      ▼              ▼        │
│  [直接通過]    [呼叫 Gemini] │ ◄── 僅此步驟需要 AI
│                判斷例外情況   │
└───────────────────────────────┘
        │
        ▼
    輸出檢核報告
```

#### 3.5.3 核心邏輯

```python
# modules/m5_qualification_check.py
from core.rule_engine import RuleEngine
from core.ai_client import GeminiClient
from core.db_manager import DBManager

class QualificationChecker:
    def __init__(self):
        self.db = DBManager()
        self.rule_engine = RuleEngine()
        self.ai_client = GeminiClient()  # 延遲初始化
    
    def check(self, name: str, id_number: str) -> dict:
        result = {
            'name': name,
            'checks': [],
            'overall_status': 'PENDING',
            'ai_used': False,
            'ai_recommendation': None
        }
        
        # Step 1: 黑名單
        blacklist_check = self.db.check_blacklist(id_number)
        result['checks'].append({
            'item': '黑名單比對',
            'status': 'FAIL' if blacklist_check else 'PASS',
            'detail': '列於黑名單中' if blacklist_check else '未在黑名單'
        })
        
        if blacklist_check:
            result['overall_status'] = 'REJECTED'
            return result
        
        # Step 2: HCP 在職查詢
        hcp_status = self.db.check_hcp_employment(id_number)
        result['checks'].append({
            'item': 'HCP 各公司在職狀態',
            'status': 'WARNING' if hcp_status else 'PASS',
            'detail': f"在 {hcp_status} 任職中" if hcp_status else '無其他公司在職紀錄'
        })
        
        # Step 3: 歷史績效
        perf_history = self.db.get_performance_by_id(id_number)
        low_perf = [p for p in perf_history if p['rating'] in ['C', 'D']]
        result['checks'].append({
            'item': '歷史績效紀錄',
            'status': 'WARNING' if low_perf else 'PASS',
            'detail': f"曾有 {len(low_perf)} 次低績效紀錄" if low_perf else '績效紀錄良好'
        })
        
        # Step 4: 離職原因
        sep_record = self.db.get_separation_by_id(id_number)
        if sep_record:
            result['checks'].append({
                'item': '離職紀錄',
                'status': 'INFO',
                'detail': f"離職日期: {sep_record['date']}, 原因: {sep_record['reason']}"
            })
        
        # Step 5: 綜合判斷
        warnings = [c for c in result['checks'] if c['status'] == 'WARNING']
        
        if not warnings:
            # 全部 PASS，不需要 AI
            result['overall_status'] = 'APPROVED'
        else:
            # 有警示項目，呼叫 AI 判斷
            result['ai_used'] = True
            result['ai_recommendation'] = self._get_ai_judgment(result)
            result['overall_status'] = 'REVIEW_REQUIRED'
        
        return result
    
    def _get_ai_judgment(self, check_result: dict) -> str:
        """呼叫 Gemini API 進行綜合判斷"""
        prompt = f"""
        你是 HR 資深專員，請根據以下檢核結果，給出離職回任資格的建議：
        
        申請人: {check_result['name']}
        檢核項目:
        {self._format_checks(check_result['checks'])}
        
        請給出:
        1. 是否建議核准回任 (建議核准 / 建議拒絕 / 需主管面談評估)
        2. 理由說明 (2-3 句話)
        3. 若有疑慮，建議進一步確認的事項
        
        請用繁體中文回覆，語氣專業但不要太制式。
        """
        
        return self.ai_client.generate(prompt)
```

#### 3.5.4 AI 使用: ⚠️ 僅在有警示項目時呼叫
- 全部 PASS → 不呼叫 AI，直接通過
- 有 WARNING → 呼叫 Gemini 綜合判斷

#### 3.5.5 成本控制

```python
# core/ai_client.py
class GeminiClient:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.call_count = 0
        self.last_call_time = None
    
    def generate(self, prompt: str, confirm: bool = True) -> str:
        """
        呼叫 Gemini API
        confirm: 若為 True，在 UI 層會先詢問使用者確認
        """
        if confirm:
            # 這個 flag 會讓 UI 層顯示確認對話框
            pass
        
        # 實際呼叫 API
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')  # 使用較便宜的模型
        response = model.generate_content(prompt)
        
        self.call_count += 1
        return response.text
```

---

### 3.6 模組6: 到期提醒系統 (Reminder System)

**解決問題**: 試用期滿調薪追蹤，SAP 無註明處，需人工記憶或每月撈報表比對

#### 3.6.1 功能需求
- 匯入新進人員名單
- 自動計算試用期滿日
- Dashboard 顯示本月/下月待處理清單
- 標記已處理狀態
- 匯出提醒清單 (Email/Excel)

#### 3.6.2 資料結構

```sql
-- 追蹤項目表
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    reminder_type TEXT,           -- 'probation' / 'contract_renewal' / 'custom'
    start_date DATE,
    due_date DATE,
    status TEXT DEFAULT 'pending', -- 'pending' / 'completed' / 'cancelled'
    notes TEXT,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.6.3 UI 設計

```python
# modules/m6_reminder_system.py
import streamlit as st
from datetime import datetime, timedelta

def render():
    st.header("⏰ 到期提醒系統")
    
    # 切換視圖
    view = st.radio("檢視", ["本月待處理", "下月預告", "全部項目"], horizontal=True)
    
    db = DBManager()
    today = datetime.now().date()
    
    if view == "本月待處理":
        month_end = today.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        items = db.get_reminders_by_range(today, month_end, status='pending')
    
    elif view == "下月預告":
        next_month_start = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_month_end = (next_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        items = db.get_reminders_by_range(next_month_start, next_month_end)
    
    else:
        items = db.get_all_reminders()
    
    # 顯示統計
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("待處理", len([i for i in items if i['status'] == 'pending']))
    with col2:
        urgent = [i for i in items if (i['due_date'] - today).days <= 7]
        st.metric("7天內到期", len(urgent), delta_color="inverse")
    with col3:
        st.metric("已完成", len([i for i in items if i['status'] == 'completed']))
    
    # 待處理清單
    st.subheader("📋 待處理清單")
    
    for item in items:
        if item['status'] == 'pending':
            days_left = (item['due_date'] - today).days
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{item['emp_id']}** - {item['emp_name']}")
                
                with col2:
                    st.write(f"到期日: {item['due_date']}")
                
                with col3:
                    if days_left < 0:
                        st.error(f"已逾期 {abs(days_left)} 天")
                    elif days_left <= 7:
                        st.warning(f"剩 {days_left} 天")
                    else:
                        st.info(f"剩 {days_left} 天")
                
                with col4:
                    if st.button("✅ 完成", key=f"done_{item['id']}"):
                        db.mark_reminder_completed(item['id'])
                        st.rerun()
    
    # 新增提醒
    with st.expander("➕ 手動新增提醒"):
        emp_id = st.text_input("工號")
        reminder_type = st.selectbox("類型", ["試用期滿", "合約到期", "其他"])
        due_date = st.date_input("到期日")
        notes = st.text_area("備註")
        
        if st.button("新增"):
            db.add_reminder(emp_id, reminder_type, due_date, notes)
            st.success("新增成功!")
    
    # 批次匯入
    with st.expander("📥 批次匯入新進人員"):
        st.write("上傳新進人員名單，自動計算試用期滿日 (到職日 + 3個月)")
        
        upload = st.file_uploader("上傳檔案", type=['xlsx', 'csv'], key='batch_import')
        probation_months = st.number_input("試用期月數", value=3, min_value=1, max_value=12)
        
        if upload and st.button("執行匯入"):
            df = pd.read_excel(upload)
            # 驗證必要欄位
            required = ['工號', '姓名', '到職日']
            # ... 執行匯入
```

#### 3.6.4 AI 使用: ❌ 不需要

---

## 4. 共用元件設計

### 4.1 Gemini API 客戶端

```python
# core/ai_client.py
import os
import json
from datetime import datetime

class GeminiClient:
    def __init__(self, config_path: str = 'config/api_config.json'):
        self.config = self._load_config(config_path)
        self.usage_log = []
    
    def _load_config(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {'api_key': None, 'model': 'gemini-1.5-flash'}
    
    def is_configured(self) -> bool:
        return self.config.get('api_key') is not None
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """呼叫 Gemini API"""
        if not self.is_configured():
            raise ValueError("Gemini API 尚未設定")
        
        import google.generativeai as genai
        genai.configure(api_key=self.config['api_key'])
        
        model = genai.GenerativeModel(self.config['model'])
        response = model.generate_content(
            prompt,
            generation_config={'temperature': temperature}
        )
        
        # 記錄使用
        self.usage_log.append({
            'timestamp': datetime.now().isoformat(),
            'prompt_length': len(prompt),
            'response_length': len(response.text)
        })
        
        return response.text
    
    def get_usage_stats(self) -> dict:
        """取得 API 使用統計"""
        return {
            'total_calls': len(self.usage_log),
            'total_prompt_chars': sum(l['prompt_length'] for l in self.usage_log),
            'total_response_chars': sum(l['response_length'] for l in self.usage_log)
        }
```

### 4.2 設定管理

```python
# core/config_manager.py
import json
import os

class ConfigManager:
    def __init__(self, config_dir: str = 'config'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
    
    def save_template(self, template_type: str, name: str, data: dict):
        """儲存範本"""
        path = os.path.join(self.config_dir, 'templates', template_type)
        os.makedirs(path, exist_ok=True)
        
        filepath = os.path.join(path, f"{name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_template(self, template_type: str, name: str) -> dict:
        """載入範本"""
        filepath = os.path.join(self.config_dir, 'templates', template_type, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_templates(self, template_type: str) -> list:
        """列出所有範本"""
        path = os.path.join(self.config_dir, 'templates', template_type)
        if os.path.exists(path):
            return [f.replace('.json', '') for f in os.listdir(path) if f.endswith('.json')]
        return []
```

---

## 5. 技術規格

### 5.1 開發環境需求

```
Python >= 3.9
```

### 5.2 依賴套件

```txt
# requirements.txt

# GUI
streamlit>=1.28.0

# 資料處理
pandas>=2.0.0
openpyxl>=3.1.0
xlrd>=2.0.0

# 資料庫
# (sqlite3 為 Python 內建)

# AI 整合
google-generativeai>=0.3.0

# 其他工具
python-dateutil>=2.8.0
```

### 5.3 執行指令

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行應用
streamlit run app.py

# 執行測試
python -m pytest tests/
```

---

## 6. 主程式入口

```python
# app.py
import streamlit as st

# 頁面配置
st.set_page_config(
    page_title="HR 資料處理工具",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 側邊欄導航
st.sidebar.title("👥 HR 資料處理工具")

module = st.sidebar.radio(
    "功能模組",
    [
        "📊 報表合併器",
        "🧹 資料清洗器", 
        "🔄 流程範本系統",
        "👤 員工查詢",
        "✅ 資格檢核器",
        "⏰ 到期提醒"
    ]
)

# 載入對應模組
if module == "📊 報表合併器":
    from modules import m1_report_merger
    m1_report_merger.render()

elif module == "🧹 資料清洗器":
    from modules import m2_data_cleaner
    m2_data_cleaner.render()

elif module == "🔄 流程範本系統":
    from modules import m3_workflow_builder
    m3_workflow_builder.render()

elif module == "👤 員工查詢":
    from modules import m4_employee_dashboard
    m4_employee_dashboard.render()

elif module == "✅ 資格檢核器":
    from modules import m5_qualification_check
    m5_qualification_check.render()

elif module == "⏰ 到期提醒":
    from modules import m6_reminder_system
    m6_reminder_system.render()

# 側邊欄底部: 設定 & 狀態
st.sidebar.divider()

with st.sidebar.expander("⚙️ 系統設定"):
    # API 設定
    api_key = st.text_input("Gemini API Key", type="password")
    if st.button("儲存 API Key"):
        # 儲存到 config
        pass
    
    # 資料庫狀態
    st.write("📁 資料庫狀態: 已連接")
    st.write("📊 員工資料: 1,234 筆")

st.sidebar.caption("版本 1.0 | © 2025")
```

---

## 7. AI 使用摘要

| 模組 | 是否需要 AI | 說明 |
|------|------------|------|
| 報表合併器 | ❌ 不需要 | difflib + pandas 即可 |
| 資料清洗器 | ❌ 不需要 | 純規則處理 |
| 流程範本系統 | ❌ 不需要 | JSON 範本 + 執行引擎 |
| 員工查詢 | ❌ 不需要 | SQLite 查詢 |
| 資格檢核器 | ⚠️ 條件式 | 僅有 WARNING 時呼叫 |
| 到期提醒 | ❌ 不需要 | 日期計算 + 狀態管理 |

**預估 API 節省**: 90%+ 的操作不需呼叫 AI

---

## 8. 開發順序建議

1. **Phase 1 - 核心基礎** (Week 1-2)
   - [ ] 專案架構建立
   - [ ] core/db_manager.py
   - [ ] core/data_processor.py
   - [ ] 主程式入口 app.py

2. **Phase 2 - 高價值模組** (Week 3-4)
   - [ ] 模組1: 報表合併器
   - [ ] 模組6: 到期提醒系統

3. **Phase 3 - 進階功能** (Week 5-6)
   - [ ] 模組2: 資料清洗器
   - [ ] 模組4: 員工查詢

4. **Phase 4 - AI 整合** (Week 7)
   - [ ] 模組5: 資格檢核器
   - [ ] core/ai_client.py

5. **Phase 5 - 自動化** (Week 8)
   - [ ] 模組3: 流程範本系統
   - [ ] 整合測試 & 優化

---

## 9. 測試資料需求

請參見 `tests/test_data/` 目錄下的測試 Excel 檔案：
- `test_m1_*.xlsx` - 報表合併測試資料
- `test_m2_*.xlsx` - 資料清洗測試資料
- `test_m3_*.xlsx` - 流程範本測試資料
- `test_m4_*.xlsx` - 員工查詢測試資料
- `test_m5_*.xlsx` - 資格檢核測試資料
- `test_m6_*.xlsx` - 到期提醒測試資料

---

**文件結束**
