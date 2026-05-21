# -*- coding: utf-8 -*-
import csv
import os

file_name = "my_applications.csv"
repaired_data = []

print("🔧 Initializing Data Integrity Repair Engine...")

if not os.path.exists(file_name):
    print(f"❌ Error: Cannot find {file_name}")
    exit()

with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Parse the header column
header = lines[0].strip().split(',')
repaired_data.append(header)

for idx, line in enumerate(lines[1:], start=2):
    if not line.strip():
        continue
    
    # Use individual line evaluation to preserve existing valid quotes
    try:
        row = next(csv.reader([line.strip()]))
    except Exception:
        row = line.strip().split(',')
        
    if len(row) == 5:
        repaired_data.append(row)
    elif len(row) > 5:
        # Merge all fields from index 4 onwards into a single Notes string
        repaired_row = [row[0], row[1], row[2], row[3], ", ".join(row[4:])]
        repaired_data.append(repaired_row)
        print(f"✅ Repaired line {idx}: Safely merged extra fields into Notes for '{row[0]}'")
    else:
        # Pad with empty fields if row is missing data columns
        while len(row) < 5:
            row.append("")
        repaired_data.append(row)

# Rewrite the sanitized rows back to file database
with open(file_name, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(repaired_data)

print("🎉 File structure successfully repaired! Your database is now valid.")