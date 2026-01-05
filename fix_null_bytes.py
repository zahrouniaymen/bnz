"""
Detect and fix null bytes in Python files
"""
import os

files_to_check = [
    'backend/models.py',
    'backend/schemas.py',
    'backend/main.py',
    'backend/analytics_enrichment.py'
]

print("Checking for null bytes in Python files...")
print()

for filepath in files_to_check:
    if not os.path.exists(filepath):
        print(f"[SKIP] {filepath} - file not found")
        continue
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        if b'\x00' in content:
            print(f"[FOUND] {filepath} - contains null bytes!")
            
            # Remove null bytes
            cleaned = content.replace(b'\x00', b'')
            
            # Write back
            with open(filepath, 'wb') as f:
                f.write(cleaned)
            
            print(f"[FIXED] {filepath} - null bytes removed")
        else:
            print(f"[OK] {filepath} - no null bytes")
    
    except Exception as e:
        print(f"[ERROR] {filepath} - {e}")

print("\nDone!")
