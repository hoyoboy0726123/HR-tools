# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from core.column_matcher import ColumnMatcher
from core.db_manager_multiuser import DBManagerMultiUser
from utils.file_handler import FileHandler
from datetime import datetime
from io import BytesIO


def render():
    st.title('報表合併器')
    st.markdown('整合多份欄位不統一的報表，智慧對齊欄位')

    # 取得當前登入用戶的 user_id
    user_id = st.session_state.user_info['user_id']

    # 初始化 uploader_id 用於清除上傳元件
    if 'uploader_id' not in st.session_state:
        st.session_state.uploader_id = 0

    # 初始化範本資料庫（支援多用戶）
    template_db = DBManagerMultiUser('workflow_templates', user_id=user_id)

    # ========== 範本管理區 ==========
    st.divider()
    with st.expander('📁 流程範本管理', expanded=False):
        tab_new, tab_load, tab_manage = st.tabs(['新建流程', '載入範本', '管理範本'])

        with tab_new:
            st.info('選擇此選項以建立新的合併流程（不使用範本）')
            if 'loaded_template' in st.session_state and st.session_state.loaded_template is not None:
                if st.button('✨ 清除當前範本，開始新建流程', type='primary'):
                    st.session_state.loaded_template = None
                    # 遞增 uploader_id 以清除檔案
                    st.session_state.uploader_id += 1
                    # 同時清除合併狀態
                    if 'merge_executed' in st.session_state:
                        st.session_state.merge_executed = False
                    st.success('已切換回新建流程模式，檔案已清除')
                    st.rerun()
            else:
                st.success('✅ 目前已處於新建流程模式')

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
                                # 遞增 uploader_id 以清除檔案
                                st.session_state.uploader_id += 1
                                # 清除先前的合併結果
                                if 'merge_executed' in st.session_state:
                                    st.session_state.merge_executed = False
                                st.success(f"✅ 已載入範本「{template['template_name']}」")
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

    # 檢查是否有載入的範本並立即顯示
    has_template = 'loaded_template' in st.session_state and st.session_state.loaded_template is not None

    if has_template:
        template_info = st.session_state.loaded_template
        template_mapping = template_info['config'].get('column_mapping', {})
        mapping_count = len(set(template_mapping.values()))
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info(f"📁 已載入範本：**{template_info['template_name']}** | {template_info.get('description', '')} | 包含 {mapping_count} 個欄位對應")
        with col2:
            if st.button('❌ 取消使用', help='回到新建流程模式'):
                st.session_state.loaded_template = None
                st.session_state.uploader_id += 1
                if 'merge_executed' in st.session_state:
                    st.session_state.merge_executed = False
                st.rerun()

    st.divider()
    st.subheader('步驟 1: 上傳報表檔案')
    uploaded_files = st.file_uploader(
        '上傳 Excel 或 CSV 檔案 (可多選)',
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        key=f"file_uploader_{st.session_state.uploader_id}"
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

    st.divider()
    st.subheader('步驟 2: 智慧欄位對齊')

    # 初始化手動拆分紀錄
    if 'split_columns' not in st.session_state:
        st.session_state.split_columns = set()

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

        # 優先處理被使用者拆出的欄位，確保它們不進入自動群組
        for col in all_col_list:
            if col in st.session_state.split_columns:
                column_groups[col] = [col]
                processed.add(col)

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
        st.info('請確認以下欄位對應是否正確，您可以修改「統一欄位名稱」。若歸類錯誤，請點擊「❌ 拆分此群組」。')

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

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text_input(
                            '統一欄位名稱',
                            value=standard_name,
                            key=f'unified_name_{group_idx}'
                        )
                    with col2:
                        st.write("") # 調整垂直對齊
                        st.write("")
                        if st.button('❌ 拆分此群組', key=f'split_btn_{group_idx}'):
                            for c in similar_cols:
                                st.session_state.split_columns.add(c)
                            st.rerun()
                group_idx += 1
            else:
                # 顯示單獨欄位，讓用戶可以選擇對應到哪個欄位
                col_name = similar_cols[0]
                is_split = col_name in st.session_state.split_columns
                expander_label = f'📌 手動對應: {col_name}' if is_split else f'📌 單獨欄位: {col_name}'
                
                with st.expander(expander_label, expanded=is_split):
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
                    
                    if is_split:
                        if st.button('🔄 恢復自動群組', key=f'restore_btn_{group_idx}'):
                            st.session_state.split_columns.remove(col_name)
                            st.rerun()
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
                        unified_name = st.session_state.get(f'unified_name_{group_idx}', standard_name)
                    else:
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
                    new_columns = []
                    col_positions = []
                    seen = set()
                    for idx, col in enumerate(df.columns):
                        unified_col = unified_mapping.get(col, col)
                        if unified_col not in seen:
                            new_columns.append(unified_col)
                            col_positions.append(idx)
                            seen.add(unified_col)
                    df_clean = df.iloc[:, col_positions].copy()
                    df_clean.columns = new_columns
                    cleaned_dfs.append(df_clean.reset_index(drop=True))

                # 執行合併
                if merge_method == '垂直堆疊':
                    result_df = pd.concat(cleaned_dfs, ignore_index=True, sort=False)
                elif merge_method == '依 Key 合併':
                    result_df = cleaned_dfs[0].copy()
                    for df in cleaned_dfs[1:]:
                        if merge_key not in result_df.columns or merge_key not in df.columns:
                            st.error(f'合併鍵「{merge_key}」在某些檔案中不存在！')
                            st.stop()
                        result_df = pd.merge(result_df, df, on=merge_key, how=merge_how, suffixes=('', '_dup'))
                    dup_cols = [col for col in result_df.columns if col.endswith('_dup')]
                    if dup_cols:
                        result_df = result_df.drop(columns=dup_cols)

                if remove_duplicates:
                    result_df = result_df.drop_duplicates(keep='first')

                # 將結果與設定存入 session_state 以供區塊外使用
                st.session_state.last_merge_result = result_df
                st.session_state.last_merge_config = {
                    'column_mapping': unified_mapping,
                    'merge_method': merge_method,
                    'merge_key': merge_key if merge_method == '依 Key 合併' else None,
                    'merge_how': merge_how if merge_method == '依 Key 合併' else None,
                    'remove_duplicates': remove_duplicates
                }
                st.session_state.merge_executed = True
                st.rerun()

        except Exception as e:
            st.error(f'合併失敗: {str(e)}')

    # ========== 合併結果與儲存範本區塊 (在按鈕外) ==========
    if st.session_state.get('merge_executed'):
        result_df = st.session_state.last_merge_result
        st.success(f'✅ 合併完成！共 {len(result_df)} 筆資料，{len(result_df.columns)} 個欄位')
        st.write('**合併結果預覽:**')
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

        st.divider()
        st.subheader('💾 儲存此流程為範本')
        st.info('儲存後，下次遇到相同格式的報表時可以直接套用')

        with st.form('save_template_form'):
            template_name = st.text_input('範本名稱', placeholder='例如：月報整合流程')
            template_desc = st.text_area('範本說明（選填）', placeholder='簡短描述此範本的用途')
            submitted = st.form_submit_button('💾 儲存範本', type='primary')

            if submitted:
                if not template_name.strip():
                    st.error('請輸入範本名稱')
                else:
                    result = template_db.save_template(
                        module='M1',
                        template_name=template_name.strip(),
                        config=st.session_state.last_merge_config,
                        description=template_desc.strip() if template_desc.strip() else None
                    )
                    if result['success']:
                        st.toast(f"✅ {result['message']}")
                        st.success(result['message'])
                        st.balloons()
                        # 延遲一下下讓使用者看到氣球，然後重新整理頁面
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(result['message'])

