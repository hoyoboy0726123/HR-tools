# -*- coding: utf-8 -*-
"""
Phase 2 功能測試
測試報表合併器和到期提醒系統
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.file_handler import FileHandler
import pandas as pd


def test_report_merger():
    """測試報表合併功能"""
    print('\\n=== Testing Report Merger ===')
    
    test_files = [
        'tests/test_data/test_m1_report_A.xlsx',
        'tests/test_data/test_m1_report_B.xlsx',
        'tests/test_data/test_m1_report_C.xlsx'
    ]
    
    loaded = 0
    dataframes = []
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                df = FileHandler.load_file(file_path)
                dataframes.append(df)
                print(f'OK - Loaded {os.path.basename(file_path)}: {df.shape}')
                loaded += 1
            except Exception as e:
                print(f'ERROR - {file_path}: {e}')
    
    print(f'OK - Loaded {loaded}/{len(test_files)} files')
    
    if dataframes:
        merged = pd.concat(dataframes, ignore_index=True)
        print(f'OK - Merged result: {merged.shape}')
        print(f'   Column count: {len(merged.columns)}')

        before = len(merged)
        merged = merged.drop_duplicates(keep='first')
        after = len(merged)
        print(f'OK - Removed {before - after} duplicates')
    

def test_reminder_system():
    """測試提醒系統"""
    print('\\n=== Testing Reminder System ===')
    
    from core.db_manager import DBManager
    from datetime import datetime, timedelta
    
    db = DBManager('data/test_reminders.db')
    
    # Test adding reminder
    today = datetime.now()
    due_date = (today + timedelta(days=90)).strftime('%Y-%m-%d')
    
    success = db.add_reminder(
        'E001',
        '試用期滿',
        today.strftime('%Y-%m-%d'),
        due_date,
        '測試提醒'
    )
    
    if success:
        print('OK - Added reminder')
    else:
        print('ERROR - Failed to add reminder')
    
    # Test querying reminders
    start = today.strftime('%Y-%m-%d')
    end = (today + timedelta(days=180)).strftime('%Y-%m-%d')
    
    reminders = db.get_reminders_by_range(start, end)
    print(f'OK - Found {len(reminders)} reminders')


if __name__ == '__main__':
    print('='*50)
    print('Testing HR Data Tool - Phase 2')
    print('='*50)
    
    try:
        test_report_merger()
        test_reminder_system()
        
        print('\\n' + '='*50)
        print('OK - All Phase 2 tests completed!')
        print('='*50)
    except Exception as e:
        print(f'\\nERROR - Test failed: {e}')
        import traceback
        traceback.print_exc()
