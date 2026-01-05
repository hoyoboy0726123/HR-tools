# 🚀 快速部署到 Render

**GitHub 儲存庫**: https://github.com/hoyoboy0726123/HR-tools
**狀態**: ✅ 已推送，準備部署

---

## 📋 一分鐘快速部署

### 1. 前往 Render
🔗 https://render.com/

### 2. 登入
使用 GitHub 帳號登入

### 3. 新建服務
點擊 **"New +"** → **"Web Service"**

### 4. 連接儲存庫
選擇 **hoyoboy0726123/HR-tools** 或輸入：
```
https://github.com/hoyoboy0726123/HR-tools
```

### 5. 配置服務

**複製以下設定**：

| 欄位 | 值 |
|------|-----|
| **Name** | `hr-data-tool` |
| **Region** | `Singapore` 或 `Oregon` |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true` |
| **Instance Type** | `Free` 或 `Starter ($7/月)` |

### 6. 部署
點擊 **"Create Web Service"** → 等待 2-3 分鐘

### 7. 完成！
獲得 URL：`https://hr-data-tool.onrender.com`

---

## 📝 詳細指南

請參考 **RENDER_DEPLOYMENT.md** 獲得完整的部署說明、故障排除、自訂網域等資訊。

---

## ⚡ 自動部署

已配置自動部署！

每次執行以下指令，Render 會自動重新部署：
```bash
git add .
git commit -m "更新功能"
git push origin main
```

---

## 💡 提示

- ✅ 使用 `render.yaml` 可自動配置所有設定
- ✅ Free 方案足夠測試使用
- ✅ Starter 方案 ($7/月) 推薦正式使用（不會休眠）
- ✅ 資料庫檔案不持久，每次重新部署會清空
- ✅ 測試檔案已包含在專案中，可直接下載使用

---

**需要幫助？** 查看 RENDER_DEPLOYMENT.md 的故障排除章節
