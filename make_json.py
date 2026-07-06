import sys
import json
from pathlib import Path

# Local calculation ke liye pandas import kar rahe hain
import pandas as pd
sys.modules['pd'] = pd

try:
    import builtins
    builtins.pd = pd  # Isse app.py ko global pd mil jayega
    
    from app import load_gene_catalog
    print("Pandas set ho gaya... data process ho raha hai (Badi file hai, 5-15 seconds lag sakte hain)...")
    
    catalog_data = load_gene_catalog()
    catalog_path = Path("static/gene_catalog.json")
    
    with open(catalog_path, "w") as f:
        json.dump(catalog_data, f)
        
    print("\n--- SUCCESS: static/gene_catalog.json BAN GAYI HAI! ---")
except Exception as e:
    print(f"Error aaya hai: {e}")

