# Render 部署指南

**平台**: Render
**專案**: HR 資料處理工具 V2.0
**GitHub**: https://github.com/hoyoboy0726123/HR-tools

---

## 🚀 快速部署步驟

### 1. 登入 Render

前往 https://render.com/ 並登入您的帳號（可使用 GitHub 帳號登入）。

---

### 2. 新建 Web Service

1. 點擊 Dashboard 的 **"New +"** 按鈕
2. 選擇 **"Web Service"**

---

### 3. 連接 GitHub 儲存庫

**方式 A: 從 GitHub 儲存庫列表選擇**
1. 如果已授權 Render 訪問 GitHub，會看到儲存庫列表
2. 找到 **hoyoboy0726123/HR-tools**
3. 點擊 **"Connect"**

**方式 B: 使用公開儲存庫 URL**
1. 點擊 **"Public Git repository"**
2. 輸入: `https://github.com/hoyoboy0726123/HR-tools`
3. 點擊 **"Continue"**

---

### 4. 配置 Web Service

填寫以下設定：

#### 基本設定
- **Name**: `hr-data-tool`（或您喜歡的名稱）
- **Region**: 選擇 **Singapore** 或 **Oregon**（較接近亞洲）
- **Branch**: `main`
- **Root Directory**: 留空（使用根目錄）

#### 運行環境
- **Runtime**: **Python 3**
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
  ```

#### 實例設定
- **Instance Type**:
  - **Free**（免費方案，適合測試）
  - 或 **Starter**（$7/月，更穩定，推薦正式使用）

#### 環境變數（可選）
點擊 **"Advanced"** → **"Add Environment Variable"**

可添加以下變數（但本專案不需要）：
```
PYTHON_VERSION = 3.11.0
```

---

### 5. 部署

1. 檢查所有設定無誤
2. 點擊底部的 **"Create Web Service"**
3. Render 開始自動部署

---

## 📊 部署過程

部署會經歷以下階段：

### 1️⃣ Building (建置中)
```
==> Cloning from https://github.com/hoyoboy0726123/HR-tools...
==> Installing dependencies...
pip install -r requirements.txt
```
**預計時間**: 2-3 分鐘

### 2️⃣ Deploying (部署中)
```
==> Starting service...
streamlit run app.py
```
**預計時間**: 30 秒

### 3️⃣ Live (運行中) ✅
```
Your service is live at https://hr-data-tool.onrender.com
```

---

## 🌐 訪問您的應用程式

部署成功後，您會獲得一個 URL：

**格式**: `https://您的服務名稱.onrender.com`

**範例**: `https://hr-data-tool.onrender.com`

點擊 URL 即可訪問您的 HR 資料處理工具！

---

## ⚙️ Render 自動化配置（render.yaml）

本專案已包含 `render.yaml` 配置檔案，Render 會自動讀取此檔案。

如果您使用 **"Infrastructure as Code"** 方式部署：

1. 在 Render Dashboard 選擇 **"New +"** → **"Blueprint"**
2. 連接 GitHub 儲存庫
3. Render 會自動讀取 `render.yaml` 並配置

**render.yaml 內容**:
```yaml
services:
  - type: web
    name: hr-data-tool
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

---

## 🔄 自動部署

Render 支援自動部署：

✅ **每次推送到 GitHub main 分支，Render 會自動重新部署**

### 測試自動部署
```bash
# 修改檔案後
git add .
git commit -m "Update feature"
git push origin main

