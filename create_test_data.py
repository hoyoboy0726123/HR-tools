# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import random

# 創建測試資料：2025年10-12月到職的員工（試用期3個月後在2026年1-3月到期）
data = []

names = ['王小明', '李小華', '張小芳', '陳小強', '林小美', '黃小龍',
         '周小花', '吳小明', '鄭小玲', '劉小宇', '蔡小文', '楊小婷']
depts = ['研發部', '業務部', '人資部', '財務部', '行政部']
positions = ['工程師', '業務專員', '專員', '主任', '經理']

# 10月到職（試用期滿：2026/01）
base_date_oct = datetime(2025, 10, 1)
for i in range(4):
    hire_date = base_date_oct + timedelta(days=random.randint(0, 29))
    data.append({
        '工號': f'E{202510+i:03d}',
        '姓名': names[i],
        '部門': depts[i % 5],
        '職稱': positions[i % 5],
        '到職日': hire_date.strftime('%Y-%m-%d'),
        '試用期月數': 3,
        '直屬主管': 'M001',
        '聯絡分機': f'#{1000+i}',
        '備註': '2025年10月新進'
    })

# 11月到職（試用期滿：2026/02）
base_date_nov = datetime(2025, 11, 1)
for i in range(4, 8):
    hire_date = base_date_nov + timedelta(days=random.randint(0, 29))
    data.append({
        '工號': f'E{202510+i:03d}',
        '姓名': names[i],
        '部門': depts[i % 5],
        '職稱': positions[i % 5],
        '到職日': hire_date.strftime('%Y-%m-%d'),
        '試用期月數': 3,
        '直屬主管': 'M002',
        '聯絡分機': f'#{1000+i}',
        '備註': '2025年11月新進'
    })

# 12月到職（試用期滿：2026/03）
base_date_dec = datetime(2025, 12, 1)
for i in range(8, 12):
    hire_date = base_date_dec + timedelta(days=random.randint(0, 29))
    data.append({
        '工號': f'E{202510+i:03d}',
        '姓名': names[i],
        '部門': depts[i % 5],
        '職稱': positions[i % 5],
        '到職日': hire_date.strftime('%Y-%m-%d'),
        '試用期月數': 3,
        '直屬主管': 'M003',
        '聯絡分機': f'#{1000+i}',
        '備註': '2025年12月新進'
    })

df = pd.DataFrame(data)

# 存檔
df.to_excel('test_data/test_m6_new_hires_2025Q4.xlsx', index=False)

print("Test file created: test_data/test_m6_new_hires_2025Q4.xlsx")
print(f"Total records: {len(df)}")
print("\nData preview:")
for _, row in df.iterrows():
    hire_dt = pd.to_datetime(row['到職日'])
    due_dt = hire_dt + pd.DateOffset(months=3)
    print(f"{row['工號']} | Hire: {row['到職日']} | Due: {due_dt.strftime('%Y-%m-%d')}")
