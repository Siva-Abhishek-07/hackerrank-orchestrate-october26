import sqlite3, os

sql_path = 'dataset/evidence/databases/customer_data_inventory_20260916.sql'
tmpdb = 'C:/Temp/test_ev93.db'
os.makedirs('C:/Temp', exist_ok=True)
if os.path.exists(tmpdb):
    os.remove(tmpdb)
conn = sqlite3.connect(tmpdb)
with open(sql_path, 'r', encoding='utf-8', errors='replace') as f:
    script = f.read()
conn.executescript(script)
conn.commit()

# List tables
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])

for tbl in ['customer_profiles', 'backup_restore_entries', 'customer_search_documents', 'customer_analytics_profiles', 'support_records', 'connector_subscriptions']:
    try:
        rows = conn.execute(f'SELECT * FROM {tbl} LIMIT 3').fetchall()
        cols = [c[0] for c in conn.execute(f'PRAGMA table_info({tbl})').fetchall()]
        cnt = conn.execute(f'SELECT COUNT(*) FROM {tbl}').fetchone()[0]
        print(f'\n{tbl} (total={cnt}):')
        for row in rows[:2]:
            print(' ', dict(zip(cols, row)))
    except Exception as e:
        print(f'{tbl}: error {e}')

conn.close()
