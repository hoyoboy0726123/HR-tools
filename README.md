# HR 資料處理工具平台

**版本**: 1.0 - Phase 1 (核心基礎)  
**日期**: 2025-01-02

## 專案概述

這是一個統一的 HR 資料處理平台，解決 HR 人員日常工作中「小但頻繁、耗時耗力」的資料處理痛點。

## 核心設計原則

1. **節省 API 成本**: 能用純 Python 規則解決的，絕不呼叫 AI
2. **範本化設計**: 所有設定可儲存為範本，重複使用  
3. **本地優先**: 企業敏感資料不上傳雲端，使用本地 SQLite

## Phase 1 已完成功能

### 核心模組 (core/)

- ✅ **db_manager.py** - SQLite 資料庫管理
  - 員工主檔管理
  - 績效紀錄追蹤
  - 訓練紀錄管理
  - 離職資料記錄
  - 提醒事項系統

- ✅ **data_processor.py** - 資料處理核心
  - 動態欄位偵測
  - 資料類型識別
  - 多種清洗操作（去空白、日期統一、重複值處理等）
  - 操作歷史記錄

- ✅ **column_matcher.py** - 欄位智能比對
  - 模糊比對找出相似欄位
  - HR 常見欄位標準化
  - 跨檔案欄位映射

### 工具模組 (utils/)

- ✅ **file_handler.py** - 檔案讀寫工具
  - 支援 Excel/CSV 格式
  - 多檔案批次處理
  - DataFrame 合併功能

### 主程式

- ✅ **app.py** - Streamlit GUI 主程式
  - 首頁儀表板
  - 員工查詢功能
  - 模組化設計，易於擴展

## 安裝與執行

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 執行應用程式

```bash
streamlit run app.py
```

應用程式將在瀏覽器中開啟 (預設 http://localhost:8501)

## 專案結構

```
hr_data_tool/
├── app.py                      # Streamlit 主程式入口
├── requirements.txt            # Python 依賴
├── config/                     # 配置檔案目錄
├── data/                       # 資料存儲目錄
│   ├── hr_database.db         # SQLite 資料庫
│   └── templates/             # 使用者範本
├── modules/                   # 功能模組 (待開發)
├── core/                      # 核心功能
│   ├── db_manager.py          # 資料庫管理
│   ├── data_processor.py      # 資料處理
│   └── column_matcher.py      # 欄位比對
├── utils/                     # 工具函數
│   └── file_handler.py        # 檔案處理
└── tests/                     # 測試資料與腳本
    └── test_data/             # 測試用 Excel 檔案
```

## 測試資料

測試資料位於 `tests/test_data/` 目錄：
- test_m4_employee_master.xlsx - 員工主檔測試資料
- test_m4_performance.xlsx - 績效紀錄測試資料
- test_m4_training.xlsx - 訓練紀錄測試資料
- 其他模組測試資料...

## 未來開發計劃

### Phase 2 - 高價值模組
- [ ] 模組1: 報表合併器 (完整實作)
- [ ] 模組6: 到期提醒系統

### Phase 3 - 進階功能
- [ ] 模組2: 資料清洗器 (完整實作)
- [ ] 模組4: 員工查詢 (資料匯入功能)

### Phase 4 - AI 整合
- [ ] 模組5: 資格檢核器
- [ ] Gemini API 整合

### Phase 5 - 自動化
- [ ] 模組3: 流程範本系統
- [ ] 排程執行功能

## 技術規格

- Python >= 3.9
- Streamlit >= 1.28.0
- Pandas >= 2.0.0
- SQLite (內建)

## 授權

© 2025 HR Data Processing Tool
