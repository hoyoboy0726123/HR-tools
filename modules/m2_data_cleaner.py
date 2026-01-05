# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from core.data_processor import DataProcessor
from core.db_manager import DBManager
from utils.file_handler import FileHandler
from io import BytesIO
from datetime import datetime


def render():
    st.title('資料清洗器')
    st.markdown('動態欄位偵測、資料類型轉換、清洗步驟可視化')

    if 'cleaning_steps' not in st.session_state:
        st.session_state.cleaning_steps = []
    if 'processor' not in st.session_state:
        st.session_state.processor = None

    # 初始化範本資料庫
    template_db = DBManager('workflow_templates')

    # ========== 範本管理區 ==========
    st.divider()
    with st.expander('📁 清洗流程範本管理', expanded=False):
        tab_new, tab_load, tab_manage = st.tabs(['新建流程', '載入範本', '管理範本'])

        with tab_new:
            st.info('選擇此選項以建立新的清洗流程（不使用範本）')
            if st.button('清除已載入的範本'):
                if 'loaded_template_m2' in st.session_state:
                    del st.session_state.loaded_template_m2
                st.session_state.cleaning_steps = []
                st.success('已清除範本')
                st.rerun()

        with tab_load:
            templates = template_db.get_all_templates('M2')
            if templates:
                st.write(f'找到 {len(templates)} 個已儲存的範本：')

                for template in templates:
                    with st.expander(f"📄 {template['template_name']}", expanded=False):
                        st.caption(f"說明：{template.get('description', '無說明')}")
                        st.caption(f"建立時間：{template['created_at']}")
                        st.caption(f"更新時間：{template['updated_at']}")

                        if st.button(f'載入此範本', key=f"load_{template['template_name']}"):
                            full_template = template_db.load_template('M2', template['template_name'])
                            if full_template:
                                st.session_state.loaded_template_m2 = full_template
                                # 載入清洗步驟
                                st.session_state.cleaning_steps = full_template['config'].get('cleaning_steps', [])
                                st.success(f"✅ 已載入範本「{template['template_name']}」")
                                st.info('⬇️ 請向下滾動上傳檔案，系統將自動套用清洗步驟')
                                st.rerun()
            else:
                st.info('目前沒有已儲存的範本')

        with tab_manage:
            templates = template_db.get_all_templates('M2')
            if templates:
                st.write(f'管理 {len(templates)} 個範本：')

                for template in templates:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"📄 **{template['template_name']}**")
                        st.caption(template.get('description', '無說明'))
                    with col2:
                        if st.button('🗑️', key=f"del_{template['template_name']}", help='刪除此範本'):
                            result = template_db.delete_template('M2', template['template_name'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
            else:
                st.info('目前沒有範本可管理')

    # 檢查是否有載入的範本
    has_template = 'loaded_template_m2' in st.session_state and st.session_state.loaded_template_m2 is not None

    if has_template:
        template_info = st.session_state.loaded_template_m2
        st.info(f"📁 已載入範本：**{template_info['template_name']}** | {template_info.get('description', '')} | 包含 {len(st.session_state.cleaning_steps)} 個清洗步驟")

    st.divider()
    st.subheader('步驟 1: 上傳原始資料')
    uploaded_file = st.file_uploader(
        '上傳 Excel 或 CSV 檔案',
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file:
        try:
            df = FileHandler.load_file(uploaded_file)

            if st.session_state.processor is None:
                st.session_state.processor = DataProcessor(df)

            processor = st.session_state.processor

            st.success(f'已載入 {len(df)} 筆資料，{len(df.columns)} 個欄位')

            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader('📄 原始資料預覽（固定顯示）')
                st.caption('此預覽永遠顯示原始資料，方便與清洗後結果對比')
                st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                st.dataframe(processor.original_df, use_container_width=True)

            with col2:
                st.subheader('欄位分析')
                for col in processor.original_df.columns:
                    stats = processor.get_column_stats(col)
                    with st.expander(f'{col}'):
                        st.write(f"類型: {stats['dtype']}")
                        st.write(f"空值: {stats['null_count']} ({stats['null_percent']}%)")
                        st.write(f"唯一值: {stats['unique_count']}")

            st.subheader('步驟 2: 設定清洗操作')

            operation = st.selectbox('選擇操作', [
                '去除前後空白',
                '統一日期格式',
                '移除重複值',
                '填入空值',
                '重新命名欄位',
                '轉換資料類型',
                '刪除欄位'
            ])

            if operation == '去除前後空白':
                target_col = st.selectbox('選擇欄位', processor.df.columns, key='trim_col')
                if st.button('加入步驟', key='add_trim'):
                    st.session_state.cleaning_steps.append({
                        'action': 'trim_whitespace',
                        'column': target_col,
                        'description': f'去除 {target_col} 前後空白'
                    })
                    st.rerun()

            elif operation == '統一日期格式':
                target_col = st.selectbox('選擇欄位', processor.df.columns, key='date_col')
                date_format = st.selectbox('目標格式', [
                    '%Y-%m-%d',
                    '%Y/%m/%d',
                    '%d/%m/%Y',
                    '%m/%d/%Y'
                ])
                if st.button('加入步驟', key='add_date'):
                    st.session_state.cleaning_steps.append({
                        'action': 'unify_date_format',
                        'column': target_col,
                        'format': date_format,
                        'description': f'統一 {target_col} 為 {date_format}'
                    })
                    st.rerun()

            elif operation == '移除重複值':
                subset_cols = st.multiselect('依據欄位', processor.df.columns)
                keep = st.selectbox('保留', ['first', 'last'])
                if st.button('加入步驟', key='add_dup'):
                    st.session_state.cleaning_steps.append({
                        'action': 'remove_duplicates',
                        'subset': subset_cols if subset_cols else None,
                        'keep': keep,
                        'description': f'移除重複值 (保留 {keep})'
                    })
                    st.rerun()

            elif operation == '填入空值':
                target_col = st.selectbox('選擇欄位', processor.df.columns, key='fill_col')
                fill_value = st.text_input('填入值', value='')
                if st.button('加入步驟', key='add_fill'):
                    st.session_state.cleaning_steps.append({
                        'action': 'fill_na',
                        'column': target_col,
                        'value': fill_value,
                        'description': f'填入 {target_col} 空值為 "{fill_value}"'
                    })
                    st.rerun()

            elif operation == '重新命名欄位':
                target_col = st.selectbox('選擇欄位', processor.df.columns, key='rename_col')
                new_name = st.text_input('新名稱')
                if st.button('加入步驟', key='add_rename') and new_name:
                    st.session_state.cleaning_steps.append({
                        'action': 'rename_column',
                        'column': target_col,
                        'new_name': new_name,
                        'description': f'重新命名 {target_col} → {new_name}'
                    })
                    st.rerun()

            elif operation == '轉換資料類型':
                target_col = st.selectbox('選擇欄位', processor.df.columns, key='convert_col')
                target_type = st.selectbox('目標類型', ['string', 'numeric', 'datetime'])
                if st.button('加入步驟', key='add_convert'):
                    st.session_state.cleaning_steps.append({
                        'action': 'convert_type',
                        'column': target_col,
                        'target_type': target_type,
                        'description': f'轉換 {target_col} 為 {target_type}'
                    })
                    st.rerun()

            elif operation == '刪除欄位':
                target_col = st.selectbox('選擇欄位', processor.df.columns, key='drop_col')
                if st.button('加入步驟', key='add_drop'):
                    st.session_state.cleaning_steps.append({
                        'action': 'drop_column',
                        'column': target_col,
                        'description': f'刪除 {target_col}'
                    })
                    st.rerun()

            st.subheader('步驟 3: 待執行步驟')
            if st.session_state.cleaning_steps:
                for i, step in enumerate(st.session_state.cleaning_steps):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{i+1}. {step.get('description', step['action'])}")
                    with col2:
                        if st.button('刪除', key=f'del_{i}'):
                            st.session_state.cleaning_steps.pop(i)
                            st.rerun()

                col1, col2 = st.columns(2)
                with col1:
                    if st.button('執行全部步驟', type='primary', use_container_width=True):
                        for step in st.session_state.cleaning_steps:
                            processor.apply_cleaning_step(step)
                        st.success('清洗完成！')
                        st.rerun()
                with col2:
                    if st.button('清空步驟', use_container_width=True):
                        st.session_state.cleaning_steps = []
                        st.rerun()
            else:
                st.info('尚無待執行步驟')

            if processor.history:
                st.divider()
                st.subheader('步驟 4: 清洗結果預覽')
                st.success(f'✅ 執行了 {len(processor.history)} 個清洗步驟')
                st.caption('⬆️ 請向上滾動查看「原始資料預覽」，與下方清洗後的資料進行對比')

                st.write('**清洗後的資料：**')
                st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                st.dataframe(processor.df, use_container_width=True)

                st.write('**資料變化統計：**')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('原始資料筆數', len(processor.original_df))
                    st.metric('清洗後筆數', len(processor.df),
                             delta=len(processor.df) - len(processor.original_df))
                with col2:
                    st.metric('原始欄位數', len(processor.original_df.columns))
                    st.metric('清洗後欄位數', len(processor.df.columns),
                             delta=len(processor.df.columns) - len(processor.original_df.columns))
                with col3:
                    original_nulls = processor.original_df.isnull().sum().sum()
                    cleaned_nulls = processor.df.isnull().sum().sum()
                    st.metric('原始空值總數', original_nulls)
                    st.metric('清洗後空值總數', cleaned_nulls,
                             delta=cleaned_nulls - original_nulls)

                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    processor.df.to_excel(writer, index=False, sheet_name='清洗結果')
                output.seek(0)

                st.download_button(
                    label='下載清洗結果',
                    data=output,
                    file_name=f'cleaned_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )

                # ========== 儲存為範本 ==========
                st.divider()
                st.subheader('💾 儲存此清洗流程為範本')
                st.info('儲存後，下次處理相同格式的資料時可以直接套用，無需重新設定')

                with st.form('save_template_form_m2'):
                    template_name = st.text_input('範本名稱', placeholder='例如：員工資料清洗流程')
                    template_desc = st.text_area('範本說明（選填）', placeholder='簡短描述此範本的用途')

                    submitted = st.form_submit_button('💾 儲存範本', type='primary')

                    if submitted:
                        if not template_name.strip():
                            st.error('請輸入範本名稱')
                        else:
                            # 建立範本設定
                            template_config = {
                                'cleaning_steps': st.session_state.cleaning_steps
                            }

                            result = template_db.save_template(
                                module='M2',
                                template_name=template_name.strip(),
                                config=template_config,
                                description=template_desc.strip() if template_desc.strip() else None
                            )

                            if result['success']:
                                st.success(result['message'])
                                st.balloons()
                            else:
                                st.error(result['message'])

                if st.button('重置為原始資料'):
                    processor.reset()
                    st.session_state.cleaning_steps = []
                    st.rerun()

        except Exception as e:
            st.error(f'處理失敗: {str(e)}')
    else:
        st.info('請上傳檔案開始使用')
