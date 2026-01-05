import sqlite3

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM offers')
total = cursor.fetchone()[0]
print(f'Total offres dans la base: {total}')

cursor.execute('SELECT status, COUNT(*) FROM offers GROUP BY status')
print('\nPar statut:')
for status, count in cursor.fetchall():
    print(f'  {status}: {count}')

cursor.execute('SELECT COUNT(*) FROM offers WHERE year_stats = 2024')
count_2024 = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM offers WHERE year_stats = 2025')
count_2025 = cursor.fetchone()[0]

print(f'\n2024: {count_2024}')
print(f'2025: {count_2025}')

conn.close()
