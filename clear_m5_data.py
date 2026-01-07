# -*- coding: utf-8 -*-
"""
Clear Module 5 test data from single qualification database
Use this to reset before testing the import UI
"""

from core.db_manager import DBManager

print("=" * 60)
print("Clearing Module 5 Test Data")
print("=" * 60)

# Clear M5 single qualification database (contains all 4 tables)
print("\nClearing m5_qualification.db (all tables)...")
try:
    db = DBManager('m5_qualification')

    # Clear all tables in the single database
    tables = ['employees', 'performance', 'training', 'separation']
    for table in tables:
        print(f"  Clearing {table} table...")
        result = db.clear_all_data(table_name=table)
        if result:
            print(f"    + Successfully cleared {table} table")
        else:
            print(f"    - Failed to clear {table} table")

    print(f"\n  ✓ Successfully cleared m5_qualification.db")
except Exception as e:
    print(f"  - Error: {e}")

print("\n" + "=" * 60)
print("Database Reset Complete")
print("=" * 60)
print("\nAll M5 qualification data has been cleared from m5_qualification.db")
print("You can now test the import UI in the Streamlit app.")
print("\nNext steps:")
print("1. Run: streamlit run app.py")
print("2. Go to 'Qualification Checker' -> 'Data Import' tab")
print("3. Upload test files:")
print("   - test_m5_employee_master.xlsx")
print("   - test_m5_separation.xlsx")
print("   - test_m5_performance.xlsx")
print("   - test_m5_training.xlsx")
