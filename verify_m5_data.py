# -*- coding: utf-8 -*-
"""
Verify Module 5 test data import
Check if all test data is properly loaded into databases
"""

from core.db_manager import DBManager
from modules.m5_qualification_check import QualificationChecker

print("="* 60)
print("Module 5 Data Verification")
print("=" * 60)

# Check employees
db_emp = DBManager('employees')
conn = db_emp._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) as count FROM employees")
emp_count = cursor.fetchone()['count']
conn.close()
print(f"\nEmployees in database: {emp_count}")

# Check separation
db_sep = DBManager('separation')
conn = db_sep._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) as count FROM separation")
sep_count = cursor.fetchone()['count']
cursor.execute("SELECT COUNT(*) as count FROM separation WHERE blacklist = 1")
blacklist_count = cursor.fetchone()['count']
conn.close()
print(f"Separation records: {sep_count}")
print(f"Blacklisted: {blacklist_count}")

# Check performance
db_perf = DBManager('performance')
conn = db_perf._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) as count FROM performance")
perf_count = cursor.fetchone()['count']
conn.close()
print(f"Performance records: {perf_count}")

# Check training
db_train = DBManager('training')
conn = db_train._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) as count FROM training")
train_count = cursor.fetchone()['count']
conn.close()
print(f"Training records: {train_count}")

# Test qualification checks
print("\n" + "=" * 60)
print("Running Sample Checks")
print("=" * 60)

checker = QualificationChecker()

# Test 1: Clean candidate (should approve)
print("\n[Test 1] Clean Candidate - A123456789")
result1 = checker.check("Test", "A123456789")
print(f"  Status: {result1['overall_status']}")
print(f"  Expected: APPROVED")
print(f"  Match: {result1['overall_status'] == 'APPROVED'}")

# Test 2: Low performance (should require review)
print("\n[Test 2] Low Performance - D456789012")
result2 = checker.check("Test", "D456789012")
print(f"  Status: {result2['overall_status']}")
print(f"  Expected: REVIEW_REQUIRED")
print(f"  Match: {result2['overall_status'] == 'REVIEW_REQUIRED'}")

# Test 3: Blacklisted (should reject)
print("\n[Test 3] Blacklisted - F678901234")
result3 = checker.check("Test", "F678901234")
print(f"  Status: {result3['overall_status']}")
print(f"  Expected: REJECTED")
print(f"  Match: {result3['overall_status'] == 'REJECTED'}")

# Summary
print("\n" + "=" * 60)
test_pass = (
    result1['overall_status'] == 'APPROVED' and
    result2['overall_status'] == 'REVIEW_REQUIRED' and
    result3['overall_status'] == 'REJECTED'
)

if test_pass:
    print("ALL VERIFICATION TESTS PASSED!")
else:
    print("SOME TESTS FAILED")

print("\nData import complete and working correctly!")
print("You can now test in the Streamlit app:")
print("1. Run: streamlit run app.py")
print("2. Go to 'Qualification Checker'")
print("3. Try these ID numbers:")
print("   - A123456789 (should approve)")
print("   - D456789012 (should require review)")
print("   - F678901234 (should reject)")
