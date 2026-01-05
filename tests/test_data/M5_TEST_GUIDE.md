# Module 5 (Qualification Checker) Test Data Guide

## Test Data Files

1. **test_m5_employee_master.xlsx** - 8 employee records
2. **test_m5_separation.xlsx** - 8 separation records
3. **test_m5_performance.xlsx** - 25 performance records
4. **test_m5_training.xlsx** - 51 training records
5. **test_m5_scenarios.xlsx** - 8 test scenario descriptions

## Test Scenarios

### Scenario 1: Auto-Approve (Clean Records)

**Test Case 1.1: 張志明**
- ID Number: `A123456789`
- Employee ID: E001
- Expected Result: **APPROVED**
- Reason: All checks PASS - good performance, voluntary separation, not blacklisted
- Performance: Average ~85-90 (A/B+ ratings)
- Separation: Voluntary (職涯發展)

**Test Case 1.2: 林美玲**
- ID Number: `B234567890`
- Employee ID: E002
- Expected Result: **APPROVED**
- Reason: Clean record with good performance history
- Performance: Consistently good
- Separation: Voluntary

**Test Case 1.3: John Chen**
- ID Number: `C345678901`
- Employee ID: E003
- Expected Result: **APPROVED**
- Reason: Clean record, no warnings
- Performance: Good ratings
- Separation: Voluntary

---

### Scenario 2: AI Review Recommended (Low Performance)

**Test Case 2.1: 王大明**
- ID Number: `D456789012`
- Employee ID: E004
- Expected Result: **REVIEW_REQUIRED**
- Reason: WARNING - has 2 low performance records (C/D), but later improved
- Performance:
  - First 2 years: C/D ratings (55-69 score)
  - Later: Improved to B (70-79 score)
- Separation: Voluntary
- AI Judgment: May recommend considering improvement trend

**Test Case 2.2: 李小華**
- ID Number: `E567890123`
- Employee ID: E005
- Expected Result: **REVIEW_REQUIRED**
- Reason: WARNING - low performance in early years
- Performance: Similar pattern to 王大明
- Separation: Voluntary
- AI Judgment: Should evaluate recent performance trend

---

### Scenario 3: Auto-Reject (Blacklisted)

**Test Case 3.1: 陳不良**
- ID Number: `F678901234`
- Employee ID: E006
- Expected Result: **REJECTED**
- Reason: FAIL - on blacklist due to serious policy violation
- Performance: Consistently poor (D/E ratings)
- Separation: Involuntary (開除 - serious violation)
- Blacklist: TRUE

**Test Case 3.2: 黃違規**
- ID Number: `G789012345`
- Employee ID: E007
- Expected Result: **REJECTED**
- Reason: FAIL - blacklisted for integrity issues
- Performance: Poor ratings
- Separation: Involuntary (資遣 - integrity issues)
- Blacklist: TRUE

---

### Scenario 4: AI Review (Involuntary Separation)

**Test Case 4.1: 劉被資遣**
- ID Number: `H890123456`
- Employee ID: E008
- Expected Result: **REVIEW_REQUIRED**
- Reason: WARNING - involuntary separation (layoff), but decent performance
- Performance: Average B/B+ ratings (72-82 score)
- Separation: Involuntary (資遣 - organizational restructuring)
- Blacklist: FALSE
- AI Judgment: Should consider if layoff was due to business needs vs performance

---

## How to Use Test Data

### Method 1: Import via Streamlit App

1. Start the app: `streamlit run app.py`
2. Navigate to each module (員工查詢, 資格檢核器)
3. Import the test data files manually:
   - Employee Query → Data Import → Upload test_m5_employee_master.xlsx
   - Continue for other data types

### Method 2: Run Automated Import

```bash
cd hr_data_tool
python tests/test_module5.py
```

This will automatically import all test data and run verification tests.

### Method 3: Quick Verification

```bash
cd hr_data_tool
python verify_m5_data.py
```

This verifies data is loaded and runs 3 sample checks.

---

## Testing in the App

1. Launch app: `streamlit run app.py`
2. Click "資格檢核器" (Qualification Checker)
3. Enter test credentials:

**Test Clean Approval:**
- Name: 張志明
- ID: A123456789
- Expected: ✅ APPROVED immediately

**Test Review Required:**
- Name: 王大明
- ID: D456789012
- Expected: ⚠️ REVIEW_REQUIRED with AI option

**Test Rejection:**
- Name: 陳不良
- ID: F678901234
- Expected: ❌ REJECTED (blacklisted)

---

## Data Summary

- Total Employees: 8
- Blacklisted: 2
- Performance Records: 25 (covering 3-4 years per employee)
- Training Records: 51 (3-8 courses per employee)
- Separation Records: 8 (all departed)

## Expected Test Results

- Auto-Approve: 3 cases (37.5%)
- Review Required: 3 cases (37.5%)
- Auto-Reject: 2 cases (25%)

This distribution demonstrates the AI cost-saving strategy:
- 37.5% auto-approve (no AI needed)
- 25% auto-reject (no AI needed)
- **Only 37.5% may need AI assistance**

---

## Regenerating Test Data

If you need to regenerate fresh test data:

```bash
cd hr_data_tool
python generate_m5_test_data.py
```

This will create new test files with randomized but realistic data.

---

## Notes

- ID numbers are hashed in the database for privacy
- Test data includes realistic Chinese names and departments
- Performance ratings use ASUS scale: A, B+, B, C, D, E
- Training hours range from 3-24 hours per course
- All separation dates are calculated based on hire dates
