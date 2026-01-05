# -*- coding: utf-8 -*-
"""
Phase 3 功能測試
測試資料清洗器和員工查詢模組
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_processor import DataProcessor
from core.db_manager import DBManager
from utils.file_handler import FileHandler
import pandas as pd


def test_data_cleaner():
    """測試資料清洗器"""
    print('\n=== Testing Data Cleaner ===')

    test_file = 'tests/test_data/test_m2_dirty_data.xlsx'

    if os.path.exists(test_file):
        try:
            df = FileHandler.load_file(test_file)
            print(f'OK - Loaded dirty data: {df.shape}')

            processor = DataProcessor(df)

            col_count = min(3, len(df.columns))
            for i in range(col_count):
                col = df.columns[i]
                stats = processor.get_column_stats(col)
                print(f'OK - Column analysis: {stats["dtype"]}, null: {stats["null_count"]}')

            processor.apply_cleaning_step({
                'action': 'trim_whitespace',
                'column': df.columns[0]
            })
            print('OK - Applied trim whitespace')

            processor.apply_cleaning_step({
                'action': 'remove_duplicates',
                'subset': None,
                'keep': 'first'
            })
            print(f'OK - Removed duplicates: {processor.df.shape}')

            processor.reset()
            print(f'OK - Reset to original: {processor.df.shape}')

        except Exception as e:
            print(f'ERROR - Data cleaner test failed: {e}')
    else:
        print(f'WARN - Test file not found: {test_file}')


def test_employee_dashboard():
    """測試員工查詢模組"""
    print('\n=== Testing Employee Dashboard ===')

    db = DBManager('data/test_hr_phase3.db')

    db.add_employee('E001', 'Alice Wang', None, 'IT', '2020-01-15')
    db.add_employee('E002', 'Bob Chen', None, 'HR', '2021-03-20')
    print('OK - Added test employees')

    results = db.search_employee('Alice')
    print(f'OK - Search found {len(results)} records')

    test_perf_file = 'tests/test_data/test_m4_performance.xlsx'
    if os.path.exists(test_perf_file):
        df = FileHandler.load_file(test_perf_file)
        result = db.import_performance_data(df)
        if result.get('success'):
            print(f'OK - Imported {result.get("count")} performance records')
        else:
            print(f'ERROR - Failed to import performance data')

    test_training_file = 'tests/test_data/test_m4_training.xlsx'
    if os.path.exists(test_training_file):
        df = FileHandler.load_file(test_training_file)
        result = db.import_training_data(df)
        if result.get('success'):
            print(f'OK - Imported {result.get("count")} training records')
        else:
            print(f'ERROR - Failed to import training data')

    perf = db.get_performance_history('E001')
    print(f'OK - Performance history: {len(perf)} records')

    training = db.get_training_history('E001')
    print(f'OK - Training history: {len(training)} records')


if __name__ == '__main__':
    print('='*50)
    print('Testing HR Data Tool - Phase 3')
    print('='*50)

    try:
        test_data_cleaner()
        test_employee_dashboard()

        print('\n' + '='*50)
        print('OK - All Phase 3 tests completed!')
        print('='*50)
    except Exception as e:
        print(f'\nERROR - Test failed: {e}')
        import traceback
        traceback.print_exc()
