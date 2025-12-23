
import os
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

sys.path.append(os.getcwd())

print("Starting RAG Direct Test...", flush=True)

try:
    print("Importing RAGEngine...", flush=True)
    from models.rag_engine import get_rag_engine
    
    print("Getting RAGEngine instance (this triggers initialization)...", flush=True)
    rag = get_rag_engine()
    
    print("Ingesting (if needed)...", flush=True)
    if rag.vector_store._collection.count() == 0:
        print("Ingesting docs...", flush=True)
        rag.ingest_documents()
        
    print("Running Search...", flush=True)
    results = rag.search("sodium")
    print(f"Results found: {len(results)}", flush=True)
    print(results, flush=True)
    
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("Test Complete.", flush=True)
