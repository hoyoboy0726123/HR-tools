# -*- coding: utf-8 -*-
"""
Module 5 (Qualification Checker) Integration Test
Tests all qualification check scenarios with realistic data
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from core.db_manager import DBManager
from modules.m5_qualification_check import QualificationChecker

print("=" * 70)
print("Module 5: Qualification Checker - Integration Test")
print("=" * 70)

# Step 1: Load test data
print("\n[Step 1] Loading test data...")
try:
    employees_df = pd.read_excel('tests/test_data/test_m5_employee_master.xlsx')
    separation_df = pd.read_excel('tests/test_data/test_m5_separation.xlsx')
    performance_df = pd.read_excel('tests/test_data/test_m5_performance.xlsx')
    training_df = pd.read_excel('tests/test_data/test_m5_training.xlsx')
    scenarios_df = pd.read_excel('tests/test_data/test_m5_scenarios.xlsx')

    print(f"+ Loaded {len(employees_df)} employees")
    print(f"+ Loaded {len(separation_df)} separation records")
    print(f"+ Loaded {len(performance_df)} performance records")
    print(f"+ Loaded {len(training_df)} training records")
    print(f"+ Loaded {len(scenarios_df)} test scenarios")
except Exception as e:
    print(f"- Failed to load test data: {e}")
    exit(1)

# Step 2: Import data to databases
print("\n[Step 2] Importing data to databases...")
try:
    db_employees = DBManager('employees')
    db_separation = DBManager('separation')
    db_performance = DBManager('performance')
    db_training = DBManager('training')

    # Import employees
    success_count = 0
    for _, row in employees_df.iterrows():
        result = db_employees.add_employee(
            emp_id=row['emp_id'],
            name=row['name'],
            id_number=row['id_number'],
            department=row.get('department', ''),
            hire_date=row.get('hire_date', ''),
            status=row.get('status', 'active')
        )
        if result:
            success_count += 1

    print(f"+ Imported {success_count}/{len(employees_df)} employees")

    # Import separation records
    success_count = 0
    for _, row in separation_df.iterrows():
        result = db_separation.add_separation_record(
            emp_id=row['emp_id'],
            separation_date=row['separation_date'],
            separation_type=row['separation_type'],
            reason=row['reason'],
            blacklist=row['blacklist']
        )
        if result:
            success_count += 1

    print(f"+ Imported {success_count}/{len(separation_df)} separation records")

    # Import performance records
    success_count = 0
    for _, row in performance_df.iterrows():
        result = db_performance.add_performance_record(
            emp_id=row['emp_id'],
            year=int(row['year']),
            rating=row['rating'],
            score=float(row['score'])
        )
        if result:
            success_count += 1

    print(f"+ Imported {success_count}/{len(performance_df)} performance records")

    # Import training records
    success_count = 0
    for _, row in training_df.iterrows():
        result = db_training.add_training_record(
            emp_id=row['emp_id'],
            course_name=row['course_name'],
            course_type=row['course_type'],
            hours=float(row['hours']),
            completion_date=row['completion_date']
        )
        if result:
            success_count += 1

    print(f"+ Imported {success_count}/{len(training_df)} training records")

except Exception as e:
    print(f"- Failed to import data: {e}")
    exit(1)

# Step 3: Initialize checker
print("\n[Step 3] Initializing Qualification Checker...")
try:
    checker = QualificationChecker()
    print("+ Checker initialized successfully")
except Exception as e:
    print(f"- Initialization failed: {e}")
    exit(1)

# Step 4: Run test scenarios
print("\n[Step 4] Running qualification check scenarios...")
print("-" * 70)

test_results = []

for idx, scenario in scenarios_df.iterrows():
    print(f"\n>>> {scenario['scenario']}")
    print(f"    Employee: {scenario['name']} ({scenario['emp_id']})")
    print(f"    ID Number: {scenario['id_number']}")
    print(f"    Expected: {scenario['expected_result']}")

    try:
        result = checker.check(scenario['name'], scenario['id_number'])

        # Display check results
        print(f"\n    Check Results:")
        for check in result['checks']:
            status_icon = {
                'PASS': '+',
                'WARNING': '!',
                'FAIL': 'x',
                'INFO': 'i'
            }.get(check['status'], '?')
            print(f"      [{status_icon}] {check['item']}: {check['status']}")
            print(f"          {check['detail']}")

        print(f"\n    Overall Status: {result['overall_status']}")

        # Verify result matches expected
        if result['overall_status'] == scenario['expected_result']:
            print(f"    Result: PASS (matches expected)")
            test_results.append({
                'scenario': scenario['scenario'],
                'emp_id': scenario['emp_id'],
                'expected': scenario['expected_result'],
                'actual': result['overall_status'],
                'status': 'PASS'
            })
        else:
            print(f"    Result: FAIL (expected {scenario['expected_result']}, got {result['overall_status']})")
            test_results.append({
                'scenario': scenario['scenario'],
                'emp_id': scenario['emp_id'],
                'expected': scenario['expected_result'],
                'actual': result['overall_status'],
                'status': 'FAIL'
            })

    except Exception as e:
        print(f"    Error: {e}")
        test_results.append({
            'scenario': scenario['scenario'],
            'emp_id': scenario['emp_id'],
            'expected': scenario['expected_result'],
            'actual': f'ERROR: {str(e)}',
            'status': 'ERROR'
        })

print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)

test_df = pd.DataFrame(test_results)
passed = len(test_df[test_df['status'] == 'PASS'])
failed = len(test_df[test_df['status'] == 'FAIL'])
errors = len(test_df[test_df['status'] == 'ERROR'])

print(f"\nTotal scenarios: {len(test_df)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Errors: {errors}")

if failed > 0 or errors > 0:
    print("\nFailed/Error scenarios:")
    for _, row in test_df[test_df['status'] != 'PASS'].iterrows():
        print(f"  - {row['scenario']} ({row['emp_id']})")
        print(f"    Expected: {row['expected']}, Got: {row['actual']}")

# Calculate pass rate
pass_rate = (passed / len(test_df)) * 100 if len(test_df) > 0 else 0
print(f"\nPass Rate: {pass_rate:.1f}%")

if pass_rate == 100:
    print("\n+++ ALL TESTS PASSED +++")
else:
    print(f"\n--- {failed + errors} TESTS FAILED ---")

# Save test results
test_df.to_excel('tests/test_data/test_m5_results.xlsx', index=False)
print(f"\nTest results saved to: tests/test_data/test_m5_results.xlsx")

print("\n" + "=" * 70)
print("Module 5 Integration Test Complete")
print("=" * 70)
