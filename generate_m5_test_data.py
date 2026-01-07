# -*- coding: utf-8 -*-
"""
Generate comprehensive test data for Module 5: Qualification Checker
Creates realistic employee data for testing all scenarios
"""

import pandas as pd
from datetime import datetime, timedelta
import random

print("Generating Module 5 test data...")

# Scenario 1: Clean candidates (should auto-approve)
clean_employees = pd.DataFrame([
    {
        'emp_id': 'E001',
        'name': '張志明',
        'id_number': 'A123456789',
        'department': '研發部',
        'hire_date': '2018-01-15',
        'status': '離職'
    },
    {
        'emp_id': 'E002',
        'name': '林美玲',
        'id_number': 'B234567890',
        'department': '行銷部',
        'hire_date': '2019-03-20',
        'status': '離職'
    },
    {
        'emp_id': 'E003',
        'name': 'John Chen',
        'id_number': 'C345678901',
        'department': 'IT部',
        'hire_date': '2020-06-10',
        'status': '離職'
    }
])

# Scenario 2: Warning candidates (low performance)
warning_employees = pd.DataFrame([
    {
        'emp_id': 'E004',
        'name': '王大明',
        'id_number': 'D456789012',
        'department': '業務部',
        'hire_date': '2017-08-05',
        'status': '離職'
    },
    {
        'emp_id': 'E005',
        'name': '李小華',
        'id_number': 'E567890123',
        'department': '客服部',
        'hire_date': '2019-11-15',
        'status': '離職'
    }
])

# Scenario 3: Blacklist candidates (should reject)
blacklist_employees = pd.DataFrame([
    {
        'emp_id': 'E006',
        'name': '陳不良',
        'id_number': 'F678901234',
        'department': '財務部',
        'hire_date': '2016-05-10',
        'status': '離職'
    },
    {
        'emp_id': 'E007',
        'name': '黃違規',
        'id_number': 'G789012345',
        'department': '人資部',
        'hire_date': '2015-09-20',
        'status': '離職'
    }
])

# Scenario 4: Involuntary separation (warning)
involuntary_employees = pd.DataFrame([
    {
        'emp_id': 'E008',
        'name': '劉被資遣',
        'id_number': 'H890123456',
        'department': '製造部',
        'hire_date': '2018-12-01',
        'status': '離職'
    }
])

# Combine all employees
all_employees = pd.concat([
    clean_employees,
    warning_employees,
    blacklist_employees,
    involuntary_employees
], ignore_index=True)

# Save employee master data
all_employees.to_excel('tests/test_data/test_m5_employee_master.xlsx', index=False)
print(f"+ Created test_m5_employee_master.xlsx ({len(all_employees)} records)")

# Generate separation records
separation_records = []

# Clean separations (voluntary)
for _, emp in clean_employees.iterrows():
    separation_records.append({
        'emp_id': emp['emp_id'],
        'separation_date': (datetime.strptime(emp['hire_date'], '%Y-%m-%d') + timedelta(days=random.randint(365*2, 365*5))).strftime('%Y-%m-%d'),
        'separation_type': '自願離職',
        'reason': random.choice(['職涯發展', '家庭因素', '進修深造', '轉換跑道']),
        'blacklist': False
    })

# Warning separations (voluntary but had issues)
for _, emp in warning_employees.iterrows():
    separation_records.append({
        'emp_id': emp['emp_id'],
        'separation_date': (datetime.strptime(emp['hire_date'], '%Y-%m-%d') + timedelta(days=random.randint(365, 365*3))).strftime('%Y-%m-%d'),
        'separation_type': '自願離職',
        'reason': random.choice(['工作壓力', '薪資考量', '職涯規劃']),
        'blacklist': False
    })

# Blacklist separations (involuntary + blacklisted)
for _, emp in blacklist_employees.iterrows():
    separation_records.append({
        'emp_id': emp['emp_id'],
        'separation_date': (datetime.strptime(emp['hire_date'], '%Y-%m-%d') + timedelta(days=random.randint(180, 730))).strftime('%Y-%m-%d'),
        'separation_type': random.choice(['開除', '資遣']),
        'reason': random.choice(['嚴重違反公司規定', '績效不佳經改善無效', '職場不當行為', '誠信問題']),
        'blacklist': True
    })

# Involuntary separation (not blacklisted)
for _, emp in involuntary_employees.iterrows():
    separation_records.append({
        'emp_id': emp['emp_id'],
        'separation_date': (datetime.strptime(emp['hire_date'], '%Y-%m-%d') + timedelta(days=random.randint(365, 365*2))).strftime('%Y-%m-%d'),
        'separation_type': '資遣',
        'reason': '組織調整',
        'blacklist': False
    })

separation_df = pd.DataFrame(separation_records)
separation_df.to_excel('tests/test_data/test_m5_separation.xlsx', index=False)
print(f"+ Created test_m5_separation.xlsx ({len(separation_df)} records)")

# Generate performance records
performance_records = []

# Clean employees - good performance
for _, emp in clean_employees.iterrows():
    base_year = int(emp['hire_date'][:4])
    for i in range(4):
        year = base_year + i
        performance_records.append({
            'emp_id': emp['emp_id'],
            'year': year,
            'rating': random.choice(['A', 'A', 'B+', 'B']),
            'score': random.randint(80, 95)
        })

