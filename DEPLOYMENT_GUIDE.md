# V2 雲端部署指南

**版本**: V2 - Production Ready
**日期**: 2026-01-05
**狀態**: ✅ 準備部署

---

## 📦 V2 版本特色

### 新增功能
1. **首頁 SOP 使用指南** - 完整的功能介紹和操作步驟
2. **測試檔案下載** - 每個功能都提供測試檔案供練習
3. **AI 開發提示詞** - 提供給使用者複製，可請 AI 開發相同功能
4. **流程範本系統** - M1、M2 支援儲存和載入流程範本
5. **全螢幕資料查看** - 所有資料表都支援全螢幕查看完整資料
6. **獨立資料庫架構** - M4、M5、M6 使用獨立資料庫，互不干擾

### 改進項目
- 移除所有開發階段標籤（Phase 1-4）
- 優化資料預覽（M2 固定顯示原始資料）
- 資料變化統計（使用 delta metrics）
- 智慧欄位辨識優化
- 批次檢核功能（M5）
- 完整的資料庫管理介面

---

## 🚀 部署選項

### 選項 1: Streamlit Community Cloud（推薦）

**優點**:
- 完全免費
- 自動 HTTPS
- 簡單易用
- 自動更新

**步驟**:

1. **準備 GitHub 儲存庫**
   ```bash
   cd v2
   git init
   git add .
   git commit -m "Initial commit - V2 deployment"
   git remote add origin https://github.com/你的帳號/hr-data-tool.git
   git push -u origin main
   ```

2. **部署到 Streamlit Cloud**
   - 前往 https://share.streamlit.io/
   - 登入 GitHub 帳號
   - 點擊 "New app"
   - 選擇您的儲存庫
   - 指定主檔案: `app.py`
   - 點擊 "Deploy"

3. **環境設定**（如需要）
   - 在 Streamlit Cloud 後台設定環境變數
   - 不需要額外設定（本專案無外部 API）

---

### 選項 2: Heroku

**優點**:
- 穩定可靠
- 支援自訂網域
- 免費方案可用

**步驟**:

1. **安裝 Heroku CLI**
   ```bash
   # Windows
   # 下載安裝: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **建立 Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
   ```

3. **建立 runtime.txt**
   ```bash
   echo "python-3.11.0" > runtime.txt
   ```

4. **部署**
   ```bash
   heroku login
   heroku create hr-data-tool
   git push heroku main
   heroku open
   ```

---

### 選項 3: AWS EC2

**優點**:
- 完全控制
- 可擴展性高
- 適合企業部署

**步驟**:

1. **啟動 EC2 實例**
   - 選擇 Ubuntu Server 22.04 LTS
   - 選擇 t2.micro（免費方案）
   - 設定安全群組（開放 8501 port）

