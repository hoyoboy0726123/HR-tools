# HR 資料處理工具 V2.0

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**一站式 HR 資料處理平台，提供報表合併、資料清洗、員工查詢、資格檢核、到期提醒等五大功能。**

---

## 🌟 V2.0 新功能

### ✨ 全新首頁 SOP 指南
- 詳細的功能介紹和操作步驟
- 12 個測試檔案可直接下載
- 使用技巧與常見問題
- 移除所有開發術語，更友善的介面

### 🤖 AI 開發提示詞
- 每個功能都提供完整的 AI 開發提示詞
- 複製給 AI（如 Claude、ChatGPT）即可開發相同功能
- 包含功能需求、技術規格、UI 設計等

### 💾 流程範本系統
- M1、M2 支援儲存和載入流程範本
- 一鍵套用常用設定
- 大幅提升重複性工作效率

### 📊 資料預覽優化
- 全螢幕查看完整資料（移除行數限制）
- M2 原始資料永久顯示，方便對比
- 新增資料變化統計（delta metrics）

### 🔄 批次檢核功能（M5）
- 一次檢核多位員工
- 批次結果摘要
- 批次匯出報告

---

## 📦 五大功能模組

### 1️⃣ 報表合併器（M1）
整合多份欄位名稱不統一的報表，自動識別相似欄位並合併。

**主要功能**:
- 智慧欄位辨識（不區分大小寫、支援變體）
- 垂直堆疊 / 依 Key 合併
- 移除重複資料
- 流程範本儲存/載入

**使用情境**:
- 合併各部門的完訓報表
- 整合不同分公司的員工資料
- 彙整多個月份的數據

---

### 2️⃣ 資料清洗器（M2）
對髒亂的資料進行清洗，包括去除空白、統一日期格式、移除重複值等。

**主要功能**:
- 7 種清洗操作（空白、日期、重複值、空值、欄位等）
- 原始資料與清洗結果對比
- 資料變化統計
- 流程範本儲存/載入

**使用情境**:
- 清理 Excel 中的前後空白
- 統一不一致的日期格式
- 移除重複記錄

---

### 3️⃣ 員工查詢（M4）
整合員工基本資料、績效歷程、訓練紀錄於單一介面。

**主要功能**:
- 多選員工查詢
- 顯示完整員工資訊（基本資料、績效、訓練、離職）
- 單一/批次匯出
- 獨立資料庫（3 個）

**使用情境**:
- 查詢員工完整歷程
- 批次匯出員工報告
- 管理員工資料庫

---

### 4️⃣ 資格檢核器（M5）
自動檢核離職員工的回任資格，基於離職類型、歷史績效、訓練記錄等。

**主要功能**:
- 單一/批次檢核
- 4 項檢核指標（員工資料、離職記錄、績效、訓練）
- 綜合判斷（核准/審查/拒絕）
- 純 Python 規則檢核（無 AI 成本）

**使用情境**:
- 離職員工申請回任
- 批次評估多位申請人
- 產生檢核報告

---

### 5️⃣ 到期提醒（M6）
管理證照、合約、試用期等各類到期事項。

**主要功能**:
- 手動新增/批次匯入提醒
- 自動標示到期狀態（已逾期/即將到期/正常）
- 狀態/類型篩選
- 標記完成、刪除、匯出

**使用情境**:
- 證照到期提醒
- 試用期屆滿通知
- 合約到期追蹤

---

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 執行應用程式

```bash
streamlit run app.py
```

應用程式將在瀏覽器中開啟（預設 http://localhost:8501）

---

## 📂 專案結構

