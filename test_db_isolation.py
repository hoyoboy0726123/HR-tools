# -*- coding: utf-8 -*-
"""
Test Independent Database Architecture
Verify M4, M5, M6 modules use separate databases
"""

from core.db_manager import DBManager
import os

def test_database_isolation():
    print("="*80)
    print("Testing Independent Database Architecture")
    print("="*80)

    # Step 1: Create test data in M4 databases
    print("\n[1] Creating test data in M4 databases...")
    try:
        db_m4_emp = DBManager('m4_employees')
        db_m4_emp.add_employee('M4-001', 'M4 Employee', None, 'M4 Dept', '2025-01-01')

        db_m4_perf = DBManager('m4_performance')
        db_m4_perf.add_performance_record('M4-001', 2024, 'A', 90)

        print("  OK: M4 test data created")
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    # Step 2: Create test data in M5 databases
    print("\n[2] Creating test data in M5 databases...")
    try:
        db_m5_emp = DBManager('m5_employees')
        db_m5_emp.add_employee('M5-001', 'M5 Employee', 'A123456789', 'M5 Dept', '2025-01-02')

        db_m5_sep = DBManager('m5_separation')
        db_m5_sep.add_separation_record('M5-001', '2025-12-31', 'Voluntary', 'Personal', False)

        print("  OK: M5 test data created")
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    # Step 3: Create test data in M6 database
    print("\n[3] Creating test data in M6 database...")
    try:
        db_m6 = DBManager('m6_reminders')
        db_m6.add_employee('M6-001', 'M6 Employee', None, 'M6 Dept', '2025-01-03')
        db_m6.add_reminder('M6-001', 'M6 Employee', 'Probation', '2025-01-03', '2025-04-03', 'Test')

        print("  OK: M6 test data created")
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    # Step 4: Verify data isolation
    print("\n[4] Verifying data isolation...")
    try:
        # Check M4 only has M4-001
        db_m4_check = DBManager('m4_employees')
        m4_all = db_m4_check.get_all_employees()
        m4_ids = [emp['emp_id'] for emp in m4_all]

        # Check M5 only has M5-001
        db_m5_check = DBManager('m5_employees')
        m5_all = db_m5_check.get_all_employees()
        m5_ids = [emp['emp_id'] for emp in m5_all]

        # Check M6 only has M6-001
        db_m6_check = DBManager('m6_reminders')
        m6_all = db_m6_check.get_all_employees()
        m6_ids = [emp['emp_id'] for emp in m6_all]

        print(f"  M4 database contains: {m4_ids}")
        print(f"  M5 database contains: {m5_ids}")
        print(f"  M6 database contains: {m6_ids}")

        # Verify isolation
        isolation_ok = True
        if 'M5-001' in m4_ids or 'M6-001' in m4_ids:
            print("  ERROR: M4 can see other modules' data")
            isolation_ok = False
        if 'M4-001' in m5_ids or 'M6-001' in m5_ids:
            print("  ERROR: M5 can see other modules' data")
            isolation_ok = False
        if 'M4-001' in m6_ids or 'M5-001' in m6_ids:
            print("  ERROR: M6 can see other modules' data")
            isolation_ok = False

        if isolation_ok:
            print("  OK: Data isolation verified - modules are completely independent")

        return isolation_ok
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def check_database_files():
    print("\n[5] Checking database files...")
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print(f"  INFO: Data directory does not exist yet")
        return

    db_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.db')])
    print(f"  Found {len(db_files)} database files:")

    expected_new = ['m4_employees.db', 'm4_performance.db',
                    'm5_employees.db', 'm5_separation.db',
                    'm6_reminders.db']

    for db_file in db_files:
        db_path = os.path.join(data_dir, db_file)
        size = os.path.getsize(db_path)
        status = "NEW" if db_file in expected_new else "OLD"
        print(f"    [{status}] {db_file} ({size:,} bytes)")

if __name__ == '__main__':
    success = test_database_isolation()
    check_database_files()

    print("\n" + "="*80)
    if success:
        print("SUCCESS: Independent database architecture working correctly")
        print("="*80)
        print("\nSummary:")
        print("  - M4 Employee Dashboard uses m4_*.db")
        print("  - M5 Qualification Checker uses m5_*.db")
        print("  - M6 Reminder System uses m6_reminders.db")
        print("  - All modules are completely isolated")
    else:
        print("FAILED: Database isolation test failed")
        print("="*80)
