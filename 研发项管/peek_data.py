import pandas as pd
import sys

try:
    # Try to read the Excel file
    df = pd.read_excel('12月-1月工时去休假.xls')
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Check for required fields
    required_fields = ['花费人', '标题', '备注', '类别', '项目', '来源', '环节', '月份', '工作量']
    missing = [f for f in required_fields if f not in df.columns]
    if missing:
        print("\nMissing fields:", missing)
    else:
        print("\nAll required fields present.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