```
v2/
├── app.py                          # 主程式（含首頁 SOP 指南）
├── requirements.txt                # Python 依賴套件
├── README.md                       # 專案說明（本文件）
├── DEPLOYMENT_GUIDE.md             # 雲端部署指南
├── V2_RELEASE_NOTES.md             # V2 版本發佈說明
├── .gitignore                      # Git 忽略清單
│
├── core/                           # 核心功能
│   ├── db_manager.py               # 資料庫管理（含範本功能）
│   ├── column_matcher.py           # 智慧欄位辨識
│   ├── data_processor.py           # 資料處理
│   └── ai_client.py                # AI 客戶端（M5 已不使用）
│
├── modules/                        # 功能模組
│   ├── m1_report_merger.py         # 報表合併器
│   ├── m2_data_cleaner.py          # 資料清洗器
│   ├── m4_employee_dashboard.py    # 員工查詢
│   ├── m5_qualification_check.py   # 資格檢核器
│   └── m6_reminder_system.py       # 到期提醒
│
├── utils/                          # 工具函數
│   └── file_handler.py             # 檔案處理
│
└── tests/                          # 測試檔案
    ├── test_core.py
    ├── test_phase2.py
    ├── test_phase3.py
    ├── test_module5.py
    └── test_data/                  # 測試資料（12 個 Excel 檔案）
        ├── test_m1_report_A.xlsx
        ├── test_m1_report_B.xlsx
        ├── test_m1_report_C.xlsx
        ├── test_m2_dirty_data.xlsx
        ├── test_m4_employee_master.xlsx
        ├── test_m4_performance.xlsx
        ├── test_m4_training.xlsx
        ├── test_m5_employee_master.xlsx
        ├── test_m5_separation.xlsx
        ├── test_m5_performance.xlsx
        ├── test_m5_training.xlsx
        └── test_m6_new_hires.xlsx
```

---

## 💻 技術棧

- **前端框架**: Streamlit 1.31+
- **資料處理**: Pandas 2.1+
- **資料庫**: SQLite 3
- **檔案處理**: openpyxl 3.1+
- **Python 版本**: 3.11+

---

## 📊 資料庫架構

應用程式會自動建立以下資料庫（儲存在 `data/` 目錄）：

| 資料庫 | 說明 | 使用模組 |
|--------|------|---------|
| workflow_templates.db | 流程範本 | M1, M2 |
| m4_employees.db | 員工主檔 | M4 |
| m4_performance.db | 績效資料 | M4 |
| m4_training.db | 訓練紀錄 | M4 |
| m5_qualification.db | 檢核資料（4 個表） | M5 |
| m6_reminders.db | 提醒資料 | M6 |

**獨立資料庫設計的優點**:
- 資料隔離，避免誤操作
- 清空一個模組不影響其他模組
- 更清晰的資料管理

---

## 🎯 使用流程

### 1. 首頁瀏覽

啟動應用程式後，首頁提供：
- 五大功能詳細介紹
- 操作步驟（SOP）
- 測試檔案下載
- AI 開發提示詞
- 使用技巧與常見問題

### 2. 選擇功能

從側邊欄選擇需要的功能模組。

### 3. 上傳資料

- 使用提供的測試檔案進行練習
- 或上傳您自己的資料檔案

### 4. 執行操作

依照 SOP 步驟執行操作。

### 5. 下載結果

匯出處理後的資料為 Excel 檔案。

### 6. 儲存範本（M1、M2）

如果需要重複執行相同流程，可儲存為範本。

---

## 🔍 測試檔案說明

所有測試檔案都可在**首頁**直接下載：

### M1 報表合併器
- **test_m1_report_A/B/C.xlsx**: 模擬不同部門的完訓報表，欄位名稱略有不同

### M2 資料清洗器
- **test_m2_dirty_data.xlsx**: 包含多種髒資料問題（空白、日期不統一、重複值、空值）

### M4 員工查詢
- **test_m4_employee_master.xlsx**: 員工主檔範例
- **test_m4_performance.xlsx**: 績效資料範例
- **test_m4_training.xlsx**: 訓練紀錄範例

