# -*- coding: utf-8 -*-
import pandas as pd
import os

class FileHandler:
    @staticmethod
    def load_file(file_path, **kwargs):
        # Handle Streamlit UploadedFile objects
        if hasattr(file_path, 'name'):
            # It's a Streamlit UploadedFile object
            file_name = file_path.name
            ext = os.path.splitext(file_name)[1].lower()

            if ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path, **kwargs)
            elif ext == '.csv':
                try:
                    return pd.read_csv(file_path, encoding='utf-8', **kwargs)
                except UnicodeDecodeError:
                    return pd.read_csv(file_path, encoding='big5', **kwargs)
            raise ValueError(f"Unsupported file type: {ext}")
        else:
            # It's a regular file path string
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path, **kwargs)
            elif ext == '.csv':
                try:
                    return pd.read_csv(file_path, encoding='utf-8', **kwargs)
                except UnicodeDecodeError:
                    return pd.read_csv(file_path, encoding='big5', **kwargs)
            raise ValueError(f"Unsupported file type: {ext}")
