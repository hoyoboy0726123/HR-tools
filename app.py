# -*- coding: utf-8 -*-
import streamlit as st
from core.db_manager import DBManager
from core.user_manager import UserManager
from core.db_migration import migrate_add_user_id_column

@st.cache_resource
def init_databases():
    """Initialize all separate databases"""
    # 確保資料庫檔案存在後執行遷移
    migrate_add_user_id_column()
    return {
        'employees': DBManager('employees'),
        'reminders': DBManager('reminders'),
        'performance': DBManager('performance'),
        'training': DBManager('training'),
        'separation': DBManager('separation')
    }

dbs = init_databases()

# 初始化 UserManager
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = UserManager()

# 初始化用戶登入狀態
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# ========== 登入頁面 ==========
if not st.session_state.logged_in:
    st.title('👥 HR 資料處理工具')
    st.markdown('### 🔐 請登入以開始使用')

    st.info('💡 **簡易登入說明**：只需輸入您的 Email 即可登入，無需密碼。您的資料將與其他用戶隔離。')

    # 登入表單
    with st.form('login_form'):
        email = st.text_input(
            '📧 Email 地址',
            placeholder='example@company.com',
            help='請輸入您的工作 Email'
        )

        submit = st.form_submit_button('🚀 登入 / 註冊', use_container_width=True)

        if submit:
            if email:
                result = st.session_state.user_manager.register_or_login(email)

                if result['success']:
                    st.session_state.logged_in = True
                    st.session_state.user_info = {
                        'user_id': result['user_id'],
                        'email': result['email'],
                        'email_hash': result['email_hash']
                    }
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
            else:
                st.warning('⚠️ 請輸入 Email 地址')

    st.divider()

    st.markdown("""
    ### ℹ️ 關於此工具

    本工具提供五大 HR 資料處理功能：
    - 📊 **報表合併器** - 整合多份格式不同的報表
    - 🧹 **資料清洗器** - 清理和標準化資料
    - 👥 **員工查詢** - 整合查詢員工完整資訊
    - ✅ **資格檢核器** - 自動檢核離職回任資格
    - 🔔 **到期提醒** - 管理證照、合約等到期事項

    ### 🔒 資料安全
    - 所有資料儲存在系統中，但會依照您的 Email 進行隔離
    - 您只能看到和管理自己的資料
    - Email 經過加密處理，保護您的隱私
    """)

    st.stop()

# ========== 主應用程式（已登入） ==========

# 初始化 session state 來管理頁面導航
if 'current_page' not in st.session_state:
    st.session_state.current_page = '首頁'

st.sidebar.title('HR 資料處理工具')

# 顯示用戶資訊
if st.session_state.user_info:
    st.sidebar.caption(f'👤 {st.session_state.user_info["email"]}')
    if st.sidebar.button('🚪 登出', use_container_width=True):
        # 清除登入狀態
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.session_state.current_page = '首頁'
        st.success('✅ 已成功登出')
        st.rerun()

st.sidebar.divider()

# 首頁按鈕（獨立區域）
if st.sidebar.button('🏠 返回首頁', use_container_width=True, type='primary' if st.session_state.current_page == '首頁' else 'secondary'):
    st.session_state.current_page = '首頁'
    st.rerun()

st.sidebar.divider()

# 功能模組選擇
st.sidebar.subheader('功能模組')

# 定義所有功能模組
all_modules = [
    '報表合併器',
    '資料清洗器',
    '員工查詢',
    '資格檢核器',
    '到期提醒',
]

# 使用按鈕來替代 radio，這樣可以不預選任何項目
for module in all_modules:
    is_selected = (st.session_state.current_page == module)
    button_type = 'primary' if is_selected else 'secondary'

    if st.sidebar.button(
        module,
        use_container_width=True,
        type=button_type,
        key=f'btn_{module}'
    ):
        st.session_state.current_page = module
        st.rerun()

