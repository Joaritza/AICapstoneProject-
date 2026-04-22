"""Simple test to verify imports work for Streamlit UI."""

import sys
from pathlib import Path

# Add project root to path (same as app.py does)
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Testing imports...")

# Test 1: Core Python imports
try:
    import streamlit as st
    print("[OK] streamlit imported")
except Exception as e:
    print(f"[FAIL] streamlit: {e}")
    sys.exit(1)

# Test 2: Config imports
try:
    from config.logger_config import logger
    print("[OK] config.logger_config imported")
except Exception as e:
    print(f"[FAIL] config.logger_config: {e}")
    sys.exit(1)

# Test 3: Agent imports
try:
    from agents.router_agent import RouterAgent
    print("[OK] agents.router_agent imported")
except Exception as e:
    print(f"[FAIL] agents.router_agent: {e}")
    sys.exit(1)

# Test 4: Standard library
try:
    import json
    from datetime import datetime
    print("[OK] json and datetime imported")
except Exception as e:
    print(f"[FAIL] standard library: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS - All imports working!")
print("=" * 60)
print("\nStreamlit UI should now load correctly.")
print("Start with: streamlit run ui/app.py")