# Render 會自動偵測並重新部署
```

---

## 📝 部署後檢查

### 1. 查看日誌

在 Render Dashboard → 您的服務 → **"Logs"**

正常運行會看到：
```
You can now view your Streamlit app in your browser.
Network URL: http://0.0.0.0:10000
External URL: https://hr-data-tool.onrender.com
```

### 2. 測試功能

訪問您的應用程式 URL，測試：
- ✅ 首頁正常顯示
- ✅ 五個功能分頁載入
- ✅ 測試檔案可以下載
- ✅ AI 提示詞正常顯示
- ✅ 各功能模組運作正常

---

## 🐛 常見問題排除

### 問題 1: 部署失敗 - 找不到 requirements.txt

**錯誤訊息**:
```
ERROR: Could not open requirements file
```

**解決方法**:
- 確認 `requirements.txt` 在根目錄
- 檢查 GitHub 儲存庫是否包含此檔案

---

### 問題 2: 應用程式無法啟動

**錯誤訊息**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**解決方法**:
檢查 Build Command 是否正確：
```bash
pip install -r requirements.txt
```

---

### 問題 3: 應用程式啟動但無法訪問

**錯誤訊息**:
```
This site can't be reached
```

**解決方法**:
檢查 Start Command 是否包含正確的 port 設定：
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

---

### 問題 4: Free 方案應用程式休眠

**現象**:
- 15 分鐘無活動後，應用程式會休眠
- 下次訪問需要等待 30-60 秒喚醒

**解決方法**:
- 升級到 **Starter 方案**（$7/月）
- 或使用 UptimeRobot 等服務定期 ping（但 Render 可能禁止此方式）

---

### 問題 5: 資料庫檔案無法持久化

**現象**:
- 每次重新部署後，資料庫清空

**原因**:
- Render Free/Starter 方案的檔案系統不持久

**解決方法**:

**選項 A**: 使用 Render 的 Disk 功能（需付費）
1. 在 Service 設定中添加 Disk
2. 將 `data/` 目錄掛載到 Disk

**選項 B**: 使用外部資料庫
1. 使用 Render PostgreSQL（免費方案可用）
2. 修改程式碼連接 PostgreSQL

**選項 C**: 接受資料不持久（適合測試）
- 每次重新部署視為新環境
- 使用測試檔案重新匯入

---

## 💰 Render 定價方案

### Free 方案
- ✅ 750 小時/月
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ 自動 HTTPS
- ⚠️ 15 分鐘無活動會休眠
- ⚠️ 檔案系統不持久

### Starter 方案（推薦）
- ✅ $7/月
- ✅ 512 MB RAM
- ✅ 0.5 CPU
- ✅ 自動 HTTPS
- ✅ 不會休眠
- ⚠️ 檔案系統仍不持久

### Standard 方案
- ✅ $25/月起
- ✅ 2 GB RAM 起
- ✅ 1 CPU 起
- ✅ 可添加持久化 Disk

---

## 🔒 安全性設定

### 環境變數（如需要）

如果未來需要添加 API Key：

1. 在 Render Dashboard → 您的服務 → **"Environment"**
2. 點擊 **"Add Environment Variable"**
3. 添加變數：
   ```
   Key: GEMINI_API_KEY
   Value: 您的 API Key
   ```
4. 點擊 **"Save Changes"**
5. Render 會自動重新部署

### HTTPS

Render 自動提供 HTTPS，無需額外設定。

---

## 📊 監控與日誌

### 查看即時日誌

Render Dashboard → 您的服務 → **"Logs"**

### 查看資源使用

Render Dashboard → 您的服務 → **"Metrics"**

可查看：
- CPU 使用率
- 記憶體使用率
- 請求次數
- 回應時間

---

## 🔄 更新應用程式

### 方式 1: 推送到 GitHub（自動）

```bash
# 修改程式碼
git add .
git commit -m "更新功能"
git push origin main

# Render 會自動偵測並部署
```

### 方式 2: 手動重新部署

1. Render Dashboard → 您的服務
2. 點擊 **"Manual Deploy"** → **"Deploy latest commit"**

### 方式 3: 清除快取重新部署

1. Render Dashboard → 您的服務
2. 點擊 **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## 🌐 自訂網域（選用）

### 添加自訂網域

1. Render Dashboard → 您的服務 → **"Settings"**
2. 找到 **"Custom Domain"** 區塊
3. 點擊 **"Add Custom Domain"**
4. 輸入您的網域（如 `hr-tool.yourcompany.com`）
5. 在您的 DNS 設定中添加 CNAME 記錄：
   ```
   CNAME hr-tool.yourcompany.com → hr-data-tool.onrender.com
   ```
6. 等待 DNS 生效（通常 5-30 分鐘）
7. Render 會自動配置 HTTPS

---

## 📞 支援資源

- **Render 文件**: https://render.com/docs
- **Streamlit 部署指南**: https://docs.streamlit.io/deploy/render
- **本專案 GitHub**: https://github.com/hoyoboy0726123/HR-tools

---

## ✅ 部署完成檢查清單

部署成功後，請確認：

- [ ] 應用程式可正常訪問（URL 正常開啟）
- [ ] 首頁顯示五大功能分頁
- [ ] 測試檔案可以下載
- [ ] AI 開發提示詞正常顯示
- [ ] M1 報表合併器功能正常
- [ ] M2 資料清洗器功能正常
- [ ] M4 員工查詢功能正常
- [ ] M5 資格檢核器功能正常
- [ ] M6 到期提醒功能正常
- [ ] 範本儲存功能正常（M1、M2）
- [ ] 資料匯入功能正常（各模組）
- [ ] 無錯誤訊息出現

---

## 🎉 部署成功！

您的 HR 資料處理工具已成功部署到 Render！

**下一步**:
1. 測試所有功能
2. 分享 URL 給團隊成員
3. 收集使用回饋
4. 持續優化改進

**應用程式 URL**: `https://您的服務名稱.onrender.com`

享受您的雲端 HR 工具！🚀