2. **連接並安裝環境**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip

   sudo apt update
   sudo apt install python3-pip -y
   pip3 install -r requirements.txt
   ```

3. **上傳專案檔案**
   ```bash
   scp -i your-key.pem -r v2/* ubuntu@your-ec2-ip:~/hr-data-tool/
   ```

4. **執行應用程式**
   ```bash
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

5. **使用 tmux 或 systemd 保持運行**
   ```bash
   # 使用 tmux
   tmux new -s streamlit
   streamlit run app.py
   # Ctrl+B, D 離開
   ```

---

### 選項 4: Docker

**優點**:
- 環境一致性
- 易於移植
- 適合 DevOps 流程

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**部署步驟**:
```bash
# 建立映像
docker build -t hr-data-tool:v2 .

# 執行容器
docker run -p 8501:8501 hr-data-tool:v2
```

---

## 📋 部署前檢查清單

### 必要檢查
- [x] app.py 正常執行
- [x] requirements.txt 完整
- [x] 測試檔案存在於 tests/test_data/
- [x] core/ 資料夾完整
- [x] modules/ 資料夾完整
- [x] utils/ 資料夾完整
- [x] .gitignore 已設定（避免上傳 .db 檔案）

### 功能測試
- [ ] 首頁正常顯示（包含 5 個功能分頁）
- [ ] 測試檔案下載功能正常
- [ ] AI 開發提示詞正常顯示
- [ ] M1 報表合併器測試通過
- [ ] M2 資料清洗器測試通過
- [ ] M4 員工查詢測試通過
- [ ] M5 資格檢核器測試通過
- [ ] M6 到期提醒測試通過

### 安全檢查
- [x] 無硬編碼密碼
- [x] 無 API Key 外洩
- [x] .gitignore 排除敏感檔案
- [x] 資料庫檔案不會被提交

---

## 📁 V2 檔案結構

```
v2/
├── app.py                          # 主程式（含首頁 SOP）
├── requirements.txt                # Python 依賴
├── README.md                       # 專案說明
├── DEPLOYMENT_GUIDE.md             # 本文件
├── .gitignore                      # Git 忽略清單
├── core/
│   ├── __init__.py
│   ├── db_manager.py               # 資料庫管理（含範本功能）
│   ├── column_matcher.py           # 智慧欄位辨識
│   └── data_processor.py           # 資料處理
├── modules/
│   ├── __init__.py
│   ├── m1_report_merger.py         # 報表合併器（含範本）
│   ├── m2_data_cleaner.py          # 資料清洗器（含範本）
│   ├── m4_employee_dashboard.py    # 員工查詢
│   ├── m5_qualification_check.py   # 資格檢核器
│   └── m6_reminder_system.py       # 到期提醒
├── utils/
│   └── file_handler.py             # 檔案處理工具
└── tests/
    ├── test_core.py
    ├── test_phase2.py
    ├── test_phase3.py
    ├── test_module5.py
    └── test_data/
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

## 🔧 環境變數設定

本專案不需要環境變數，所有設定都在程式內或資料庫中。

如果未來需要設定環境變數（例如外部 API），可使用：

**Streamlit Cloud**:
- 在 App settings → Secrets 中設定

**Heroku**:
```bash
heroku config:set KEY=VALUE
```

**AWS EC2**:
```bash
export KEY=VALUE
```

---

## 📊 資料庫說明

### 自動生成的資料庫

應用程式首次執行時會自動建立以下資料庫（儲存在 `data/` 目錄）：

1. **workflow_templates.db** - 流程範本（M1、M2）
2. **m4_employees.db** - M4 員工主檔
3. **m4_performance.db** - M4 績效資料
4. **m4_training.db** - M4 訓練紀錄
5. **m5_qualification.db** - M5 檢核資料（含 4 個表）
6. **m6_reminders.db** - M6 提醒資料

### 資料備份

建議定期備份 `data/` 目錄：
```bash
# 本地備份
cp -r data/ backup_$(date +%Y%m%d)/

# 雲端備份（如使用 AWS）
aws s3 sync data/ s3://your-bucket/hr-data-backup/
```

---

## 🌐 網域設定（選用）

### Streamlit Cloud
- 預設網址: `https://你的應用名稱.streamlit.app`
- 可設定自訂網域（需付費方案）

### Heroku
```bash
heroku domains:add www.your-domain.com
# 然後在 DNS 設定 CNAME 指向 Heroku 提供的網址
```

### AWS
- 使用 Route 53 設定 DNS
- 配合 CloudFront 提供 HTTPS

---

## 🔒 安全性建議

### 生產環境建議

1. **使用 HTTPS**
   - Streamlit Cloud 和 Heroku 預設提供
   - AWS 需自行設定 SSL 憑證

2. **設定存取控制**
   - 使用 Streamlit 的身份驗證功能（如需要）
   - 或在前端加上 HTTP Basic Auth

3. **定期更新**
   ```bash
   pip list --outdated
   pip install --upgrade streamlit pandas openpyxl
   ```

4. **監控日誌**
   - Streamlit Cloud 提供內建日誌查看
   - AWS/Heroku 可使用 CloudWatch/Papertrail

---

## 📈 效能優化

### 快取設定

已在程式中使用 `@st.cache_resource` 快取資料庫連接：
```python
@st.cache_resource
def init_databases():
    return {...}
```

### 資料庫優化

- 定期執行 `VACUUM` 清理資料庫
- 為常用查詢欄位建立索引

---

## 🆘 故障排除

### 常見問題

**問題 1: 模組無法載入**
```
ModuleNotFoundError: No module named 'xxx'
```
**解決**: 確認 requirements.txt 完整並重新安裝
```bash
pip install -r requirements.txt
```

**問題 2: 資料庫無法寫入**
```
PermissionError: Permission denied
```
**解決**: 確認 `data/` 目錄有寫入權限
```bash
chmod 755 data/
```

**問題 3: Streamlit 無法啟動**
```
OSError: [Errno 98] Address already in use
```
**解決**: 更換 port
```bash
streamlit run app.py --server.port=8502
```

---

## 📞 支援與維護

### 技術文件
- Streamlit 文件: https://docs.streamlit.io/
- Pandas 文件: https://pandas.pydata.org/docs/
- SQLite 文件: https://www.sqlite.org/docs.html

### 問題回報
- 使用 GitHub Issues 追蹤問題
- 記錄錯誤訊息和環境資訊

---

## 🎯 部署後測試

部署完成後，請執行以下測試：

1. **首頁測試**
   - [ ] 五個功能分頁正常顯示
   - [ ] 測試檔案下載正常
   - [ ] AI 提示詞複製功能正常

2. **功能測試**
   - [ ] 使用測試檔案測試 M1 報表合併
   - [ ] 使用測試檔案測試 M2 資料清洗
   - [ ] 測試 M4 員工查詢匯入與查詢
   - [ ] 測試 M5 資格檢核（單一與批次）
   - [ ] 測試 M6 到期提醒新增與管理

3. **範本功能測試**
   - [ ] M1 儲存範本
   - [ ] M1 載入範本
   - [ ] M2 儲存範本
   - [ ] M2 載入範本

---

## ✅ 部署完成檢查

- [ ] 應用程式可正常訪問
- [ ] 所有功能正常運作
- [ ] 測試檔案可下載
- [ ] 資料庫正常建立
- [ ] 無錯誤訊息
- [ ] 效能可接受（載入時間 < 3 秒）

---

**V2 已準備好部署！**

選擇最適合您需求的部署選項，依照步驟執行即可。

如有任何問題，請參考故障排除章節或查閱相關技術文件。