# 根據當前頁面顯示內容
if st.session_state.current_page == '首頁':
    st.title('📚 HR 資料處理工具 - 使用指南')
    st.write('歡迎使用 HR 資料處理工具平台！本指南將幫助您快速上手五大功能模組。')

    # 功能導覽
    st.info('💡 **快速導覽**：請點選下方功能標籤查看詳細使用說明，每個功能都提供測試檔案供您練習。')

    # 建立功能分頁
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        '📊 報表合併器',
        '🧹 資料清洗器',
        '👥 員工查詢',
        '✅ 資格檢核器',
        '🔔 到期提醒'
    ])

    # ========== 功能 1: 報表合併器 ==========
    with tab1:
        st.header('📊 報表合併器')
        st.markdown('### 功能說明')
        st.write('整合多份欄位名稱不統一的報表，自動識別相似欄位並合併成單一報表。')

        st.markdown('### 使用情境')
        st.write("""
        - 每月收到各部門格式不同的完訓報表，需要整合成一份
        - 不同分公司的員工資料欄位名稱略有差異（如「工號」、「員工編號」、「EMP_ID」）
        - 需要將垂直或橫向合併多個 Excel 檔案
        """)

        st.markdown('### 操作步驟（SOP）')
        st.markdown("""
        **步驟 1：上傳報表檔案**
        1. 點選左側選單「報表合併器」
        2. 上傳 2 個以上的 Excel 或 CSV 檔案（可多選）
        3. 系統會自動顯示每個檔案的預覽和欄位列表

        **步驟 2：智慧欄位對齊**
        1. 系統會自動識別相似欄位（例如：工號、emp_id、員工編號）
        2. 確認系統建議的「統一欄位名稱」是否正確
        3. 如需修改，可直接編輯欄位名稱
        4. 對於單獨欄位，可選擇「保持原樣」或「對應到其他欄位」

        **步驟 3：選擇合併方式**
        1. **垂直堆疊**：將所有資料上下疊加（適用於相同格式的多筆資料）
        2. **依 Key 合併**：根據共同欄位橫向合併（適用於需要關聯的資料）
           - 選擇合併鍵（通常是工號、員工編號等）
           - 選擇合併方式：
             - 外部合併：保留所有資料
             - 內部合併：只保留共同資料
             - 左側合併：以第一個檔案為主
        3. 勾選「移除重複資料」（建議）

        **步驟 4：執行合併與匯出**
        1. 點擊「🚀 執行合併」
        2. 查看合併結果預覽（可點擊全螢幕查看完整資料）
        3. 點擊「📥 下載合併結果」匯出 Excel 檔案
        4. （選擇性）儲存為範本，供下次使用
        """)

        st.markdown('### 💾 儲存流程範本')
        st.write("""
        完成合併後，可將設定儲存為範本：
        1. 在結果頁面找到「💾 儲存此流程為範本」
        2. 輸入範本名稱（例如：月報整合流程）
        3. 輸入說明（選填）
        4. 點擊「儲存範本」

        下次處理相同格式的報表時：
        1. 展開「📁 流程範本管理」
        2. 點選「載入範本」分頁
        3. 選擇已儲存的範本
        4. 上傳新檔案後，設定會自動套用！
        """)

        st.markdown('### 📥 測試檔案下載')
        st.write('請下載以下測試檔案進行練習：')

        import os
        test_files_m1 = [
            'test_m1_report_A.xlsx',
            'test_m1_report_B.xlsx',
            'test_m1_report_C.xlsx'
        ]

        col1, col2, col3 = st.columns(3)
        for idx, filename in enumerate(test_files_m1):
            file_path = f'tests/test_data/{filename}'
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                with [col1, col2, col3][idx]:
                    st.download_button(
                        label=f'📄 {filename}',
                        data=file_data,
                        file_name=filename,
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )

        st.caption('💡 提示：這三個檔案模擬了不同部門的完訓報表，欄位名稱略有不同，適合測試合併功能。')

        st.markdown('### 🤖 AI 開發提示詞')
        st.write('如果您想要請 AI 開發類似的報表合併功能，可以複製以下提示詞：')

        ai_prompt_m1 = """請幫我開發一個報表合併工具，需求如下：

**功能需求：**
1. 支援上傳多個 Excel 或 CSV 檔案（至少 2 個）
2. 自動識別不同檔案中相似的欄位名稱（例如：「工號」、「emp_id」、「員工編號」應被視為同一欄位）
3. 提供欄位對齊功能，讓使用者確認或修改統一的欄位名稱
4. 支援兩種合併方式：
   - 垂直堆疊：將所有資料上下疊加（適合相同格式的多筆資料）
   - 依 Key 合併：根據共同欄位橫向合併（支援 inner、outer、left 合併方式）
5. 提供移除重複資料的選項
6. 合併完成後可預覽結果並匯出為 Excel 檔案
7. 支援流程範本儲存與載入功能（儲存欄位對應設定、合併方式等）

**技術需求：**
- 使用 Python + Streamlit 開發網頁介面
- 使用 Pandas 處理資料
- 智慧欄位辨識：不區分大小寫、支援常見變體（如底線、空格、中英文）
- 範本儲存到資料庫（SQLite）

**使用者介面：**
- 檔案上傳區（支援多選）
- 檔案預覽與欄位列表展示
- 欄位對齊設定介面
- 合併方式選擇（radio button 或 selectbox）
- 結果預覽（可全螢幕查看）
- 匯出按鈕
- 範本管理介面（新建、載入、管理）

請提供完整的程式碼實作。"""

        st.code(ai_prompt_m1, language='text')
        st.caption('💡 複製此提示詞給 AI（如 Claude、ChatGPT），即可快速開發類似功能。')

    # ========== 功能 2: 資料清洗器 ==========
    with tab2:
        st.header('🧹 資料清洗器')
        st.markdown('### 功能說明')
        st.write('對髒亂的資料進行清洗，包括去除空白、統一日期格式、移除重複值、填補空值等。')

        st.markdown('### 使用情境')
        st.write("""
        - Excel 資料有多餘的前後空白字元
        - 日期格式不統一（2024/01/05、2024-01-05、01/05/2024）
        - 資料有重複記錄需要移除
        - 部分欄位有空值需要填補
        - 欄位名稱需要重新命名或刪除
        """)

        st.markdown('### 操作步驟（SOP）')
        st.markdown("""
        **步驟 1：上傳原始資料**
        1. 點選左側選單「資料清洗器」
        2. 上傳需要清洗的 Excel 或 CSV 檔案
        3. 查看「原始資料預覽」和「欄位分析」（包含資料類型、空值數、唯一值數）

        **步驟 2：設定清洗操作**

        系統提供以下清洗選項：

        1. **去除前後空白**
           - 選擇目標欄位
           - 點擊「加入步驟」

        2. **統一日期格式**
           - 選擇日期欄位
           - 選擇目標格式（YYYY-MM-DD、YYYY/MM/DD 等）
           - 點擊「加入步驟」

        3. **移除重複值**
           - 選擇判斷重複的欄位（可多選）
           - 選擇保留第一筆或最後一筆
           - 點擊「加入步驟」

        4. **填入空值**
           - 選擇目標欄位
           - 輸入填補值（例如：0、N/A、平均值）
           - 點擊「加入步驟」

        5. **重新命名欄位**
           - 選擇要改名的欄位
           - 輸入新名稱
           - 點擊「加入步驟」

        6. **轉換資料類型**
           - 選擇欄位
           - 選擇目標類型（string、numeric、datetime）
           - 點擊「加入步驟」

        7. **刪除欄位**
           - 選擇要刪除的欄位
           - 點擊「加入步驟」

        **步驟 3：查看待執行步驟**
        1. 所有加入的步驟會顯示在「待執行步驟」列表
        2. 可點擊「刪除」移除不需要的步驟
        3. 確認無誤後，點擊「執行全部步驟」

        **步驟 4：查看清洗結果**
        1. 向上滾動查看「原始資料預覽」（固定顯示）
        2. 向下查看「清洗結果預覽」
        3. 比對「資料變化統計」：
           - 資料筆數變化
           - 欄位數變化
           - 空值總數變化
        4. 點擊「下載清洗結果」匯出 Excel 檔案
        5. （選擇性）儲存為範本
        """)

        st.markdown('### 💾 儲存流程範本')
        st.write("""
        清洗完成後，可將清洗步驟儲存為範本：
        1. 在結果頁面找到「💾 儲存此清洗流程為範本」
        2. 輸入範本名稱（例如：員工資料清洗流程）
        3. 點擊「儲存範本」

        下次處理相同格式的髒資料時，載入範本即可自動套用所有清洗步驟！
        """)

        st.markdown('### 📥 測試檔案下載')
        st.write('請下載以下測試檔案進行練習：')

        test_file_m2 = 'test_m2_dirty_data.xlsx'
        file_path = f'tests/test_data/{test_file_m2}'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            st.download_button(
                label=f'📄 {test_file_m2}',
                data=file_data,
                file_name=test_file_m2,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        st.caption('💡 提示：此檔案包含多種常見的髒資料問題（空白、日期不統一、重複值、空值等），適合測試清洗功能。')

        st.markdown('### 🤖 AI 開發提示詞')
        st.write('如果您想要請 AI 開發類似的資料清洗功能，可以複製以下提示詞：')

        ai_prompt_m2 = """請幫我開發一個資料清洗工具，需求如下：

**功能需求：**
1. 支援上傳 Excel 或 CSV 檔案
2. 顯示原始資料預覽和欄位分析（資料類型、空值數、唯一值數）
3. 提供以下清洗操作（可加入多個步驟）：
   - 去除前後空白：移除文字欄位的前後空白字元
   - 統一日期格式：將日期欄位轉換為指定格式（YYYY-MM-DD、YYYY/MM/DD 等）
   - 移除重複值：根據指定欄位移除重複資料（可選保留第一筆或最後一筆）
   - 填入空值：將空值填補為指定值（可支援固定值、平均值、中位數等）
   - 重新命名欄位：修改欄位名稱
   - 轉換資料類型：將欄位轉換為 string、numeric 或 datetime
   - 刪除欄位：移除不需要的欄位
4. 顯示待執行步驟列表（可刪除個別步驟）
5. 執行清洗後顯示結果預覽
6. 提供資料變化統計（筆數、欄位數、空值數的前後對比）
7. 匯出清洗後的資料為 Excel 檔案
8. 支援清洗流程範本儲存與載入（儲存所有清洗步驟）

**技術需求：**
- 使用 Python + Streamlit 開發網頁介面
- 使用 Pandas 處理資料
- 使用 session_state 管理清洗步驟列表
- 範本儲存到資料庫（SQLite）

**使用者介面：**
- 檔案上傳區
- 原始資料預覽（固定顯示，不受清洗影響）
- 欄位分析表格
- 清洗操作設定區（每種操作有對應的參數設定）
- 待執行步驟列表（顯示所有已加入的步驟）
- 執行按鈕
- 清洗結果預覽（可全螢幕查看）
- 資料變化統計（使用 metric 顯示 delta）
- 匯出按鈕
- 範本管理介面

請提供完整的程式碼實作。"""

        st.code(ai_prompt_m2, language='text')
        st.caption('💡 複製此提示詞給 AI（如 Claude、ChatGPT），即可快速開發類似功能。')

    # ========== 功能 3: 員工查詢 ==========
    with tab3:
        st.header('👥 員工查詢')
        st.markdown('### 功能說明')
        st.write('整合員工基本資料、績效歷程、訓練紀錄於單一介面，支援多選查詢和批次匯出。')

        st.markdown('### 使用情境')
        st.write("""
        - 需要查詢員工的完整資料（基本資料 + 績效 + 訓練 + 離職記錄）
        - 一次查詢多位員工的資料並批次匯出
        - 需要員工歷程的完整視圖以進行評估
        """)

        st.markdown('### 操作步驟（SOP）')
        st.markdown("""
        **步驟 1：匯入資料**

        1. 點選「資料匯入」分頁
        2. 選擇匯入類型：
           - **員工主檔**：工號、姓名、部門、到職日（必要）
           - **績效資料**：工號、年度、考績、分數
           - **訓練紀錄**：工號、課程名稱、課程類別、時數、完成日期
        3. 上傳檔案並查看預覽
        4. 點擊「執行匯入」
        5. 查看匯入結果（成功筆數、失敗筆數）

        **步驟 2：查詢員工**

        1. 回到「查詢員工」分頁
        2. 使用多選下拉選單選擇要查詢的員工（可多選）
        3. 系統會顯示每位員工的：
           - 基本資料（工號、姓名、部門、狀態、到職日）
           - 績效歷程（年度、考績、分數、平均分數）
           - 訓練紀錄（課程名稱、類別、時數、總完訓時數）
           - 離職紀錄（如果有）

        **步驟 3：匯出資料**

        單一員工匯出：
        1. 在員工資料卡片中，點擊「📄 匯出此員工」
        2. 會產生包含所有資料的 Excel 檔案（多個分頁）

        批次匯出：
        1. 點擊「加入到批次匯出」將員工加入清單
        2. 查看「📋 批次匯出清單」中的員工
        3. 選擇匯出方式：
           - **📊 下載總表**：所有員工在一個分頁（摘要格式）
           - **📥 下載詳細分頁**：每位員工一個分頁（完整資料）
        4. 點擊「🗑️ 清空清單」可重新選擇

        **步驟 4：資料庫管理**

        1. 點選「資料庫管理」分頁
        2. 選擇要管理的資料庫（員工主檔、績效資料、訓練紀錄）
        3. 查看資料庫內容
        4. 可選擇「清空資料庫」或「匯出資料庫內容」
        """)

        st.markdown('### 📥 測試檔案下載')
        st.write('請下載以下測試檔案進行練習：')

        test_files_m4 = [
            ('test_m4_employee_master.xlsx', '員工主檔'),
            ('test_m4_performance.xlsx', '績效資料'),
            ('test_m4_training.xlsx', '訓練紀錄')
        ]

        for filename, desc in test_files_m4:
            file_path = f'tests/test_data/{filename}'
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                st.download_button(
                    label=f'📄 {filename} ({desc})',
                    data=file_data,
                    file_name=filename,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key=f'download_m4_{filename}'
                )

        st.caption('💡 提示：請依序匯入員工主檔 → 績效資料 → 訓練紀錄，然後就可以查詢完整的員工資訊。')

        st.markdown('### 🤖 AI 開發提示詞')
        st.write('如果您想要請 AI 開發類似的員工查詢系統，可以複製以下提示詞：')

        ai_prompt_m4 = """請幫我開發一個員工資料整合查詢系統，需求如下：

**功能需求：**
1. 資料匯入功能：
   - 員工主檔：工號、姓名、部門、職位、到職日、狀態
   - 績效資料：工號、年度、考績等級、分數
   - 訓練紀錄：工號、課程名稱、課程類別、時數、完成日期
   - 支援智慧欄位辨識（不區分大小寫、支援常見變體）
   - 顯示匯入統計（成功筆數、失敗筆數）

2. 員工查詢功能：
   - 多選下拉選單選擇員工（可一次查詢多位）
   - 顯示員工完整資料卡片：
     * 基本資料（工號、姓名、部門、職位、到職日、狀態）
     * 績效歷程表格（年度、考績、分數，並計算平均分數）
     * 訓練紀錄表格（課程、類別、時數，並計算總完訓時數）
     * 離職紀錄（如果有）

3. 資料匯出功能：
   - 單一員工匯出：產生包含所有資料的 Excel（多個分頁）
   - 批次匯出：
     * 加入批次匯出清單
     * 下載總表：所有員工在一個分頁（摘要格式）
     * 下載詳細分頁：每位員工一個分頁（完整資料）

4. 資料庫管理：
   - 查看資料庫內容
   - 清空資料庫
   - 匯出資料庫內容為 Excel

**技術需求：**
- 使用 Python + Streamlit 開發網頁介面
- 使用 SQLite 資料庫（獨立的 m4_employees.db、m4_performance.db、m4_training.db）
- 使用 Pandas 處理資料和匯出
- 使用 session_state 管理批次匯出清單

**使用者介面：**
- 使用 tabs 分頁：查詢員工、資料匯入、資料庫管理
- 員工卡片使用 expander 或 container 顯示
- 批次匯出清單使用 sidebar 或獨立區域
- 資料表格支援全螢幕查看

請提供完整的程式碼實作，包含資料庫架構設計。"""

        st.code(ai_prompt_m4, language='text')
        st.caption('💡 複製此提示詞給 AI（如 Claude、ChatGPT），即可快速開發類似功能。')

    # ========== 功能 4: 資格檢核器 ==========
    with tab4:
        st.header('✅ 資格檢核器')
        st.markdown('### 功能說明')
        st.write('自動檢核離職員工的回任資格，基於離職類型、歷史績效、訓練記錄等多項指標進行綜合判斷。')

        st.markdown('### 使用情境')
        st.write("""
        - 離職員工申請回任，需要快速評估是否符合資格
        - 需要檢查員工是否在黑名單中
        - 需要參考員工的離職原因、歷史績效、訓練記錄
        - 批次檢核多位申請人的回任資格
        """)

        st.markdown('### 檢核項目')
        st.write("""
        系統會自動檢核以下項目：

        1. **員工資料查詢** - 確認員工是否存在於系統中
        2. **離職記錄檢查** - 分析離職類型：
           - ✅ PASS：自願離職、退休
           - ⚠️ WARNING：資遣、開除（需主管審查）
        3. **歷史績效查詢** - 檢查績效記錄：
           - ✅ PASS：平均分數 ≥ 70 且無低績效（C/D/E）
           - ⚠️ WARNING：有低績效記錄（需主管審查）
        4. **訓練記錄查詢** - 提供參考資訊（總完訓時數）

        綜合判斷：
        - **✅ 建議核准**：所有檢核項目通過
        - **⚠️ 需要審查**：有警示項目，建議主管評估
        - **❌ 不建議核准**：有嚴重問題（如黑名單）
        """)

        st.markdown('### 操作步驟（SOP）')
        st.markdown("""
        **步驟 1：匯入資料**

        1. 點選「資料匯入」分頁
        2. 依序上傳以下檔案：
           - **員工資料**：工號、姓名（必填）
           - **離職記錄**：工號、離職日期、離職類型、離職原因（必填）
           - **績效資料**：工號、年度、考績、分數（必填）
           - **訓練記錄**：工號、課程名稱、時數、完成日期（必填）
        3. 系統會自動驗證必填欄位
        4. 顯示欄位對應關係
        5. 點擊「匯入」並查看匯入統計

        **步驟 2：執行檢核**

        單一檢核：
        1. 點選「資格檢核」分頁
        2. 選擇「單一檢核」模式
        3. 從下拉選單選擇員工姓名
        4. 點擊「🔍 執行檢核」
        5. 查看檢核報告：
           - 整體狀態（核准/需審查/拒絕）
           - 各項檢核結果
           - 系統建議
           - 審查要點（如有WARNING）

        批次檢核：
        1. 選擇「批次檢核」模式
        2. 多選要檢核的員工
        3. 點擊「🔍 批次執行檢核」
        4. 查看批次結果摘要（總數、通過數、警示數）

        **步驟 3：匯出檢核報告**

        單一匯出：
        - 在檢核結果下方點擊「📄 匯出檢核報告」
        - 產生包含「檢核摘要」和「檢核明細」的 Excel 檔案

        批次匯出：
        - 在批次結果頁面點擊「📥 批次匯出報告」
        - 產生所有檢核結果的彙整報告

        **步驟 4：資料庫管理**

        1. 點選「資料庫管理」分頁
        2. 可查看、匯出、刪除各類資料
        3. 支援單筆刪除或整個資料庫清空
        """)

        st.markdown('### 📥 測試檔案下載')
        st.write('請下載以下測試檔案進行練習：')

        test_files_m5 = [
            ('test_m5_employee_master.xlsx', '員工資料'),
            ('test_m5_separation.xlsx', '離職記錄'),
            ('test_m5_performance.xlsx', '績效資料'),
            ('test_m5_training.xlsx', '訓練記錄')
        ]

        for filename, desc in test_files_m5:
            file_path = f'tests/test_data/{filename}'
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                st.download_button(
                    label=f'📄 {filename} ({desc})',
                    data=file_data,
                    file_name=filename,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key=f'download_m5_{filename}'
                )

        st.caption('💡 提示：測試檔案包含多種檢核情境（通過、警示、拒絕），可用於測試完整的檢核流程。')

        st.markdown('### 🤖 AI 開發提示詞')
        st.write('如果您想要請 AI 開發類似的資格檢核系統，可以複製以下提示詞：')

        ai_prompt_m5 = """請幫我開發一個離職員工回任資格檢核系統，需求如下：

**功能需求：**
1. 資料匯入功能（支援智慧欄位辨識）：
   - 員工資料：工號、姓名
   - 離職記錄：工號、離職日期、離職類型、離職原因
   - 績效資料：工號、年度、考績等級、分數
   - 訓練記錄：工號、課程名稱、時數、完成日期

2. 資格檢核功能：
   - 單一檢核：選擇一位員工進行檢核
   - 批次檢核：同時檢核多位員工
   - 檢核項目：
     * 員工資料查詢（確認員工是否存在）
     * 離職記錄檢查（分析離職類型：自願/資遣/開除）
       - PASS：自願離職、退休
       - WARNING：資遣、開除（需審查）
     * 歷史績效查詢（檢查分數和低績效記錄）
       - PASS：平均分數 ≥ 70 且無 C/D/E 績效
       - WARNING：有低績效記錄
     * 訓練記錄查詢（提供總完訓時數參考）

3. 綜合判斷邏輯：
   - ✅ 建議核准：所有檢核 PASS
   - ⚠️ 需要審查：有 WARNING 項目
   - ❌ 不建議核准：有嚴重問題

4. 檢核報告匯出：
   - 單一報告：包含「檢核摘要」和「檢核明細」分頁
   - 批次報告：彙整所有檢核結果

5. 資料庫管理：
   - 查看各類資料
   - 單筆刪除或整庫清空
   - 匯出資料

**技術需求：**
- 使用 Python + Streamlit 開發網頁介面
- 使用 SQLite 資料庫（m5_qualification.db，包含 4 個資料表）
- 使用 Pandas 處理資料和匯出
- 檢核邏輯使用 Python 規則（不使用 AI）

**使用者介面：**
- 使用 tabs 分頁：資格檢核、資料匯入、資料庫管理
- 檢核模式切換：單一檢核 / 批次檢核
- 檢核報告使用不同顏色標示（✅ PASS / ⚠️ WARNING / ❌ FAIL）
- 批次結果顯示摘要統計（總數、通過數、警示數）

請提供完整的程式碼實作，包含檢核邏輯和資料庫設計。"""

        st.code(ai_prompt_m5, language='text')
        st.caption('💡 複製此提示詞給 AI（如 Claude、ChatGPT），即可快速開發類似功能。')

    # ========== 功能 5: 到期提醒 ==========
    with tab5:
        st.header('🔔 到期提醒系統')
        st.markdown('### 功能說明')
        st.write('管理證照、合約、試用期等各類到期事項，自動提醒即將到期和已逾期的項目。')

        st.markdown('### 使用情境')
        st.write("""
        - 員工證照即將到期，需要提前提醒換證
        - 試用期即將屆滿，需要安排考核
        - 合約到期前需要提醒續約
        - 定期檢查所有到期事項的狀態
        """)

        st.markdown('### 提醒類型')
        st.write("""
        系統支援以下提醒類型：
        - 🎓 **證照到期**：各類專業證照、執照
        - 📝 **試用期屆滿**：新進員工試用期結束
        - 📄 **合約到期**：勞動合約、外包合約
        - 📋 **其他**：自訂提醒事項
        """)

        st.markdown('### 操作步驟（SOP）')
        st.markdown("""
        **步驟 1：新增提醒**

        手動新增：
        1. 點選「新增提醒」分頁
        2. 輸入員工工號和姓名
        3. 選擇提醒類型（證照到期、試用期屆滿、合約到期、其他）
        4. 選擇到期日期
        5. 輸入備註（選填，例如：護理師執照、三個月試用期）
        6. 點擊「新增提醒」

        批次匯入：
        1. 準備包含以下欄位的 Excel/CSV 檔案：
           - 工號（emp_id）
           - 姓名（emp_name）
           - 提醒類型（reminder_type）
           - 到期日期（due_date）
           - 備註（notes，選填）
        2. 點選「批次匯入」分頁
        3. 上傳檔案
        4. 確認欄位對應正確
        5. 點擊「匯入提醒」
        6. 查看匯入統計

        **步驟 2：查看提醒**

        1. 點選「查看提醒」分頁
        2. 使用篩選器：
           - **狀態篩選**：待處理 / 已完成 / 全部
           - **類型篩選**：證照到期 / 試用期屆滿 / 合約到期 / 其他 / 全部
        3. 查看提醒列表（按到期日排序）
        4. 系統會自動標示：
           - 🔴 **已逾期**：到期日已過
           - 🟡 **即將到期**：7 天內到期
           - 🟢 **正常**：超過 7 天

        **步驟 3：管理提醒**

        標記為已完成：
        1. 在提醒列表中找到該項目
        2. 點擊「✅ 標記完成」
        3. 系統記錄完成日期

        刪除提醒：
        1. 點擊「🗑️ 刪除」
        2. 確認刪除

        **步驟 4：匯出資料**

        1. 在「查看提醒」分頁
        2. 套用所需的篩選條件
        3. 點擊「📥 匯出資料」
        4. 下載 Excel 檔案（包含所有篩選後的提醒）
        """)

        st.markdown('### 📊 到期狀態說明')
        st.write("""
        - **🔴 已逾期**：到期日 < 今天（需立即處理）
        - **🟡 即將到期**：0 ≤ (到期日 - 今天) ≤ 7 天（需盡快處理）
        - **🟢 正常**：到期日 - 今天 > 7 天（持續追蹤）
        """)

        st.markdown('### 📥 測試檔案下載')
        st.write('請下載以下測試檔案進行練習：')

        test_file_m6 = 'test_m6_new_hires.xlsx'
        file_path = f'tests/test_data/{test_file_m6}'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            st.download_button(
                label=f'📄 {test_file_m6}',
                data=file_data,
                file_name=test_file_m6,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        st.caption('💡 提示：此檔案包含新進員工的試用期提醒資料，可用於測試批次匯入和提醒管理功能。')

        st.markdown('### 🤖 AI 開發提示詞')
        st.write('如果您想要請 AI 開發類似的到期提醒系統，可以複製以下提示詞：')

        ai_prompt_m6 = """請幫我開發一個到期事項提醒管理系統，需求如下：

**功能需求：**
1. 新增提醒功能：
   - 手動新增：輸入工號、姓名、提醒類型、到期日期、備註
   - 批次匯入：上傳包含多筆提醒的 Excel/CSV 檔案
   - 提醒類型：證照到期、試用期屆滿、合約到期、其他

2. 查看提醒功能：
   - 篩選器：
     * 狀態篩選：待處理 / 已完成 / 全部
     * 類型篩選：證照到期 / 試用期屆滿 / 合約到期 / 其他 / 全部
   - 提醒列表按到期日排序
   - 自動標示到期狀態：
     * 🔴 已逾期：到期日 < 今天
     * 🟡 即將到期：0-7 天內到期
     * 🟢 正常：> 7 天

3. 管理提醒功能：
   - 標記為已完成（記錄完成日期）
   - 刪除提醒
   - 編輯提醒（選用）

4. 匯出功能：
   - 匯出篩選後的提醒清單為 Excel

5. 統計儀表板（選用）：
   - 顯示待處理數量
   - 已逾期數量
   - 即將到期數量
   - 本月到期數量

**技術需求：**
- 使用 Python + Streamlit 開發網頁介面
- 使用 SQLite 資料庫（reminders.db）
- 使用 Pandas 處理資料和匯出
- 自動計算到期狀態（使用 datetime 比較日期）

**資料庫結構：**
- 欄位：id、emp_id、emp_name、reminder_type、due_date、notes、status、completed_date、created_at

**使用者介面：**
- 使用 tabs 分頁：查看提醒、新增提醒、批次匯入
- 提醒列表使用表格顯示，並以顏色區分到期狀態
- 每筆提醒提供「標記完成」和「刪除」按鈕
- 篩選器使用 selectbox 或 radio

**到期狀態計算邏輯：**
```python
days_until_due = (due_date - today).days
if days_until_due < 0:
    status = "已逾期"
    color = "🔴"
elif days_until_due <= 7:
    status = "即將到期"
    color = "🟡"
else:
    status = "正常"
    color = "🟢"
```

請提供完整的程式碼實作。"""

        st.code(ai_prompt_m6, language='text')
        st.caption('💡 複製此提示詞給 AI（如 Claude、ChatGPT），即可快速開發類似功能。')

    # 頁尾資訊
    st.divider()
    st.markdown("""
    ### 💡 使用技巧

    1. **善用範本功能**：報表合併器和資料清洗器都支援儲存範本，處理重複性工作時可大幅節省時間
    2. **全螢幕查看**：所有資料預覽都支援點擊右上角按鈕全螢幕查看完整資料
    3. **批次操作**：員工查詢、資格檢核都支援批次處理，一次處理多筆資料更有效率
    4. **資料獨立**：各模組使用獨立資料庫，互不干擾

    ### ❓ 常見問題

    **Q: 上傳的檔案欄位名稱和系統不一樣怎麼辦？**
    A: 系統支援智慧欄位辨識，會自動匹配相似欄位名稱（如：工號、emp_id、員工編號都會被識別為同一欄位）

    **Q: 範本可以跨電腦使用嗎？**
    A: 範本儲存在本地資料庫中，如需跨電腦使用，請複製整個資料庫檔案

    **Q: 資料會上傳到雲端嗎？**
    A: 所有資料都儲存在本地，不會上傳到任何雲端服務，確保資料安全

    **Q: 如何清空所有資料？**
    A: 每個模組的「資料庫管理」分頁都有清空功能，可選擇性清空特定資料庫
    """)

elif st.session_state.current_page == '報表合併器':
    from modules import m1_report_merger
    m1_report_merger.render()

elif st.session_state.current_page == '資料清洗器':
    from modules import m2_data_cleaner
    m2_data_cleaner.render()

elif st.session_state.current_page == '員工查詢':
    from modules import m4_employee_dashboard
    m4_employee_dashboard.render()

elif st.session_state.current_page == '資格檢核器':
    from modules import m5_qualification_check
    m5_qualification_check.render()

elif st.session_state.current_page == '到期提醒':
    from modules import m6_reminder_system
    m6_reminder_system.render()
