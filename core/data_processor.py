# -*- coding: utf-8 -*-
import pandas as pd
from typing import List, Dict
from datetime import datetime

class DataProcessor:
    def __init__(self, df):
        self.df = df.copy()
        self.original_df = df.copy()
        self.history = []

    def detect_column_type(self, column):
        """Detect data type of a column"""
        if column not in self.df.columns:
            return 'unknown'

        sample = self.df[column].dropna().head(100)
        if len(sample) == 0:
            return 'empty'

        try:
            pd.to_datetime(sample)
            return 'datetime'
        except:
            pass

        try:
            pd.to_numeric(sample)
            return 'numeric'
        except:
            pass

        return 'string'

    def get_column_stats(self, column):
        """Get statistics for a column"""
        if column not in self.df.columns:
            return {}

        total = len(self.df)
        null_count = self.df[column].isna().sum()
        unique_count = self.df[column].nunique()
        dtype = self.detect_column_type(column)

        return {
            'total': total,
            'null_count': null_count,
            'null_percent': round(null_count / total * 100, 2) if total > 0 else 0,
            'unique_count': unique_count,
            'dtype': dtype
        }

    def apply_cleaning_step(self, step):
        action = step['action']
        column = step.get('column')

        self.history.append({
            'step': step,
            'before_shape': self.df.shape
        })

        if action == 'trim_whitespace' and column:
            self.df[column] = self.df[column].astype(str).str.strip()
        elif action == 'unify_date_format' and column:
            fmt = step.get('format', '%Y-%m-%d')
            self.df[column] = pd.to_datetime(self.df[column], errors='coerce').dt.strftime(fmt)
        elif action == 'remove_duplicates':
            subset = step.get('subset')
            keep = step.get('keep', 'first')
            self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        elif action == 'fill_na' and column:
            fill_value = step.get('value', '')
            self.df[column] = self.df[column].fillna(fill_value)
        elif action == 'rename_column' and column:
            new_name = step.get('new_name')
            if new_name:
                self.df = self.df.rename(columns={column: new_name})
        elif action == 'convert_type' and column:
            target_type = step.get('target_type', 'string')
            if target_type == 'numeric':
                self.df[column] = pd.to_numeric(self.df[column], errors='coerce')
            elif target_type == 'datetime':
                self.df[column] = pd.to_datetime(self.df[column], errors='coerce')
            elif target_type == 'string':
                self.df[column] = self.df[column].astype(str)
        elif action == 'drop_column' and column:
            self.df = self.df.drop(columns=[column])

        return self.df

    def reset(self):
        """Reset to original dataframe"""
        self.df = self.original_df.copy()
        self.history = []
        return self.df