### M5 資格檢核器
- **test_m5_employee_master.xlsx**: 員工資料範例
- **test_m5_separation.xlsx**: 離職記錄範例（包含多種離職類型）
- **test_m5_performance.xlsx**: 績效資料範例（包含不同等級）
- **test_m5_training.xlsx**: 訓練記錄範例

### M6 到期提醒
- **test_m6_new_hires.xlsx**: 新進員工試用期提醒範例

---

## 🌐 雲端部署

詳細部署指南請參考 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**推薦部署平台**:

1. **Streamlit Community Cloud**（推薦）
   - 完全免費
   - 自動 HTTPS
   - 一鍵部署

2. **Heroku**
   - 穩定可靠
   - 支援自訂網域

3. **AWS EC2**
   - 完全控制
   - 適合企業部署

4. **Docker**
   - 環境一致性
   - 易於移植

---

## 🔐 安全性

- ✅ 所有資料儲存在本地，不上傳雲端
- ✅ 無外部 API 依賴（M5 已移除 AI）
- ✅ 無敏感資料暴露風險
- ✅ 支援 HTTPS 部署

---

## 💡 使用技巧

1. **善用範本功能**
   處理重複性工作時，儲存範本可大幅節省時間。

2. **全螢幕查看**
   所有資料預覽都支援點擊右上角按鈕全螢幕查看。

3. **批次操作**
   M4、M5 支援批次處理，一次處理多筆資料更有效率。

4. **資料獨立**
   各模組使用獨立資料庫，互不干擾。

5. **測試檔案練習**
   使用提供的測試檔案熟悉功能後，再處理實際資料。

---

## ❓ 常見問題

### Q: 上傳的檔案欄位名稱和系統不一樣怎麼辦？

**A**: 系統支援智慧欄位辨識，會自動匹配相似欄位名稱。例如：「工號」、「emp_id」、「員工編號」都會被識別為同一欄位。

### Q: 範本可以跨電腦使用嗎？

**A**: 範本儲存在本地資料庫中（workflow_templates.db），如需跨電腦使用，請複製 `data/` 目錄下的資料庫檔案。

### Q: 資料會上傳到雲端嗎？

**A**: 所有資料都儲存在本地，不會上傳到任何雲端服務，確保資料安全。

### Q: 如何清空所有資料？

**A**: 每個模組的「資料庫管理」分頁都有清空功能，可選擇性清空特定資料庫。

### Q: M5 還需要設定 API Key 嗎？

**A**: V2 已完全移除 M5 的 AI 功能，不需要任何 API Key，也沒有使用成本。

### Q: 可以處理多大的檔案？

**A**: 建議單一檔案 < 10,000 行。超過可能導致載入緩慢，但仍可正常處理。

---

## 🔄 版本歷史

### V2.0.0 (2026-01-05)
- ✨ 全新首頁 SOP 指南
- ✨ AI 開發提示詞功能
- ✨ 流程範本系統（M1、M2）
- ✨ 批次檢核功能（M5）
- 🎨 資料預覽優化（全螢幕、原始資料固定顯示）
- 🔧 M5 移除 AI，改為純 Python 規則
- 🗄️ 獨立資料庫架構（M4、M5、M6）
- 📊 資料變化統計（M2）
- 🐛 修復多項 bug

### V1.0.0 (2026-01-03)
- 初始版本
- 五大功能模組完成
- 基礎資料庫架構

---

## 🤝 貢獻

歡迎提出問題和建議！

---

## 📄 授權

MIT License

---

## 📞 支援

- 📖 查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 了解部署方式
- 📝 查看 [V2_RELEASE_NOTES.md](V2_RELEASE_NOTES.md) 了解詳細更新內容
- 💡 參考首頁的使用指南和常見問題

---

## 🎉 開始使用

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 執行應用程式
streamlit run app.py

# 3. 在瀏覽器中開啟 http://localhost:8501

# 4. 從首頁下載測試檔案開始練習！
```

---

**打造高效的 HR 資料處理流程，從 V2.0 開始！** 🚀
