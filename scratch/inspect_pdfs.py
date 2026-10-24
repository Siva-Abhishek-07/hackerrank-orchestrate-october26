import os

pdf_dir = 'dataset/evidence/documents'
for f in os.listdir(pdf_dir):
    if f.endswith('.pdf'):
        path = os.path.join(pdf_dir, f)
        print(f"PDF: {f} (size: {os.path.getsize(path)})")
        try:
            import pypdf
            reader = pypdf.PdfReader(path)
            print(f"  Pages: {len(reader.pages)}")
            for i, p in enumerate(reader.pages):
                print(f"  --- Page {i+1} ---")
                print(p.extract_text()[:400])
        except Exception as e:
            print(f"  pypdf error: {e}")
