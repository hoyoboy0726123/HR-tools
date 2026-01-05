# -*- coding: utf-8 -*-
"""
Phase 1 核心功能測試
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db_manager import DBManager
from core.column_matcher import ColumnMatcher
from core.data_processor import DataProcessor
from utils.file_handler import FileHandler
import pandas as pd


def test_database():
    """測試資料庫功能"""
    print('\n=== Testing Database ===')
    db = DBManager('data/test_hr_database.db')
    print('OK - Database initialized')

    success = db.add_employee('E001', 'John Doe', 'A123456789', 'IT', '2023-01-15')
    print(f'OK - Add employee: {"Success" if success else "Failed"}')

    results = db.search_employee('John')
    print(f'OK - Search: Found {len(results)} records')

    stats = db.get_database_stats()
    print(f'OK - Stats: {stats}')


def test_column_matcher():
    """測試欄位比對功能"""
    print('\n=== Testing Column Matcher ===')
    matcher = ColumnMatcher(threshold=0.6)

    col1 = ['Employee ID', 'Name', 'Department']
    col2 = ['EmpID', 'Name', 'Dept']

    matches = matcher.find_similar_columns(col1, col2)
    print(f'OK - Found {len(matches)} matches')
    for c1, (c2, score) in matches.items():
        print(f'  - {c1} ~ {c2} (score: {score:.2f})')


def test_data_processor():
    """測試資料處理功能"""
    print('\n=== Testing Data Processor ===')

    test_data = pd.DataFrame({
        'Employee ID': ['E001', 'E002', 'E003', 'E001'],
        'Name': ['  John  ', 'Jane', 'Bob', '  John  '],
        'Department': ['IT', 'HR', 'Finance', 'IT'],
        'Hire Date': ['2023/01/15', '2023-02-20', '2023.03.10', '2023/01/15']
    })

    processor = DataProcessor(test_data)
    print(f'OK - Original data: {processor.df.shape}')

    processor.apply_cleaning_step({'action': 'trim_whitespace', 'column': 'Name'})
    print('OK - Applied trim whitespace')

    processor.apply_cleaning_step({
        'action': 'unify_date_format',
        'column': 'Hire Date',
        'format': '%Y-%m-%d'
    })
    print('OK - Applied date formatting')

    processor.apply_cleaning_step({
        'action': 'remove_duplicates',
        'subset': ['Employee ID'],
        'keep': 'first'
    })
    print(f'OK - Removed duplicates: {processor.df.shape}')


def test_file_handler():
    """測試檔案處理功能"""
    print('\n=== Testing File Handler ===')

    test_files = [
        'tests/test_data/test_m4_employee_master.xlsx',
        'tests/test_data/test_m4_performance.xlsx'
    ]

    loaded_count = 0
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                df = FileHandler.load_file(file_path)
                print(f'OK - Loaded {os.path.basename(file_path)}: {df.shape}')
                loaded_count += 1
            except Exception as e:
                print(f'ERROR - Failed to load {file_path}: {e}')
        else:
            print(f'WARN - File not found: {file_path}')

    print(f'OK - Successfully loaded {loaded_count}/{len(test_files)} files')


if __name__ == '__main__':
    print('='*50)
    print('Testing HR Data Tool - Phase 1 Core')
    print('='*50)

    try:
        test_database()
        test_column_matcher()
        test_data_processor()
        test_file_handler()

        print('\n' + '='*50)
        print('OK - All Phase 1 tests completed!')
        print('='*50)
    except Exception as e:
        print(f'\nERROR - Test failed: {e}')
        import traceback
        traceback.print_exc()
