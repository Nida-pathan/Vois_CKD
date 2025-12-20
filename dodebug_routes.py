from app import app
import sys

print("Listing all registered routes:")
for rule in app.url_map.iter_rules():
    if 'chatbot' in str(rule):
        print(f"FOUND: {rule} -> {rule.endpoint}")

print("\nDone listing routes.")
