
try:
    with open('temp_start_app_ref.bat', 'r', encoding='utf-16') as f:
        print(f.read())
except:
    try:
        with open('temp_start_app_ref.bat', 'r', encoding='utf-8') as f:
            print(f.read())
    except:
        with open('temp_start_app_ref.bat', 'r', encoding='cp1252') as f:
            print(f.read())
