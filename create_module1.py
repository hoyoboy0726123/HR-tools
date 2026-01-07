# Create Module 1: Report Merger
import os

code = """# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from core.column_matcher import ColumnMatcher
from utils.file_handler import FileHandler
import json
import os
from datetime import datetime
from io import BytesIO


def save_mapping_template(template_name, mapping_data):
    os.makedirs('data/templates/column_mappings', exist_ok=True)
    template_path = f'data/templates/column_mappings/{template_name}.json'
    template = {
        'name': template_name,
        'created_at': datetime.now().isoformat(),
        'mapping': mapping_data
    }
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    return True


def load_mapping_template(template_name):
    template_path = f'data/templates/column_mappings/{template_name}.json'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def list_mapping_templates():
    template_dir = 'data/templates/column_mappings'
    if os.path.exists(template_dir):
        return [f.replace('.json', '') for f in os.listdir(template_dir) if f.endswith('.json')]
    return []


def render():
    st.title("📊 報表合併器")
    st.markdown("整合多份欄位不統一的報表")
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    
    st.subheader("步驟 1: 上傳報表檔案")
    uploaded_files = st.file_uploader(
        "上傳 Excel 或 CSV 檔案 (可多選)",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        key='file_uploader'
    )
    
    if uploaded_files:
        dataframes = {}
        for file in uploaded_files:
            try:
                df = FileHandler.load_file(file)
                dataframes[file.name] = df
            except Exception as e:
                st.error(f"載入 {file.name} 失敗: {e}")
        
        st.session_state.uploaded_files = dataframes
        st.success(f"✅ 已載入 {len(dataframes)} 個檔案")
        
        for filename, df in dataframes.items():
            with st.expander(f"📄 {filename}"):
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("資料筆數", df.shape[0])
                    st.metric("欄位數量", df.shape[1])
                with col2:
                    st.write("**欄位列表:**")
                    st.write(", ".join(df.columns.tolist()))
                st.write("**資料預覽:**")
                st.dataframe(df.head(3), use_container_width=True)
        
        st.subheader("步驟 2: 選擇合併方式")
        merge_method = st.radio(
            "合併方式",
            ["垂直堆疊 (Union)", "依 Key 合併 (Join)"],
            help="垂直堆疊: 將所有報表上下合併"
        )
        
        if merge_method == "依 Key 合併 (Join)":
            all_cols = set(dataframes[list(dataframes.keys())[0]].columns)
            for df in dataframes.values():
                all_cols = all_cols.intersection(set(df.columns))
            if all_cols:
                key_column = st.selectbox("選擇合併鍵值欄位", list(all_cols))
                join_type = st.selectbox("合併類型", ["inner", "outer", "left"])
            else:
                st.warning("找不到共同欄位")
                key_column = None
                join_type = None
        
        remove_duplicates = st.checkbox("移除重複資料", value=True)
        
        st.subheader("步驟 3: 執行合併")
        if st.button("🔄 執行合併", type="primary", use_container_width=True):
            try:
                with st.spinner("正在合併資料..."):
                    if merge_method == "垂直堆疊 (Union)":
                        result_df = pd.concat(dataframes.values(), ignore_index=True)
                        if remove_duplicates:
                            before_count = len(result_df)
                            result_df = result_df.drop_duplicates(keep='first')
                            after_count = len(result_df)
                            st.info(f"已移除 {before_count - after_count} 筆重複資料")
                    else:
                        if key_column:
                            result_df = None
                            for filename, df in dataframes.items():
                                if result_df is None:
                                    result_df = df
                                else:
                                    result_df = pd.merge(result_df, df, on=key_column, how=join_type)
                        else:
                            st.error("請選擇合併鍵值欄位")
                            result_df = None
                    
                    if result_df is not None:
                        st.success(f"✅ 合併完成！共 {len(result_df)} 筆資料，{len(result_df.columns)} 個欄位")
                        st.write("**合併結果預覽:**")
                        st.dataframe(result_df.head(20), use_container_width=True)
                        
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            result_df.to_excel(writer, index=False, sheet_name='合併結果')
                        output.seek(0)
                        
                        st.download_button(
                            label="💾 下載 Excel 檔案",
                            data=output,
                            file_name=f"merged_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"合併失敗: {str(e)}")
    else:
        st.info("👆 請上傳至少一個檔案開始使用")
"""

with open('modules/m1_report_merger.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Created modules/m1_report_merger.py")
