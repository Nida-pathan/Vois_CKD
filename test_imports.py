
import sys
# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("Testing Imports...", flush=True)

try:
    print("1. Importing langchain...", flush=True)
    import langchain
    print("   [OK] langchain imported", flush=True)
except ImportError as e:
    print(f"   [FAIL] langchain failed: {e}", flush=True)

try:
    print("2. Importing langchain_community...", flush=True)
    import langchain_community
    print("   [OK] langchain_community imported", flush=True)
except ImportError as e:
    print(f"   [FAIL] langchain_community failed: {e}", flush=True)

try:
    print("3. Importing torch...", flush=True)
    import torch
    print("   [OK] torch imported", flush=True)
except ImportError as e:
    print(f"   [FAIL] torch failed: {e}", flush=True)

try:
    print("4. Importing sentence_transformers...", flush=True)
    import sentence_transformers
    print("   [OK] sentence_transformers imported", flush=True)
except ImportError as e:
    print(f"   [FAIL] sentence_transformers failed: {e}", flush=True)

try:
    print("5. Importing HuggingFaceEmbeddings...", flush=True)
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("   [OK] HuggingFaceEmbeddings imported", flush=True)
except ImportError as e:
    print(f"   [FAIL] HuggingFaceEmbeddings failed: {e}", flush=True)

print("Import Test Complete.", flush=True)
