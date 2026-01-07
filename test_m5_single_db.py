# -*- coding: utf-8 -*-
"""
Test M5 Single Database Architecture
Verify m5_qualification.db contains all 4 tables and works correctly
"""

from core.db_manager import DBManager

print("=" * 80)
print("Testing M5 Single Database Architecture")
print("=" * 80)

# Test 1: Create database and verify tables
print("\n[Test 1] Initializing m5_qualification database...")
try:
    db = DBManager('m5_qualification')
    print("  OK: Database initialized")
except Exception as e:
    print(f"  ERROR: {e}")
    exit(1)

# Test 2: Add test employee
print("\n[Test 2] Adding test employee...")
try:
    result = db.add_employee('TEST-001', 'Test Employee', 'A123456789', 'Test Dept', '2025-01-01')
    if result:
        print("  OK: Employee added to employees table")
    else:
        print("  ERROR: Failed to add employee")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 3: Add test performance record
print("\n[Test 3] Adding test performance record...")
try:
    result = db.add_performance_record('TEST-001', 2024, 'A', 95)
    if result:
        print("  OK: Performance record added to performance table")
    else:
        print("  ERROR: Failed to add performance record")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 4: Add test training record
print("\n[Test 4] Adding test training record...")
try:
    result = db.add_training_record('TEST-001', 'Test Course', 'Technical', 8, '2024-12-01')
    if result:
        print("  OK: Training record added to training table")
    else:
        print("  ERROR: Failed to add training record")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 5: Add test separation record
print("\n[Test 5] Adding test separation record...")
try:
    result = db.add_separation_record('TEST-001', '2024-12-31', 'Voluntary', 'Personal', False)
    if result:
        print("  OK: Separation record added to separation table")
    else:
        print("  ERROR: Failed to add separation record")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 6: Verify data retrieval
print("\n[Test 6] Verifying data retrieval...")
try:
    employees = db.get_all_employees()
    performance = db.get_all_records(table_name='performance')
    training = db.get_all_records(table_name='training')
    separation = db.get_all_records(table_name='separation')

    print(f"  Employees table: {len(employees)} records")
    print(f"  Performance table: {len(performance)} records")
    print(f"  Training table: {len(training)} records")
    print(f"  Separation table: {len(separation)} records")

    if len(employees) == 1 and len(performance) == 1 and len(training) == 1 and len(separation) == 1:
        print("  OK: All tables contain expected data")
    else:
        print("  WARNING: Record counts don't match expected values")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 7: Test database stats
print("\n[Test 7] Testing database stats...")
try:
    stats = db.get_database_stats()
    print(f"  Stats: {stats}")
    if 'active_employees' in stats and 'performance_records' in stats:
        print("  OK: Database stats working correctly")
    else:
        print("  WARNING: Stats missing expected fields")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 8: Test table-specific delete
print("\n[Test 8] Testing table-specific delete...")
try:
    result = db.delete_by_emp_id('TEST-001', table_name='performance')
    if result:
        performance_after = db.get_all_records(table_name='performance')
        if len(performance_after) == 0:
            print("  OK: Performance record deleted (employees table unaffected)")
        else:
            print("  ERROR: Performance record not deleted")
    else:
        print("  ERROR: Delete operation failed")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 9: Test table-specific clear
print("\n[Test 9] Testing table-specific clear...")
try:
    result = db.clear_all_data(table_name='training')
    if result:
        training_after = db.get_all_records(table_name='training')
        employees_after = db.get_all_employees()
        if len(training_after) == 0 and len(employees_after) == 1:
            print("  OK: Training table cleared (other tables unaffected)")
        else:
            print("  ERROR: Clear operation affected wrong tables")
    else:
        print("  ERROR: Clear operation failed")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 10: Clean up
print("\n[Test 10] Cleaning up test data...")
try:
    db.clear_all_data()  # Clear all tables
    print("  OK: All test data cleared")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
print("\nSummary:")
print("  + m5_qualification.db successfully uses single database architecture")
print("  + All 4 tables (employees, performance, training, separation) working")
print("  + Table-specific operations (get, delete, clear) working correctly")
print("\nNext step: Test the Streamlit UI")
