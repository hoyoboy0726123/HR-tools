# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from core.column_matcher import ColumnMatcher
from core.db_manager import DBManager
from utils.file_handler import FileHandler
from datetime import datetime
from io import BytesIO


def render():
    st.title('報表合併器')
    st.markdown('整合多份欄位不統一的報表，智慧對齊欄位')

    # 初始化範本資料庫
    template_db = DBManager('workflow_templates')

    # ========== 範本管理區 ==========
    st.divider()
    with st.expander('📁 流程範本管理', expanded=False):
        tab_new, tab_load, tab_manage = st.tabs(['新建流程', '載入範本', '管理範本'])

        with tab_new:
            st.info('選擇此選項以建立新的合併流程（不使用範本）')

        with tab_load:
            templates = template_db.get_all_templates('M1')
            if templates:
                st.write(f'找到 {len(templates)} 個已儲存的範本：')

                # 顯示範本列表
                for template in templates:
                    with st.expander(f"📄 {template['template_name']}", expanded=False):
                        st.caption(f"說明：{template.get('description', '無說明')}")
                        st.caption(f"建立時間：{template['created_at']}")
                        st.caption(f"更新時間：{template['updated_at']}")

                        if st.button(f'載入此範本', key=f"load_{template['template_name']}"):
                            # 載入完整範本資料
                            full_template = template_db.load_template('M1', template['template_name'])
                            if full_template:
                                st.session_state.loaded_template = full_template
                                st.success(f"✅ 已載入範本「{template['template_name']}」")
                                st.info('⬇️ 請向下滾動至「步驟 1」上傳檔案，系統將自動套用範本設定')
                                st.rerun()
            else:
                st.info('目前沒有已儲存的範本')

        with tab_manage:
            templates = template_db.get_all_templates('M1')
            if templates:
                st.write(f'管理 {len(templates)} 個範本：')

                for template in templates:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"📄 **{template['template_name']}**")
                        st.caption(template.get('description', '無說明'))
                    with col2:
                        if st.button('🗑️', key=f"del_{template['template_name']}", help='刪除此範本'):
                            result = template_db.delete_template('M1', template['template_name'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
            else:
                st.info('目前沒有範本可管理')

    st.divider()
    st.subheader('步驟 1: 上傳報表檔案')
    uploaded_files = st.file_uploader(
        '上傳 Excel 或 CSV 檔案 (可多選)',
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        key='file_uploader'
    )

    if not uploaded_files:
        st.info('📂 請上傳至少一個檔案開始使用')
        return

    # 載入檔案（每次都重新載入，不保存）
    try:
        dataframes = {}
        for file in uploaded_files:
            df = FileHandler.load_file(file)
            dataframes[file.name] = df
    except Exception as e:
        st.error(f'載入檔案失敗: {e}')
        return

    st.success(f'已載入 {len(dataframes)} 個檔案')

    # 顯示檔案預覽
    for filename, df in dataframes.items():
        with st.expander(f'📄 {filename}'):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric('資料筆數', df.shape[0])
                st.metric('欄位數量', df.shape[1])
            with col2:
                st.write('**欄位列表:**')
                st.code(', '.join(df.columns.tolist()))
            st.write('**資料預覽:**')
            st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
            st.dataframe(df, width='stretch')

    # 檢查是否有載入的範本
    has_template = 'loaded_template' in st.session_state and st.session_state.loaded_template is not None

    if has_template:
        template_info = st.session_state.loaded_template
        st.info(f"📁 已載入範本：**{template_info['template_name']}** | {template_info.get('description', '')}")

    st.divider()
    st.subheader('步驟 2: 智慧欄位對齊')

    # 收集所有欄位
    all_columns = {}
    for filename, df in dataframes.items():
        for col in df.columns:
            if col not in all_columns:
                all_columns[col] = []
            all_columns[col].append(filename)

    # 如果有範本，直接使用範本的欄位對應
    if has_template:
        template_config = template_info['config']
        unified_mapping_from_template = template_config.get('column_mapping', {})

        st.success('✅ 使用範本的欄位對應設定')
        st.write('**範本設定的欄位對應：**')

        # 顯示範本的欄位對應
        mapping_display = {}
        for orig_col, unified_col in unified_mapping_from_template.items():
            if unified_col not in mapping_display:
                mapping_display[unified_col] = []
            mapping_display[unified_col].append(orig_col)

        for unified_col, orig_cols in mapping_display.items():
            st.write(f"- **{unified_col}** ← {', '.join(orig_cols)}")

        # 直接跳到步驟 3
        unified_mapping = unified_mapping_from_template
        column_groups = {}  # 不需要用戶設定

    else:
        # 原有的智慧欄位對齊邏輯
        # 找出相似欄位
        from difflib import SequenceMatcher
        column_groups = {}
        all_col_list = list(all_columns.keys())
        processed = set()

        for col in all_col_list:
            if col in processed:
                continue

            group = [col]
            for other_col in all_col_list:
                if other_col != col and other_col not in processed:
                    similarity = SequenceMatcher(None, col.lower(), other_col.lower()).ratio()
                    if similarity >= 0.6:
                        group.append(other_col)
                        processed.add(other_col)

            processed.add(col)
            standard_name = min(group, key=len) if len(group) > 1 else col
            column_groups[standard_name] = group

        st.write('**系統自動識別的欄位對應關係：**')
        st.info('請確認以下欄位對應是否正確，您可以修改「統一欄位名稱」')

        # 收集所有唯一的欄位名稱（用於下拉選單）
        all_unique_cols = sorted(set(all_columns.keys()))

        # 顯示欄位群組並收集用戶輸入
        group_idx = 0
        for standard_name, similar_cols in column_groups.items():
            if len(similar_cols) > 1:
                with st.expander(f'🔗 欄位群組 {group_idx + 1}: {", ".join(similar_cols)}', expanded=True):
                    st.write(f'**識別到的相似欄位:** {", ".join(similar_cols)}')

                    for col in similar_cols:
                        st.caption(f'  • `{col}` 來自: {", ".join(all_columns[col])}')

                    st.text_input(
                        '統一欄位名稱',
                        value=standard_name,
                        key=f'unified_name_{group_idx}'
                    )
                group_idx += 1
            else:
                # 顯示單獨欄位，讓用戶可以選擇對應到哪個欄位
                col_name = similar_cols[0]
                with st.expander(f'📌 單獨欄位: {col_name}', expanded=False):
                    st.caption(f'來自: {", ".join(all_columns[col_name])}')

                    # 提供選項：保持原樣或對應到其他欄位
                    map_option = st.radio(
                        '處理方式',
                        ['保持原欄位名稱', '對應到其他欄位'],
                        key=f'map_option_{group_idx}'
                    )

                    if map_option == '對應到其他欄位':
                        st.selectbox(
                            '對應到',
                            options=all_unique_cols,
                            key=f'unified_name_{group_idx}'
                        )
                    else:
                        # 使用隱藏的方式儲存原欄位名稱
                        if f'unified_name_{group_idx}' not in st.session_state:
                            st.session_state[f'unified_name_{group_idx}'] = col_name
                group_idx += 1

    st.divider()
    st.subheader('步驟 3: 選擇合併方式')

    # 如果沒有範本，需要建立 unified_mapping_preview
    if not has_template:
        # 預先建立 unified_mapping（用於顯示合併鍵選項）
        unified_mapping_preview = {}
        group_idx = 0
        for standard_name, similar_cols in column_groups.items():
            if len(similar_cols) > 1:
                unified_name = st.session_state.get(f'unified_name_{group_idx}', standard_name)
            else:
                map_option = st.session_state.get(f'map_option_{group_idx}', '保持原欄位名稱')
                if map_option == '對應到其他欄位':
                    unified_name = st.session_state.get(f'unified_name_{group_idx}', standard_name)
                else:
                    unified_name = standard_name
            group_idx += 1
            for col in similar_cols:
                unified_mapping_preview[col] = unified_name
    else:
        # 使用範本的欄位對應
        unified_mapping_preview = unified_mapping

    # 從範本取得預設值（如果有的話）
    template_merge_method = None
    template_merge_key = None
    template_merge_how = None
    template_remove_dup = True

    if has_template:
        template_config = template_info['config']
        template_merge_method = template_config.get('merge_method', '垂直堆疊')
        template_merge_key = template_config.get('merge_key')
        template_merge_how = template_config.get('merge_how', 'outer')
        template_remove_dup = template_config.get('remove_duplicates', True)

    col1, col2 = st.columns(2)
    with col1:
        merge_method_index = 0 if template_merge_method == '垂直堆疊' else 1 if template_merge_method else 0
        merge_method = st.radio(
            '合併方式',
            ['垂直堆疊', '依 Key 合併'],
            index=merge_method_index,
            help='垂直堆疊：將所有資料上下疊加｜依 Key 合併：根據共同欄位橫向合併'
        )

    with col2:
        if merge_method == '依 Key 合併':
            unified_cols = sorted(set(unified_mapping_preview.values()))
            # 從範本找到預設的 merge_key index
            default_key_index = 0
            if template_merge_key and template_merge_key in unified_cols:
                default_key_index = unified_cols.index(template_merge_key)

            merge_key = st.selectbox(
                '選擇合併鍵（Key）',
                options=unified_cols,
                index=default_key_index,
                help='通常選擇「工號」、「員工編號」等唯一識別欄位'
            )

            # 從範本找到預設的 merge_how index
            how_options = ['outer', 'inner', 'left']
            default_how_index = 0
            if template_merge_how and template_merge_how in how_options:
                default_how_index = how_options.index(template_merge_how)

            merge_how = st.selectbox(
                '合併方式',
                options=how_options,
                index=default_how_index,
                format_func=lambda x: {
                    'outer': '外部合併（保留所有資料）',
                    'inner': '內部合併（只保留共同資料）',
                    'left': '左側合併（以第一個檔案為主）'
                }[x]
            )
        else:
            merge_key = None
            merge_how = None

    remove_duplicates = st.checkbox('移除重複資料', value=template_remove_dup)

    st.divider()
    st.subheader('步驟 4: 執行合併')

    if st.button('🚀 執行合併', type='primary', width='stretch'):
        try:
            with st.spinner('正在合併資料...'):
                # 建立欄位對應表（從 session_state 讀取用戶輸入）
                unified_mapping = {}
                group_idx = 0
                for standard_name, similar_cols in column_groups.items():
                    if len(similar_cols) > 1:
                        # 有相似欄位群組，從 session_state 讀取用戶輸入
                        unified_name = st.session_state.get(f'unified_name_{group_idx}', standard_name)
                    else:
                        # 單獨欄位，檢查用戶選擇的處理方式
                        map_option = st.session_state.get(f'map_option_{group_idx}', '保持原欄位名稱')
                        if map_option == '對應到其他欄位':
                            unified_name = st.session_state.get(f'unified_name_{group_idx}', standard_name)
                        else:
                            unified_name = standard_name

                    group_idx += 1

                    for col in similar_cols:
                        unified_mapping[col] = unified_name

                # 即時處理：重命名並清理所有 DataFrame
                cleaned_dfs = []
                for filename, df in dataframes.items():
                    # 建立新的欄位名稱列表和對應的欄位索引
                    new_columns = []
                    col_positions = []
                    seen = set()

                    for idx, col in enumerate(df.columns):
                        # 取得統一名稱
                        unified_col = unified_mapping.get(col, col)

                        # 只保留第一次出現的欄位名稱
                        if unified_col not in seen:
                            new_columns.append(unified_col)
                            col_positions.append(idx)
                            seen.add(unified_col)

                    # 使用 iloc 根據位置索引選擇欄位，避免列名重複問題
                    df_clean = df.iloc[:, col_positions].copy()
                    df_clean.columns = new_columns
                    df_clean = df_clean.reset_index(drop=True)

                    cleaned_dfs.append(df_clean)

                # 執行合併
                if merge_method == '垂直堆疊':
                    result_df = pd.concat(cleaned_dfs, ignore_index=True, sort=False)

                elif merge_method == '依 Key 合併':
                    result_df = cleaned_dfs[0].copy()

                    for df in cleaned_dfs[1:]:
                        if merge_key not in result_df.columns or merge_key not in df.columns:
                            st.error(f'合併鍵「{merge_key}」在某些檔案中不存在！')
                            st.stop()

                        result_df = pd.merge(
                            result_df,
                            df,
                            on=merge_key,
                            how=merge_how,
                            suffixes=('', '_dup')
                        )

                    # 移除重複欄位
                    dup_cols = [col for col in result_df.columns if col.endswith('_dup')]
                    if dup_cols:
                        st.info(f'移除重複欄位: {", ".join(dup_cols)}')
                        result_df = result_df.drop(columns=dup_cols)

                # 移除重複資料
                if remove_duplicates:
                    before_count = len(result_df)
                    result_df = result_df.drop_duplicates(keep='first')
                    after_count = len(result_df)
                    if before_count > after_count:
                        st.info(f'已移除 {before_count - after_count} 筆重複資料')

                st.success(f'✅ 合併完成！共 {len(result_df)} 筆資料，{len(result_df.columns)} 個欄位')

                st.write('**合併結果預覽:**')
                st.caption('💡 點擊右上角全螢幕按鈕可查看完整資料')
                st.dataframe(result_df, width='stretch')

                # 匯出 Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    result_df.to_excel(writer, index=False, sheet_name='合併結果')
                output.seek(0)

                st.download_button(
                    label='📥 下載合併結果（Excel）',
                    data=output,
                    file_name=f'merged_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    width='stretch'
                )

                # ========== 儲存為範本 ==========
                st.divider()
                st.subheader('💾 儲存此流程為範本')
                st.info('儲存後，下次遇到相同格式的報表時可以直接套用，無需重新設定')

                with st.form('save_template_form'):
                    template_name = st.text_input('範本名稱', placeholder='例如：月報整合流程')
                    template_desc = st.text_area('範本說明（選填）', placeholder='簡短描述此範本的用途')

                    submitted = st.form_submit_button('💾 儲存範本', type='primary')

                    if submitted:
                        if not template_name.strip():
                            st.error('請輸入範本名稱')
                        else:
                            # 建立範本設定
                            template_config = {
                                'column_mapping': unified_mapping,
                                'merge_method': merge_method,
                                'merge_key': merge_key if merge_method == '依 Key 合併' else None,
                                'merge_how': merge_how if merge_method == '依 Key 合併' else None,
                                'remove_duplicates': remove_duplicates
                            }

                            result = template_db.save_template(
                                module='M1',
                                template_name=template_name.strip(),
                                config=template_config,
                                description=template_desc.strip() if template_desc.strip() else None
                            )

                            if result['success']:
                                st.success(result['message'])
                                st.balloons()
                            else:
                                st.error(result['message'])

        except Exception as e:
            st.error(f'合併失敗: {str(e)}')
            import traceback
            st.code(traceback.format_exc())