# Warning employees - has low performance
for _, emp in warning_employees.iterrows():
    base_year = int(emp['hire_date'][:4])
    for i in range(3):
        year = base_year + i
        if i < 2:
            # First 2 years: low performance
            performance_records.append({
                'emp_id': emp['emp_id'],
                'year': year,
                'rating': random.choice(['C', 'D', 'C']),
                'score': random.randint(55, 69)
            })
        else:
            # Later improved
            performance_records.append({
                'emp_id': emp['emp_id'],
                'year': year,
                'rating': 'B',
                'score': random.randint(70, 79)
            })

# Blacklist employees - consistently poor
for _, emp in blacklist_employees.iterrows():
    base_year = int(emp['hire_date'][:4])
    for i in range(2):
        year = base_year + i
        performance_records.append({
            'emp_id': emp['emp_id'],
            'year': year,
            'rating': random.choice(['D', 'E', 'C']),
            'score': random.randint(45, 65)
        })

# Involuntary separation - average performance
for _, emp in involuntary_employees.iterrows():
    base_year = int(emp['hire_date'][:4])
    for i in range(3):
        year = base_year + i
        performance_records.append({
            'emp_id': emp['emp_id'],
            'year': year,
            'rating': random.choice(['B', 'B+', 'B']),
            'score': random.randint(72, 82)
        })

performance_df = pd.DataFrame(performance_records)
performance_df.to_excel('tests/test_data/test_m5_performance.xlsx', index=False)
print(f"+ Created test_m5_performance.xlsx ({len(performance_df)} records)")

# Generate training records
training_records = []

courses = [
    '新人訓練', '職業安全衛生', '資訊安全',
    '專業技能培訓', '管理技能訓練', '語言學習',
    '產品知識', '客戶服務', '專案管理'
]

for _, emp in all_employees.iterrows():
    num_courses = random.randint(3, 8)
    base_date = datetime.strptime(emp['hire_date'], '%Y-%m-%d')

    for i in range(num_courses):
        course_date = base_date + timedelta(days=random.randint(30, 1000))
        training_records.append({
            'emp_id': emp['emp_id'],
            'course_name': random.choice(courses),
            'course_type': random.choice(['必修', '必修', '選修']),
            'hours': random.choice([3, 6, 8, 16, 24]),
            'completion_date': course_date.strftime('%Y-%m-%d')
        })

training_df = pd.DataFrame(training_records)
training_df.to_excel('tests/test_data/test_m5_training.xlsx', index=False)
print(f"+ Created test_m5_training.xlsx ({len(training_df)} records)")

# Generate test scenarios summary
scenarios = pd.DataFrame([
    {
        'scenario': 'Scenario 1: Auto-Approve',
        'emp_id': 'E001',
        'name': '張志明',
        'id_number': 'A123456789',
        'expected_result': 'APPROVED',
        'reason': 'All checks PASS - good performance, voluntary separation, not blacklisted'
    },
    {
        'scenario': 'Scenario 1: Auto-Approve',
        'emp_id': 'E002',
        'name': '林美玲',
        'id_number': 'B234567890',
        'expected_result': 'APPROVED',
        'reason': 'All checks PASS - good performance history'
    },
    {
        'scenario': 'Scenario 1: Auto-Approve',
        'emp_id': 'E003',
        'name': 'John Chen',
        'id_number': 'C345678901',
        'expected_result': 'APPROVED',
        'reason': 'All checks PASS - clean record'
    },
    {
        'scenario': 'Scenario 2: AI Review Recommended',
        'emp_id': 'E004',
        'name': '王大明',
        'id_number': 'D456789012',
        'expected_result': 'REVIEW_REQUIRED',
        'reason': 'WARNING - has 2 low performance records (C/D), but later improved'
    },
    {
        'scenario': 'Scenario 2: AI Review Recommended',
        'emp_id': 'E005',
        'name': '李小華',
        'id_number': 'E567890123',
        'expected_result': 'REVIEW_REQUIRED',
        'reason': 'WARNING - low performance in early years'
    },
    {
        'scenario': 'Scenario 3: Auto-Reject (Blacklist)',
        'emp_id': 'E006',
        'name': '陳不良',
        'id_number': 'F678901234',
        'expected_result': 'REJECTED',
        'reason': 'FAIL - on blacklist due to serious policy violation'
    },
    {
        'scenario': 'Scenario 3: Auto-Reject (Blacklist)',
        'emp_id': 'E007',
        'name': '黃違規',
        'id_number': 'G789012345',
        'expected_result': 'REJECTED',
        'reason': 'FAIL - blacklisted for integrity issues'
    },
    {
        'scenario': 'Scenario 4: AI Review (Involuntary Sep)',
        'emp_id': 'E008',
        'name': '劉被資遣',
        'id_number': 'H890123456',
        'expected_result': 'REVIEW_REQUIRED',
        'reason': 'WARNING - involuntary separation (layoff), but decent performance'
    }
])

scenarios.to_excel('tests/test_data/test_m5_scenarios.xlsx', index=False)
print(f"+ Created test_m5_scenarios.xlsx ({len(scenarios)} test scenarios)")

print("\n" + "=" * 60)
print("Module 5 test data generation complete!")
print("=" * 60)
print("\nGenerated files:")
print("1. test_m5_employee_master.xlsx - Employee basic data")
print("2. test_m5_separation.xlsx - Separation records")
print("3. test_m5_performance.xlsx - Performance history")
print("4. test_m5_training.xlsx - Training records")
print("5. test_m5_scenarios.xlsx - Test scenario guide")
print("\nTest scenarios:")
print("- 3 auto-approve cases (clean records)")
print("- 2 AI review cases (low performance)")
print("- 2 auto-reject cases (blacklisted)")
print("- 1 AI review case (involuntary separation)")
print("\nNext step: Import these files into the databases to run tests")
