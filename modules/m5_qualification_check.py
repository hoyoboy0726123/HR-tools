"""
模組5: 資格檢核器 (Qualification Checker)
離職回任資格檢核系統

設計原則：
1. 使用明確的規則進行自動化檢核
2. 黑名單自動拒絕、全通過自動核准
3. 有警示項目時標示為「需主管人工審查」
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from core.db_manager_multiuser import DBManagerMultiUser


class QualificationChecker:
    """資格檢核核心邏輯"""

    def __init__(self, user_id=None):
        # 使用 M5 專用的單一資料庫 - 包含 4 個表 (employees, performance, training, separation)
        # 支援多用戶資料隔離
        self.user_id = user_id
        self.db = DBManagerMultiUser('m5_qualification', user_id=user_id)
        # 為了向後兼容和程式碼可讀性，保留這些別名
        self.db_employees = self.db
        self.db_performance = self.db
        self.db_training = self.db
        self.db_separation = self.db

    @staticmethod
    def find_column(df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """
        智慧查找欄位名稱（不區分大小寫、支援多種變體）

        Args:
            df: DataFrame
            possible_names: 可能的欄位名稱列表

        Returns:
            找到的欄位名稱，若找不到則返回 None
        """
        df_columns_lower = {col.lower().strip(): col for col in df.columns}

        for name in possible_names:
            name_lower = name.lower().strip()
            if name_lower in df_columns_lower:
                return df_columns_lower[name_lower]

        return None

    @staticmethod
    def validate_required_columns(df: pd.DataFrame, column_mapping: Dict[str, List[str]]) -> tuple[bool, List[str]]:
        """
        驗證必填欄位是否存在

        Args:
            df: DataFrame
            column_mapping: {顯示名稱: [可能的欄位名稱列表]}

        Returns:
            (是否全部存在, 缺少的欄位列表)
        """
        missing = []
        for display_name, possible_names in column_mapping.items():
            if QualificationChecker.find_column(df, possible_names) is None:
                missing.append(f"{display_name} ({'/'.join(possible_names[:2])})")

        return len(missing) == 0, missing

    def check(self, name: str, id_number: str = None) -> Dict[str, Any]:
        """
        執行資格檢核

        Args:
            name: 姓名
            id_number: 身分證字號（選填，若不提供則只用姓名查詢）

        Returns:
            檢核結果字典
        """
        result = {
            'name': name,
            'id_number': id_number if id_number else 'N/A',
            'checks': [],
            'overall_status': 'PENDING',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Step 1: 查詢員工基本資料
        employee = self._find_employee_by_name(name) if not id_number else self._find_employee(id_number)

        if not employee:
            result['overall_status'] = 'NOT_FOUND'
            result['checks'].append({
                'item': '員工資料查詢',
                'status': 'FAIL',
                'detail': '查無此員工記錄，可能未曾在本公司任職'
            })
            return result

        result['emp_id'] = employee['emp_id']
        result['checks'].append({
            'item': '員工資料查詢',
            'status': 'PASS',
            'detail': f"工號: {employee['emp_id']}, 部門: {employee.get('department', 'N/A')}"
        })

        # Step 2: 黑名單比對
        blacklist_check = self._check_blacklist(employee['emp_id'])
        result['checks'].append(blacklist_check)

        if blacklist_check['status'] == 'FAIL':
            result['overall_status'] = 'REJECTED'
            result['rejection_reason'] = '列於黑名單中，不得回任'
            return result

        # Step 3: 離職紀錄查詢
        separation_check = self._check_separation(employee['emp_id'])
        result['checks'].append(separation_check)

        # Step 4: 歷史績效查詢
        performance_check = self._check_performance(employee['emp_id'])
        result['checks'].append(performance_check)

        # Step 5: 訓練紀錄查詢（額外參考）
        training_check = self._check_training(employee['emp_id'])
        result['checks'].append(training_check)

        # Step 6: 綜合判斷
        warnings = [c for c in result['checks'] if c['status'] == 'WARNING']

        if not warnings:
            # 全部 PASS，自動核准
            result['overall_status'] = 'APPROVED'
            result['recommendation'] = '✅ 所有檢核項目通過，建議核准回任'
        else:
            # 有警示項目，需要人工審查
            result['overall_status'] = 'REVIEW_REQUIRED'
            result['recommendation'] = f"⚠️ 有 {len(warnings)} 個警示項目，需要主管人工審查"
            result['warnings'] = warnings
            result['review_notes'] = self._generate_review_notes(warnings)

        return result

    def _generate_review_notes(self, warnings: List[Dict]) -> str:
        """生成審查建議"""
        notes = ["建議主管重點評估以下項目：\n"]

        for i, warning in enumerate(warnings, 1):
            notes.append(f"{i}. {warning['item']}: {warning['detail']}")

        return "\n".join(notes)

    def _find_employee(self, id_number: str) -> Optional[Dict]:
        """根據身分證字號查詢員工"""
        import hashlib

        # Hash the id_number for comparison
        id_number_hash = hashlib.sha256(id_number.encode()).hexdigest()

        conn = self.db_employees._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id_number_hash = ?", (id_number_hash,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def _find_employee_by_name(self, name: str) -> Optional[Dict]:
        """根據姓名查詢員工"""
        conn = self.db_employees._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def _check_blacklist(self, emp_id: str) -> Dict[str, Any]:
        """黑名單檢查"""
        sep_record = self.db_separation.get_separation_record(emp_id)

        if sep_record and sep_record.get('blacklist'):
            return {
                'item': '黑名單比對',
                'status': 'FAIL',
                'detail': f"列於黑名單中（離職日期: {sep_record.get('separation_date', 'N/A')}）",
                'data': sep_record
            }
        else:
            return {
                'item': '黑名單比對',
                'status': 'PASS',
                'detail': '未在黑名單'
            }

    def _check_separation(self, emp_id: str) -> Dict[str, Any]:
        """離職紀錄檢查"""
        sep_record = self.db_separation.get_separation_record(emp_id)

        if not sep_record:
            return {
                'item': '離職紀錄',
                'status': 'INFO',
                'detail': '無離職紀錄（在職或從未離職）'
            }

        # 分析離職類型
        sep_type = sep_record.get('separation_type', '')
        reason = sep_record.get('reason', '未填寫')
        sep_date = sep_record.get('separation_date', 'N/A')

        if sep_type in ['資遣', '開除']:
            return {
                'item': '離職紀錄',
                'status': 'WARNING',
                'detail': f"非自願離職（{sep_type}）於 {sep_date}，原因: {reason}",
                'data': sep_record
            }
        else:
            return {
                'item': '離職紀錄',
                'status': 'PASS',
                'detail': f"自願離職於 {sep_date}，原因: {reason}",
                'data': sep_record
            }

    def _check_performance(self, emp_id: str) -> Dict[str, Any]:
        """歷史績效檢查"""
        perf_records = self.db_performance.get_performance_history(emp_id)

        if not perf_records:
            return {
                'item': '歷史績效紀錄',
                'status': 'INFO',
                'detail': '無績效紀錄'
            }

        # 分析績效
        df = pd.DataFrame(perf_records)
        low_perf = df[df['rating'].isin(['C', 'D', 'E'])]

        if len(low_perf) > 0:
            avg_score = df['score'].mean() if 'score' in df.columns else 0
            return {
                'item': '歷史績效紀錄',
                'status': 'WARNING',
                'detail': f"曾有 {len(low_perf)} 次低績效紀錄（C/D/E），平均分數: {avg_score:.1f}",
                'data': perf_records
            }
        else:
            avg_score = df['score'].mean() if 'score' in df.columns else 0
            return {
                'item': '歷史績效紀錄',
                'status': 'PASS',
                'detail': f"績效良好，平均分數: {avg_score:.1f}，共 {len(perf_records)} 筆記錄",
                'data': perf_records
            }

    def _check_training(self, emp_id: str) -> Dict[str, Any]:
        """訓練紀錄檢查"""
        training_records = self.db_training.get_training_history(emp_id)

        if not training_records:
            return {
                'item': '訓練紀錄',
                'status': 'INFO',
                'detail': '無訓練紀錄'
            }

        df = pd.DataFrame(training_records)
        total_hours = df['hours'].sum() if 'hours' in df.columns else 0

        return {
            'item': '訓練紀錄',
            'status': 'INFO',
            'detail': f"總完訓時數: {total_hours} 小時，共 {len(training_records)} 個課程",
            'data': training_records
        }


def render():
    """渲染資格檢核器介面"""
    st.header("✅ 資格檢核器")
    st.caption("離職回任資格檢核系統 - 規則式自動化檢核")

    # 取得當前登入用戶的 user_id
    user_id = st.session_state.user_info['user_id']

    # 初始化 checker（支援多用戶）
    if 'checker' not in st.session_state:
        st.session_state.checker = QualificationChecker(user_id=user_id)

    # 初始化檢核結果儲存（確保一定會初始化，避免 AttributeError）
    if 'check_results' not in st.session_state:
        st.session_state.check_results = {}

    if 'show_batch_export' not in st.session_state:
        st.session_state.show_batch_export = False

    # Tab 分頁
    tab1, tab2, tab3 = st.tabs(["📋 資格檢核", "📥 資料匯入", "🗄️ 資料庫管理"])

    # Tab 1: 資格檢核
    with tab1:
        st.subheader("員工資格檢核")

        # 取得所有已匯入的員工清單
        db_employees = st.session_state.checker.db_employees
        conn = db_employees._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT emp_id, name, id_number_hash, department FROM employees ORDER BY emp_id")
        all_employees = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not all_employees:
            st.warning("⚠️ 資料庫中尚無員工資料，請先到「資料匯入」頁面匯入測試資料")
        else:
            st.info(f"📊 資料庫中共有 {len(all_employees)} 位員工記錄")

            # 選擇檢核模式
            check_mode = st.radio(
                "檢核模式",
                options=["單一檢核", "批次檢核"],
                horizontal=True
            )

            if check_mode == "單一檢核":
                # 單一員工檢核
                employee_options = {f"{emp['emp_id']} - {emp['name']} ({emp.get('department', 'N/A')})": emp for emp in all_employees}

                selected_option = st.selectbox(
                    "選擇要檢核的員工",
                    options=[""] + list(employee_options.keys()),
                    format_func=lambda x: "請選擇員工..." if x == "" else x
                )

                if selected_option and selected_option != "":
                    selected_emp = employee_options[selected_option]

                    st.write("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**工號**: {selected_emp['emp_id']}")
                        st.write(f"**姓名**: {selected_emp['name']}")
                    with col2:
                        st.write(f"**部門**: {selected_emp.get('department', 'N/A')}")

                    if st.button("🔍 執行檢核", type="primary"):
                        with st.spinner("檢核中..."):
                            # 使用姓名直接檢核（不需要身分證字號）
                            result = st.session_state.checker.check(selected_emp['name'], None)
                            st.session_state.last_check_result = result
                            # 同時儲存到批次結果中
                            st.session_state.check_results[selected_emp['emp_id']] = result

            else:
                # 批次檢核
                employee_options = [f"{emp['emp_id']} - {emp['name']} ({emp.get('department', 'N/A')})" for emp in all_employees]

                selected_options = st.multiselect(
                    "選擇要檢核的員工（可多選）",
                    options=employee_options,
                    help="可以使用 Ctrl/Cmd 多選，或在下拉選單中逐一勾選"
                )

                if selected_options:
                    st.info(f"✅ 已選擇 {len(selected_options)} 位員工")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔍 批次執行檢核", type="primary"):
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            for idx, option in enumerate(selected_options):
                                emp_id = option.split(" - ")[0]
                                emp_name = option.split(" - ")[1].split(" (")[0]

                                status_text.text(f"檢核中... {emp_name} ({idx + 1}/{len(selected_options)})")

                                # 執行檢核（不需要身分證字號）
                                result = st.session_state.checker.check(emp_name, None)
                                st.session_state.check_results[emp_id] = result

                                progress_bar.progress((idx + 1) / len(selected_options))

                            status_text.text("✅ 批次檢核完成！")
                            st.success(f"已完成 {len(selected_options)} 位員工的資格檢核")
                            st.rerun()

                    with col2:
                        if st.session_state.check_results:
                            if st.button("🗑️ 清除檢核結果"):
                                st.session_state.check_results = {}
                                st.rerun()

                    with col3:
                        if st.session_state.check_results:
                            if st.button("📥 批次匯出報告"):
                                st.session_state.show_batch_export = True

        # 顯示批次檢核結果摘要
        if st.session_state.check_results:
            st.divider()
            st.subheader("📊 批次檢核結果摘要")

            # 統計各狀態數量
            status_counts = {'APPROVED': 0, 'REVIEW_REQUIRED': 0, 'REJECTED': 0, 'NOT_FOUND': 0}
            for result in st.session_state.check_results.values():
                status = result.get('overall_status', 'NOT_FOUND')
                status_counts[status] = status_counts.get(status, 0) + 1

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ 建議核准", status_counts['APPROVED'])
            with col2:
                st.metric("⚠️ 需要審查", status_counts['REVIEW_REQUIRED'])
            with col3:
                st.metric("❌ 不建議核准", status_counts['REJECTED'])
            with col4:
                st.metric("📊 總計", len(st.session_state.check_results))

            # 顯示檢核結果表格
            with st.expander("📋 查看詳細結果", expanded=True):
                results_list = []
                for emp_id, result in st.session_state.check_results.items():
                    status_text_map = {
                        'APPROVED': '✅ 建議核准',
                        'REJECTED': '❌ 不建議核准',
                        'REVIEW_REQUIRED': '⚠️ 需要審查',
                        'NOT_FOUND': '❌ 查無資料'
                    }
                    results_list.append({
                        '工號': emp_id,
                        '姓名': result.get('name', 'N/A'),
                        '檢核狀態': status_text_map.get(result.get('overall_status'), '未知'),
                        '系統建議': result.get('recommendation', 'N/A'),
                        '檢核時間': result.get('timestamp', 'N/A')
                    })

                results_df = pd.DataFrame(results_list)
                st.dataframe(results_df, use_container_width=True)

        # 批次匯出功能
        if 'show_batch_export' in st.session_state and st.session_state.show_batch_export:
            st.divider()
            st.subheader("📥 批次匯出檢核報告")

            from io import BytesIO

            # 建立批次報告
            all_summaries = []
            all_details = []

            status_text_map = {
                'APPROVED': '✅ 建議核准',
                'REJECTED': '❌ 不建議核准',
                'REVIEW_REQUIRED': '⚠️ 需要審查',
                'NOT_FOUND': '❌ 查無資料'
            }

            for emp_id, result in st.session_state.check_results.items():
                # 摘要資料
                all_summaries.append({
                    '工號': emp_id,
                    '姓名': result.get('name', 'N/A'),
                    '檢核時間': result.get('timestamp', 'N/A'),
                    '檢核狀態': status_text_map.get(result.get('overall_status'), '未知'),
                    '系統建議': result.get('recommendation', 'N/A'),
                    '審查要點': result.get('review_notes', 'N/A')
                })

                # 明細資料
                for check in result.get('checks', []):
                    all_details.append({
                        '工號': emp_id,
                        '姓名': result.get('name', 'N/A'),
                        '檢核項目': check.get('item', 'N/A'),
                        '狀態': check.get('status', 'N/A'),
                        '詳細說明': check.get('detail', 'N/A')
                    })

            summary_df = pd.DataFrame(all_summaries)
            details_df = pd.DataFrame(all_details)

            # 生成 Excel 檔案
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                summary_df.to_excel(writer, index=False, sheet_name='檢核摘要')
                details_df.to_excel(writer, index=False, sheet_name='檢核明細')

            output.seek(0)

            st.download_button(
                label=f'💾 下載批次檢核報告 ({len(st.session_state.check_results)} 位員工)',
                data=output,
                file_name=f"batch_qualification_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            if st.button("關閉匯出"):
                st.session_state.show_batch_export = False
                st.rerun()

        # 顯示單一檢核結果（在單一檢核模式下）
        if 'last_check_result' in st.session_state and check_mode == "單一檢核":
            result = st.session_state.last_check_result

            st.divider()
            st.subheader("📄 檢核報告")

            # 顯示整體狀態
            status_color = {
                'APPROVED': 'success',
                'REJECTED': 'error',
                'REVIEW_REQUIRED': 'warning',
                'NOT_FOUND': 'error',
                'PENDING': 'info'
            }

            status_text = {
                'APPROVED': '✅ 建議核准',
                'REJECTED': '❌ 不建議核准',
                'REVIEW_REQUIRED': '⚠️ 需要審查',
                'NOT_FOUND': '❌ 查無資料',
                'PENDING': '⏳ 檢核中'
            }

            status = result['overall_status']
            getattr(st, status_color[status])(f"**檢核狀態**: {status_text[status]}")

            # 顯示檢核項目
            st.write("**檢核項目明細**:")
            for i, check in enumerate(result['checks']):
                icon = {
                    'PASS': '✅',
                    'WARNING': '⚠️',
                    'FAIL': '❌',
                    'INFO': 'ℹ️'
                }
                st.write(f"{icon.get(check['status'], '•')} **{check['item']}**: {check['detail']}")

            # 顯示建議
            if 'recommendation' in result:
                st.info(f"**系統建議**: {result['recommendation']}")

            # 顯示審查要點（僅在 REVIEW_REQUIRED 時顯示）
            if status == 'REVIEW_REQUIRED' and 'review_notes' in result:
                st.divider()
                st.warning("**⚠️ 需要主管人工審查**")
                st.write(result['review_notes'])

            # 匯出單一報告按鈕
            st.divider()
            if st.button("📥 匯出此檢核報告"):
                # 建立報告 DataFrame
                report_data = {
                    '檢核時間': [result['timestamp']],
                    '姓名': [result['name']],
                    '工號': [result.get('emp_id', 'N/A')],
                    '檢核狀態': [status_text[status]],
                    '系統建議': [result.get('recommendation', 'N/A')],
                    '審查要點': [result.get('review_notes', 'N/A')]
                }

                report_df = pd.DataFrame(report_data)

                # 檢核明細
                checks_df = pd.DataFrame([
                    {
                        '檢核項目': check['item'],
                        '狀態': check['status'],
                        '詳細說明': check['detail']
                    }
                    for check in result['checks']
                ])

                # 使用 ExcelWriter 建立多分頁報告
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    report_df.to_excel(writer, index=False, sheet_name='檢核摘要')
                    checks_df.to_excel(writer, index=False, sheet_name='檢核明細')

                output.seek(0)

                st.download_button(
                    label='💾 下載檢核報告',
                    data=output,
                    file_name=f"qualification_check_{result.get('emp_id', 'unknown')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

    # Tab 2: 資料匯入
    with tab2:
        st.subheader("📥 資料匯入")
        st.caption("匯入測試資料以進行資格檢核")

        import_tab1, import_tab2, import_tab3, import_tab4 = st.tabs([
            "員工資料", "離職記錄", "績效資料", "訓練記錄"
        ])

        # 員工資料匯入
        with import_tab1:
            st.write("**上傳員工主檔**")

            with st.expander("📋 必填欄位說明", expanded=False):
                st.markdown("""
                **必填欄位**（系統會自動識別以下任一名稱）：
                - **工號**：`emp_id` / `工號` / `員工編號` / `employee_id`
                - **姓名**：`name` / `姓名` / `員工姓名` / `employee_name`

                **選填欄位**：
                - **身分證**：`id_number` / `身分證字號` / `身份證` / `id`
                - **部門**：`department` / `部門` / `dept`
                - **到職日**：`hire_date` / `到職日` / `入職日期` / `arrival_date`
                - **狀態**：`status` / `狀態`（預設為「離職」）

                ✅ 系統支援**不區分大小寫**，`EMP_ID` 和 `emp_id` 都可以識別
                """)

            emp_file = st.file_uploader("選擇員工資料檔案", type=['xlsx', 'csv'], key='emp_file')

            if emp_file:
                try:
                    emp_df = pd.read_excel(emp_file) if emp_file.name.endswith('xlsx') else pd.read_csv(emp_file)

                    st.write(f"**檔案預覽** ({len(emp_df)} 筆資料):")
                    st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                    st.dataframe(emp_df)

                    # 驗證必填欄位
                    required_cols = {
                        '工號': ['emp_id', '工號', '員工編號', 'employee_id', 'id'],
                        '姓名': ['name', '姓名', '員工姓名', 'employee_name']
                    }

                    is_valid, missing = st.session_state.checker.validate_required_columns(emp_df, required_cols)

                    if not is_valid:
                        st.error(f"❌ 缺少必填欄位：{', '.join(missing)}")
                        st.info("請確認檔案包含必填欄位，或參考上方「必填欄位說明」")
                    else:
                        st.success("✅ 欄位驗證通過")

                        # 顯示識別到的欄位
                        col_map = {}
                        all_possible_cols = {
                            '工號': ['emp_id', '工號', '員工編號', 'employee_id', 'id'],
                            '姓名': ['name', '姓名', '員工姓名', 'employee_name'],
                            '身分證': ['id_number', '身分證字號', '身份證', 'id_card'],
                            '部門': ['department', '部門', 'dept'],
                            '到職日': ['hire_date', '到職日', '入職日期', 'arrival_date'],
                            '狀態': ['status', '狀態']
                        }

                        for field, possible_names in all_possible_cols.items():
                            found = st.session_state.checker.find_column(emp_df, possible_names)
                            if found:
                                col_map[field] = found

                        with st.expander("🔍 已識別的欄位對應", expanded=False):
                            for field, col_name in col_map.items():
                                st.text(f"  {field} → {col_name}")

                        if st.button("匯入員工資料", key='import_emp', type='primary'):
                            success_count = 0
                            error_count = 0
                            errors = []

                            for idx, row in emp_df.iterrows():
                                try:
                                    result = st.session_state.checker.db_employees.add_employee(
                                        emp_id=row[col_map['工號']] if '工號' in col_map else None,
                                        name=row[col_map['姓名']] if '姓名' in col_map else None,
                                        id_number=row[col_map['身分證']] if '身分證' in col_map else None,
                                        department=row[col_map['部門']] if '部門' in col_map else None,
                                        hire_date=row[col_map['到職日']] if '到職日' in col_map else None,
                                        status=row[col_map['狀態']] if '狀態' in col_map else '離職'
                                    )
                                    if result:
                                        success_count += 1
                                    else:
                                        error_count += 1
                                except Exception as e:
                                    error_count += 1
                                    errors.append(f"第 {idx+2} 列: {str(e)}")

                            if success_count > 0:
                                st.success(f"✅ 成功匯入 {success_count}/{len(emp_df)} 筆員工資料")
                            if error_count > 0:
                                st.warning(f"⚠️ {error_count} 筆資料匯入失敗")
                                if errors:
                                    with st.expander("查看錯誤詳情"):
                                        for err in errors[:10]:  # 只顯示前10個錯誤
                                            st.text(err)

                            if success_count > 0:
                                st.rerun()
                except Exception as e:
                    st.error(f"讀取檔案失敗: {str(e)}")

        # 離職記錄匯入
        with import_tab2:
            st.write("**上傳離職記錄**")

            with st.expander("📋 必填欄位說明", expanded=False):
                st.markdown("""
                **必填欄位**（系統會自動識別以下任一名稱）：
                - **工號**：`emp_id` / `工號` / `員工編號` / `employee_id`
                - **離職日期**：`separation_date` / `離職日期` / `離職時間`
                - **離職類型**：`separation_type` / `離職類型` / `離職性質`
                - **離職原因**：`reason` / `離職原因` / `原因`

                **選填欄位**：
                - **黑名單**：`blacklist` / `黑名單` (TRUE/FALSE 或 1/0)

                ✅ 系統支援**不區分大小寫**，`EMP_ID` 和 `emp_id` 都可以識別
                """)

            sep_file = st.file_uploader("選擇離職記錄檔案", type=['xlsx', 'csv'], key='sep_file')

            if sep_file:
                try:
                    sep_df = pd.read_excel(sep_file) if sep_file.name.endswith('xlsx') else pd.read_csv(sep_file)

                    # 必填欄位驗證
                    required_cols = {
                        '工號': ['emp_id', '工號', '員工編號', 'employee_id'],
                        '離職日期': ['separation_date', '離職日期', '離職時間'],
                        '離職類型': ['separation_type', '離職類型', '離職性質'],
                        '離職原因': ['reason', '離職原因', '原因']
                    }

                    is_valid, missing = st.session_state.checker.validate_required_columns(sep_df, required_cols)

                    if not is_valid:
                        st.error(f"❌ 缺少必填欄位：{', '.join(missing)}")
                        st.info("💡 請參考上方「必填欄位說明」，確認檔案包含所有必要欄位")
                    else:
                        # 顯示欄位對應
                        st.success("✅ 所有必填欄位都已找到")

                        col_mapping = {}
                        for display_name, possible_names in required_cols.items():
                            found_col = st.session_state.checker.find_column(sep_df, possible_names)
                            if found_col:
                                col_mapping[display_name] = found_col

                        with st.expander("📊 欄位對應關係", expanded=False):
                            for display_name, file_col in col_mapping.items():
                                st.write(f"- {display_name} ← `{file_col}`")

                        st.write("**檔案預覽**:")
                        st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                        st.dataframe(sep_df)

                        if st.button("匯入離職記錄", key='import_sep'):
                            success_count = 0
                            error_count = 0
                            errors = []

                            for idx, row in sep_df.iterrows():
                                try:
                                    emp_id_col = st.session_state.checker.find_column(sep_df, required_cols['工號'])
                                    date_col = st.session_state.checker.find_column(sep_df, required_cols['離職日期'])
                                    type_col = st.session_state.checker.find_column(sep_df, required_cols['離職類型'])
                                    reason_col = st.session_state.checker.find_column(sep_df, required_cols['離職原因'])
                                    blacklist_col = st.session_state.checker.find_column(sep_df, ['blacklist', '黑名單'])

                                    result = st.session_state.checker.db_separation.add_separation_record(
                                        emp_id=row[emp_id_col],
                                        separation_date=row[date_col],
                                        separation_type=row[type_col],
                                        reason=row[reason_col],
                                        blacklist=bool(row.get(blacklist_col, False)) if blacklist_col else False
                                    )
                                    if result:
                                        success_count += 1
                                    else:
                                        error_count += 1
                                except Exception as e:
                                    error_count += 1
                                    errors.append(f"第 {idx + 2} 列: {str(e)}")

                            # 顯示匯入結果
                            if success_count > 0:
                                st.success(f"✅ 成功匯入 {success_count} 筆離職記錄")
                            if error_count > 0:
                                st.warning(f"⚠️ {error_count} 筆記錄匯入失敗")
                                if errors:
                                    with st.expander("查看錯誤詳情"):
                                        for err in errors[:10]:  # 最多顯示 10 個錯誤
                                            st.text(err)

                            st.info(f"📊 匯入統計：總計 {len(sep_df)} 筆，成功 {success_count} 筆，失敗 {error_count} 筆")
                            st.rerun()

                except Exception as e:
                    st.error(f"讀取檔案失敗: {str(e)}")

        # 績效資料匯入
        with import_tab3:
            st.write("**上傳績效資料**")

            with st.expander("📋 必填欄位說明", expanded=False):
                st.markdown("""
                **必填欄位**（系統會自動識別以下任一名稱）：
                - **工號**：`emp_id` / `工號` / `員工編號` / `employee_id`
                - **年度**：`year` / `年度` / `考核年度`
                - **考績等級**：`rating` / `考績` / `等級` / `評等`
                - **分數**：`score` / `分數` / `績效分數`

                ✅ 系統支援**不區分大小寫**，`EMP_ID` 和 `emp_id` 都可以識別
                """)

            perf_file = st.file_uploader("選擇績效資料檔案", type=['xlsx', 'csv'], key='perf_file')

            if perf_file:
                try:
                    perf_df = pd.read_excel(perf_file) if perf_file.name.endswith('xlsx') else pd.read_csv(perf_file)

                    # 必填欄位驗證
                    required_cols = {
                        '工號': ['emp_id', '工號', '員工編號', 'employee_id'],
                        '年度': ['year', '年度', '考核年度'],
                        '考績等級': ['rating', '考績', '等級', '評等'],
                        '分數': ['score', '分數', '績效分數']
                    }

                    is_valid, missing = st.session_state.checker.validate_required_columns(perf_df, required_cols)

                    if not is_valid:
                        st.error(f"❌ 缺少必填欄位：{', '.join(missing)}")
                        st.info("💡 請參考上方「必填欄位說明」，確認檔案包含所有必要欄位")
                    else:
                        # 顯示欄位對應
                        st.success("✅ 所有必填欄位都已找到")

                        col_mapping = {}
                        for display_name, possible_names in required_cols.items():
                            found_col = st.session_state.checker.find_column(perf_df, possible_names)
                            if found_col:
                                col_mapping[display_name] = found_col

                        with st.expander("📊 欄位對應關係", expanded=False):
                            for display_name, file_col in col_mapping.items():
                                st.write(f"- {display_name} ← `{file_col}`")

                        st.write("**檔案預覽**:")
                        st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                        st.dataframe(perf_df)

                        if st.button("匯入績效資料", key='import_perf'):
                            success_count = 0
                            error_count = 0
                            errors = []

                            for idx, row in perf_df.iterrows():
                                try:
                                    emp_id_col = st.session_state.checker.find_column(perf_df, required_cols['工號'])
                                    year_col = st.session_state.checker.find_column(perf_df, required_cols['年度'])
                                    rating_col = st.session_state.checker.find_column(perf_df, required_cols['考績等級'])
                                    score_col = st.session_state.checker.find_column(perf_df, required_cols['分數'])

                                    result = st.session_state.checker.db_performance.add_performance_record(
                                        emp_id=row[emp_id_col],
                                        year=int(row[year_col]),
                                        rating=row[rating_col],
                                        score=float(row[score_col])
                                    )
                                    if result:
                                        success_count += 1
                                    else:
                                        error_count += 1
                                except Exception as e:
                                    error_count += 1
                                    errors.append(f"第 {idx + 2} 列: {str(e)}")

                            # 顯示匯入結果
                            if success_count > 0:
                                st.success(f"✅ 成功匯入 {success_count} 筆績效資料")
                            if error_count > 0:
                                st.warning(f"⚠️ {error_count} 筆記錄匯入失敗")
                                if errors:
                                    with st.expander("查看錯誤詳情"):
                                        for err in errors[:10]:  # 最多顯示 10 個錯誤
                                            st.text(err)

                            st.info(f"📊 匯入統計：總計 {len(perf_df)} 筆，成功 {success_count} 筆，失敗 {error_count} 筆")
                            st.rerun()

                except Exception as e:
                    st.error(f"讀取檔案失敗: {str(e)}")

        # 訓練記錄匯入
        with import_tab4:
            st.write("**上傳訓練記錄**")

            with st.expander("📋 必填欄位說明", expanded=False):
                st.markdown("""
                **必填欄位**（系統會自動識別以下任一名稱）：
                - **工號**：`emp_id` / `工號` / `員工編號` / `employee_id`
                - **課程名稱**：`course_name` / `課程名稱` / `訓練課程`
                - **課程類型**：`course_type` / `課程類型` / `訓練類型`
                - **時數**：`hours` / `時數` / `訓練時數`
                - **完訓日期**：`completion_date` / `完訓日期` / `結訓日期`

                ✅ 系統支援**不區分大小寫**，`EMP_ID` 和 `emp_id` 都可以識別
                """)

            train_file = st.file_uploader("選擇訓練記錄檔案", type=['xlsx', 'csv'], key='train_file')

            if train_file:
                try:
                    train_df = pd.read_excel(train_file) if train_file.name.endswith('xlsx') else pd.read_csv(train_file)

                    # 必填欄位驗證
                    required_cols = {
                        '工號': ['emp_id', '工號', '員工編號', 'employee_id'],
                        '課程名稱': ['course_name', '課程名稱', '訓練課程'],
                        '課程類型': ['course_type', '課程類型', '訓練類型'],
                        '時數': ['hours', '時數', '訓練時數'],
                        '完訓日期': ['completion_date', '完訓日期', '結訓日期']
                    }

                    is_valid, missing = st.session_state.checker.validate_required_columns(train_df, required_cols)

                    if not is_valid:
                        st.error(f"❌ 缺少必填欄位：{', '.join(missing)}")
                        st.info("💡 請參考上方「必填欄位說明」，確認檔案包含所有必要欄位")
                    else:
                        # 顯示欄位對應
                        st.success("✅ 所有必填欄位都已找到")

                        col_mapping = {}
                        for display_name, possible_names in required_cols.items():
                            found_col = st.session_state.checker.find_column(train_df, possible_names)
                            if found_col:
                                col_mapping[display_name] = found_col

                        with st.expander("📊 欄位對應關係", expanded=False):
                            for display_name, file_col in col_mapping.items():
                                st.write(f"- {display_name} ← `{file_col}`")

                        st.write("**檔案預覽**:")
                        st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                        st.dataframe(train_df)

                        if st.button("匯入訓練記錄", key='import_train'):
                            success_count = 0
                            error_count = 0
                            errors = []

                            for idx, row in train_df.iterrows():
                                try:
                                    emp_id_col = st.session_state.checker.find_column(train_df, required_cols['工號'])
                                    course_name_col = st.session_state.checker.find_column(train_df, required_cols['課程名稱'])
                                    course_type_col = st.session_state.checker.find_column(train_df, required_cols['課程類型'])
                                    hours_col = st.session_state.checker.find_column(train_df, required_cols['時數'])
                                    completion_date_col = st.session_state.checker.find_column(train_df, required_cols['完訓日期'])

                                    result = st.session_state.checker.db_training.add_training_record(
                                        emp_id=row[emp_id_col],
                                        course_name=row[course_name_col],
                                        course_type=row[course_type_col],
                                        hours=float(row[hours_col]),
                                        completion_date=row[completion_date_col]
                                    )
                                    if result:
                                        success_count += 1
                                    else:
                                        error_count += 1
                                except Exception as e:
                                    error_count += 1
                                    errors.append(f"第 {idx + 2} 列: {str(e)}")

                            # 顯示匯入結果
                            if success_count > 0:
                                st.success(f"✅ 成功匯入 {success_count} 筆訓練記錄")
                            if error_count > 0:
                                st.warning(f"⚠️ {error_count} 筆記錄匯入失敗")
                                if errors:
                                    with st.expander("查看錯誤詳情"):
                                        for err in errors[:10]:  # 最多顯示 10 個錯誤
                                            st.text(err)

                            st.info(f"📊 匯入統計：總計 {len(train_df)} 筆，成功 {success_count} 筆，失敗 {error_count} 筆")
                            st.rerun()

                except Exception as e:
                    st.error(f"讀取檔案失敗: {str(e)}")

    # Tab 3: 資料庫管理
    with tab3:
        from io import BytesIO

        st.subheader("🗄️ 資料庫管理")
        st.warning("⚠️ 請謹慎操作，刪除後無法復原！")

        # 選擇要管理的資料庫
        db_type = st.selectbox("選擇資料庫", [
            "員工資料 (employees)",
            "績效資料 (performance)",
            "訓練資料 (training)",
            "離職資料 (separation)"
        ])

        # 使用單一資料庫 m5_qualification，根據選擇載入對應的表
        db = st.session_state.checker.db  # Single database for all tables

        if "員工資料" in db_type:
            table_name = "employees"
            all_data = db.get_all_employees()
        elif "績效資料" in db_type:
            table_name = "performance"
            all_data = db.get_all_records(table_name='performance')
        elif "訓練資料" in db_type:
            table_name = "training"
            all_data = db.get_all_records(table_name='training')
        else:  # 離職資料
            table_name = "separation"
            all_data = db.get_all_records(table_name='separation')

        if all_data:
            st.info(f"📊 {db_type} 中共有 {len(all_data)} 筆資料")

            # 顯示資料
            df_display = pd.DataFrame(all_data)
            st.dataframe(df_display, use_container_width=True)

            st.divider()

            # 管理選項
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("清空資料庫")
                confirm = st.checkbox(f"我確認要清空 {db_type} 的所有資料", key=f"confirm_clear_{db_type}")
                if confirm:
                    if st.button("🗑️ 確認清空", type="primary", key=f"clear_btn_{db_type}"):
                        try:
                            db.clear_all_data(table_name=table_name)
                            st.success(f"{db_type} 已清空")
                            st.rerun()
                        except Exception as e:
                            st.error(f"清空失敗: {str(e)}")

            with col2:
                st.subheader("匯出資料")
                # 匯出資料庫內容
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_display.to_excel(writer, index=False, sheet_name=table_name)
                output.seek(0)

                st.download_button(
                    label="📥 下載備份檔案",
                    data=output,
                    file_name=f"m5_{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # 依條件刪除
            st.divider()
            st.subheader("依條件刪除")

            if "員工資料" in db_type:
                emp_to_delete = st.multiselect(
                    "選擇要刪除的員工",
                    options=[f"{emp['emp_id']} - {emp['name']}" for emp in all_data]
                )

                if emp_to_delete and st.button("刪除選定員工", type="primary"):
                    emp_ids = [e.split(" - ")[0] for e in emp_to_delete]
                    try:
                        for emp_id in emp_ids:
                            db.delete_employee(emp_id)
                        st.success(f"已刪除 {len(emp_ids)} 位員工")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {str(e)}")
            else:
                # 其他資料庫提供依工號刪除
                emp_id_to_delete = st.text_input("輸入要刪除的工號")
                if emp_id_to_delete and st.button("刪除此工號的所有記錄", type="primary"):
                    try:
                        db.delete_by_emp_id(emp_id_to_delete, table_name=table_name)
                        st.success(f"已刪除工號 {emp_id_to_delete} 的所有記錄")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {str(e)}")

        else:
            st.info(f"{db_type} 中無資料")
