import sys
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/deletion_requests.csv')

# Look for patterns that might be NOT_APPLICABLE:
# Access request, export request, update/rectification request, objection/opt-out, etc.
keywords_del = [
    'delete', 'deletion', 'erase', 'erasure', 'remove', 'removal', 'close',
    'supprimer', 'suppression', 'eliminar', 'eliminación', 'eliminacion',
    'löschen', 'löschung', 'cancellare', 'cancellazione', '削除',
    'exclusão', 'exclusao', 'excluir', 'effacer', 'schließen', 'chiudere',
    'apagar', 'verwijderen', 'usunięcie', 'usunąć', 'smazat', 'slet'
]

no_del_kw = []
for idx, r in df_req.iterrows():
    text = r['request_text'].lower()
    has_del = any(w in text for w in keywords_del)
    if not has_del:
        no_del_kw.append((r['case_id'], r['request_text']))

print(f"Total requests without basic deletion keywords: {len(no_del_kw)}")
with open(r'C:\Users\motup\.gemini\antigravity-ide\brain\d27db20e-39f1-414d-873b-8b6d6163c2d9\scratch\no_del_kw.txt', 'w', encoding='utf-8') as f:
    for c, t in no_del_kw:
        f.write(f"[{c}] {t}\n")

print("Saved to scratch/no_del_kw.txt")
