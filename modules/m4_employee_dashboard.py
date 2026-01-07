# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from core.db_manager_multiuser import DBManagerMultiUser
from utils.file_handler import FileHandler
from io import BytesIO
from datetime import datetime


def render():
    st.title('員工資料查詢')
    st.markdown('查詢員工基本資料、績效歷程、訓練紀錄')

    # 取得當前登入用戶的 user_id
    user_id = st.session_state.user_info['user_id']

    # 再次確認資料庫結構（確保遷移已執行）
    from core.db_migration import migrate_add_user_id_column
    migrate_add_user_id_column()

    # 使用 M4 模組專屬資料庫（支援多用戶）
    db_employees = DBManagerMultiUser('m4_employees', user_id=user_id)
    db_performance = DBManagerMultiUser('m4_performance', user_id=user_id)
    db_training = DBManagerMultiUser('m4_training', user_id=user_id)
    db_separation = DBManagerMultiUser('m4_separation', user_id=user_id)

    # 初始化查詢結果累積
    if 'accumulated_results' not in st.session_state:
        st.session_state.accumulated_results = []

    tab1, tab2, tab3 = st.tabs(['查詢員工', '資料匯入', '資料庫管理'])

    with tab1:
        st.subheader('搜尋員工')

        # 取得所有員工姓名列表
        all_employees = db_employees.get_all_employees()

        if all_employees:
            # 使用多選下拉選單
            selected_names = st.multiselect(
                '選擇員工（可多選）',
                options=[emp['name'] for emp in all_employees],
                default=None,
                help='可以選擇多個員工，查詢結果會累積'
            )

            if selected_names:
                # 為每個選擇的員工查詢資料
                for name in selected_names:
                    employees = db_employees.search_employee(name)

                    if employees:
                        for emp in employees:
                            emp_id = emp['emp_id']

                            with st.expander(f"👤 {emp['name']} ({emp_id})", expanded=True):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric('工號', emp_id)
                                with col2:
                                    st.metric('姓名', emp['name'])
                                with col3:
                                    st.metric('部門', emp.get('department', 'N/A'))
                                with col4:
                                    status_color = '🟢' if emp.get('status') == 'active' else '🔴'
                                    st.metric('狀態', f"{status_color} {emp.get('status', 'N/A')}")

                                st.write(f"**到職日**: {emp.get('hire_date', 'N/A')}")

                                # 績效歷程
                                st.markdown('**績效歷程**')
                                perf_records = db_performance.get_performance_history(emp_id)
                                if perf_records:
                                    perf_df = pd.DataFrame(perf_records)
                                    st.dataframe(
                                        perf_df[['year', 'rating', 'score']],
                                        hide_index=True,
                                        width='stretch'
                                    )
                                    avg_score = perf_df['score'].mean() if 'score' in perf_df.columns else 0
                                    st.metric('平均分數', f'{avg_score:.2f}')
                                else:
                                    st.info('無績效紀錄')

                                # 訓練紀錄
                                st.markdown('**訓練紀錄**')
                                training_records = db_training.get_training_history(emp_id)
                                if training_records:
                                    training_df = pd.DataFrame(training_records)
                                    st.dataframe(
                                        training_df[['course_name', 'course_type', 'hours', 'completion_date']],
                                        hide_index=True,
                                        width='stretch'
                                    )
                                    total_hours = training_df['hours'].sum() if 'hours' in training_df.columns else 0
                                    st.metric('總完訓時數', f'{total_hours:.1f} 小時')
                                else:
                                    st.info('無訓練紀錄')

                                # 離職紀錄
                                sep_record = db_separation.get_separation_record(emp_id)
                                if sep_record:
                                    st.markdown('**離職紀錄**')
                                    st.warning(f"**離職日期**: {sep_record.get('separation_date', 'N/A')}")
                                    st.write(f"**離職類型**: {sep_record.get('separation_type', 'N/A')}")
                                    st.write(f"**原因**: {sep_record.get('reason', 'N/A')}")
                                    if sep_record.get('blacklist'):
                                        st.error('⚠️ 此員工已列入黑名單')

                                # 匯出選項
                                st.divider()
                                btn_col1, btn_col2 = st.columns(2)

                                with btn_col1:
                                    # 單一員工匯出
                                    output_single = BytesIO()
                                    with pd.ExcelWriter(output_single, engine='openpyxl') as writer:
                                        # 基本資料
                                        basic_df = pd.DataFrame([{
                                            '工號': emp_id,
                                            '姓名': emp['name'],
                                            '部門': emp.get('department', 'N/A'),
                                            '狀態': emp.get('status', 'N/A'),
                                            '到職日': emp.get('hire_date', 'N/A')
                                        }])
                                        basic_df.to_excel(writer, index=False, sheet_name='基本資料')

                                        # 績效歷程
                                        if perf_records:
                                            perf_df.to_excel(writer, index=False, sheet_name='績效歷程')

                                        # 訓練紀錄
                                        if training_records:
                                            training_df.to_excel(writer, index=False, sheet_name='訓練紀錄')

                                        # 離職紀錄
                                        if sep_record:
                                            sep_df = pd.DataFrame([sep_record])
                                            sep_df.to_excel(writer, index=False, sheet_name='離職紀錄')

                                    output_single.seek(0)

                                    st.download_button(
                                        label='📄 匯出此員工',
                                        data=output_single,
                                        file_name=f'{emp_id}_{emp["name"]}_{datetime.now().strftime("%Y%m%d")}.xlsx',
                                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                        key=f'export_single_{emp_id}'
                                    )

                                with btn_col2:
                                    # 加入到累積結果
                                    if st.button(f'加入到批次匯出', key=f'add_{emp_id}'):
                                        # 建立完整的員工資料記錄（包含詳細資料）
                                        full_record = {
                                            'emp_id': emp_id,
                                            'name': emp['name'],
                                            'department': emp.get('department', 'N/A'),
                                            'status': emp.get('status', 'N/A'),
                                            'hire_date': emp.get('hire_date', 'N/A'),
                                            'perf_records': perf_records if perf_records else [],
                                            'training_records': training_records if training_records else [],
                                            'sep_record': sep_record if sep_record else None
                                        }

                                        # 檢查是否已存在
                                        if not any(r['emp_id'] == emp_id for r in st.session_state.accumulated_results):
                                            st.session_state.accumulated_results.append(full_record)
                                            st.success(f'已加入 {emp["name"]} 到批次匯出清單')
                                        else:
                                            st.warning(f'{emp["name"]} 已在批次匯出清單中')

                st.divider()
                # 顯示累積結果和匯出功能
                if st.session_state.accumulated_results:
                    st.subheader(f'📋 批次匯出清單 ({len(st.session_state.accumulated_results)} 位員工)')

                    # 顯示清單摘要
                    summary_data = []
                    for record in st.session_state.accumulated_results:
                        summary_data.append({
                            '工號': record['emp_id'],
                            '姓名': record['name'],
                            '部門': record['department'],
                            '狀態': record['status']
                        })
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, width='stretch')

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button('🗑️ 清空清單', type='secondary'):
                            st.session_state.accumulated_results = []
                            st.rerun()

                    with col2:
                        # 批次匯出總表（所有人在一起）
                        summary_full = []
                        for record in st.session_state.accumulated_results:
                            summary_full.append({
                                '工號': record['emp_id'],
                                '姓名': record['name'],
                                '部門': record['department'],
                                '狀態': record['status'],
                                '到職日': record['hire_date'],
                                '平均績效分數': pd.DataFrame(record['perf_records'])['score'].mean() if record['perf_records'] else 0,
                                '總完訓時數': pd.DataFrame(record['training_records'])['hours'].sum() if record['training_records'] else 0
                            })

                        output_summary = BytesIO()
                        with pd.ExcelWriter(output_summary, engine='openpyxl') as writer:
                            pd.DataFrame(summary_full).to_excel(writer, index=False, sheet_name='員工總表')
                        output_summary.seek(0)

                        st.download_button(
                            label='📊 下載總表',
                            data=output_summary,
                            file_name=f'employees_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )

                    with col3:
                        # 批次匯出 Excel（一個員工一個分頁）
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            for record in st.session_state.accumulated_results:
                                emp_id = record['emp_id']
                                emp_name = record['name']
                                sheet_name = f"{emp_id}_{emp_name}"[:31]  # Excel 分頁名稱限制 31 字元

                                # 建立該員工的完整資料
                                emp_data = {
                                    '基本資料': pd.DataFrame([{
                                        '工號': record['emp_id'],
                                        '姓名': record['name'],
                                        '部門': record['department'],
                                        '狀態': record['status'],
                                        '到職日': record['hire_date']
                                    }])
                                }

                                # 將所有資料寫入同一分頁
                                start_row = 0

                                # 寫入基本資料
                                emp_data['基本資料'].to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)
                                start_row += len(emp_data['基本資料']) + 3

                                # 寫入績效歷程
                                if record['perf_records']:
                                    perf_df = pd.DataFrame(record['perf_records'])
                                    writer.sheets[sheet_name].cell(row=start_row+1, column=1, value='績效歷程')
                                    perf_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row+1)
                                    start_row += len(perf_df) + 4

                                # 寫入訓練紀錄
                                if record['training_records']:
                                    training_df = pd.DataFrame(record['training_records'])
                                    writer.sheets[sheet_name].cell(row=start_row+1, column=1, value='訓練紀錄')
                                    training_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row+1)
                                    start_row += len(training_df) + 4

                                # 寫入離職紀錄
                                if record['sep_record']:
                                    sep_df = pd.DataFrame([record['sep_record']])
                                    writer.sheets[sheet_name].cell(row=start_row+1, column=1, value='離職紀錄')
                                    sep_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row+1)

                        output.seek(0)

                        st.download_button(
                            label='📥 下載詳細分頁',
                            data=output,
                            file_name=f'employees_detailed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            type='primary'
                        )
        else:
            st.info('資料庫中無員工資料，請先匯入資料')

    with tab2:
        st.subheader('資料匯入')
        st.markdown('上傳 Excel/CSV 檔案批次匯入員工資料')

        import_type = st.selectbox('選擇匯入類型', [
            '員工主檔',
            '績效資料',
            '訓練紀錄'
        ])

        uploaded_file = st.file_uploader(
            '上傳檔案',
            type=['xlsx', 'xls', 'csv'],
            key='import_file'
        )

        if uploaded_file:
            try:
                df = FileHandler.load_file(uploaded_file)

                st.write('檔案預覽:')
                st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                st.dataframe(df, width='stretch')

                st.info(f'共 {len(df)} 筆資料，{len(df.columns)} 個欄位')
                st.write('欄位列表:', ', '.join(df.columns.tolist()))

                if st.button('執行匯入', type='primary', width='stretch'):
                    with st.spinner('正在匯入資料...'):
                        if import_type == '員工主檔':
                            result = db_employees.import_employee_data(df)
                        elif import_type == '績效資料':
                            result = db_performance.import_performance_data(df)
                        elif import_type == '訓練紀錄':
                            result = db_training.import_training_data(df)
                        else:
                            result = {'success': False, 'error': 'Unknown import type'}

                        if result.get('success'):
                            st.success(f"匯入成功！共 {result.get('count', 0)} 筆")
                            st.balloons()
                        else:
                            st.error(f"匯入失敗: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f'讀取檔案失敗: {str(e)}')
        else:
            st.info('請上傳檔案開始匯入')

            with st.expander('查看欄位對照表'):
                st.markdown("""
                **員工主檔** 需要包含:
                - `emp_id` 或 `工號` (必填)
                - `name` 或 `姓名` (必填)
                - `department` 或 `部門` (選填)
                - `hire_date` 或 `到職日` (選填)

                **績效資料** 需要包含:
                - `emp_id` 或 `工號` (必填)
                - `year` 或 `年度` (必填)
                - `rating` 或 `考績` (選填)
                - `score` 或 `分數` (選填)

                **訓練紀錄** 需要包含:
                - `emp_id` 或 `工號` (必填)
                - `course_name` 或 `課程名稱` (必填)
                - `course_type` 或 `課程類別` (選填)
                - `hours` 或 `時數` (選填)
                - `completion_date` 或 `完成日期` (選填)
                """)

    with tab3:
        st.subheader('🗄️ 資料庫管理')
        st.warning('⚠️ 請謹慎操作，刪除後無法復原！')

        manage_type = st.selectbox('選擇管理資料庫', [
            '員工主檔',
            '績效資料',
            '訓練紀錄'
        ])

        # 根據選擇的資料庫顯示內容
        if manage_type == '員工主檔':
            db = db_employees
            all_data = db.get_all_employees()
            table_name = 'employees'
        elif manage_type == '績效資料':
            db = db_performance
            all_data = db.get_all_records()
            table_name = 'performance'
        else:  # 訓練紀錄
            db = db_training
            all_data = db.get_all_records()
            table_name = 'training'

        if all_data:
            st.info(f'資料庫中共有 {len(all_data)} 筆資料')

            # 顯示資料
            df_display = pd.DataFrame(all_data)
            st.dataframe(df_display, width='stretch')

            st.divider()

            # 刪除選項
            st.subheader('刪除資料')

            col1, col2 = st.columns(2)

            with col1:
                st.subheader('清空資料庫')
                confirm = st.checkbox(f'我確認要清空 {manage_type} 的所有資料', key=f'confirm_clear_{manage_type}')
                if confirm:
                    if st.button('🗑️ 確認清空', type='primary', key=f'clear_btn_{manage_type}'):
                        try:
                            db.clear_all_data()
                            st.success('資料庫已清空')
                            st.rerun()
                        except Exception as e:
                            st.error(f'清空失敗: {str(e)}')

            with col2:
                # 匯出當前資料庫內容
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_display.to_excel(writer, index=False, sheet_name=table_name)
                output.seek(0)

                st.download_button(
                    label='📥 匯出資料庫內容',
                    data=output,
                    file_name=f'{table_name}_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            # 依條件刪除
            st.divider()
            st.subheader('依條件刪除')

            if manage_type == '員工主檔':
                emp_to_delete = st.multiselect(
                    '選擇要刪除的員工',
                    options=[f"{emp['emp_id']} - {emp['name']}" for emp in all_data]
                )

                if emp_to_delete and st.button('刪除選定員工', type='primary'):
                    emp_ids = [e.split(' - ')[0] for e in emp_to_delete]
                    try:
                        for emp_id in emp_ids:
                            db.delete_employee(emp_id)
                        st.success(f'已刪除 {len(emp_ids)} 位員工')
                        st.rerun()
                    except Exception as e:
                        st.error(f'刪除失敗: {str(e)}')
            else:
                # 其他資料庫提供依工號刪除
                emp_id_to_delete = st.text_input('輸入要刪除的工號')
                if emp_id_to_delete and st.button('刪除此工號的所有記錄', type='primary'):
                    try:
                        db.delete_by_emp_id(emp_id_to_delete)
                        st.success(f'已刪除工號 {emp_id_to_delete} 的所有記錄')
                        st.rerun()
                    except Exception as e:
                        st.error(f'刪除失敗: {str(e)}')

        else:
            st.info('資料庫中無資料')
