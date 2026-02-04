#!/usr/bin/env python
"""
Diagnostic script to identify the exact error
"""
import os
import sys

print("=" * 70)
print("FRAUD DETECTION SYSTEM - DIAGNOSTIC TEST")
print("=" * 70)

# Step 1: Check directory
print("\n[1] Checking current directory...")
print(f"    Current dir: {os.getcwd()}")
print(f"    Files: {os.listdir('.')[:10]}")

# Step 2: Check models exist
print("\n[2] Checking models directory...")
models_dir = "fraud_detection_models"
if os.path.exists(models_dir):
    files = os.listdir(models_dir)
    print(f"    ✓ Models directory exists")
    print(f"    ✓ Files: {files}")
else:
    print(f"    ✗ Models directory not found!")
    sys.exit(1)

# Step 3: Check imports
print("\n[3] Testing imports...")
try:
    import streamlit
    print(f"    ✓ streamlit: {streamlit.__version__}")
except ImportError as e:
    print(f"    ✗ streamlit: {e}")

try:
    import pickle
    print(f"    ✓ pickle: available")
except ImportError as e:
    print(f"    ✗ pickle: {e}")

try:
    import pandas
    print(f"    ✓ pandas: {pandas.__version__}")
except ImportError as e:
    print(f"    ✗ pandas: {e}")

try:
    import numpy
    print(f"    ✓ numpy: {numpy.__version__}")
except ImportError as e:
    print(f"    ✗ numpy: {e}")

# Step 4: Load pickle files
print("\n[4] Testing model loading...")
import pickle

try:
    with open(f"{models_dir}/logistic_regression_model.pkl", "rb") as f:
        lr_model = pickle.load(f)
    print(f"    ✓ Loaded: logistic_regression_model")
except Exception as e:
    print(f"    ✗ Error loading LR model: {e}")
    sys.exit(1)

try:
    with open(f"{models_dir}/random_forest_model.pkl", "rb") as f:
        rf_model = pickle.load(f)
    print(f"    ✓ Loaded: random_forest_model")
except Exception as e:
    print(f"    ✗ Error loading RF model: {e}")
    sys.exit(1)

try:
    with open(f"{models_dir}/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    print(f"    ✓ Loaded: scaler")
except Exception as e:
    print(f"    ✗ Error loading scaler: {e}")
    sys.exit(1)

try:
    with open(f"{models_dir}/model_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    print(f"    ✓ Loaded: metadata")
    print(f"       - LR AUC: {metadata.get('lr_auc', 'N/A')}")
    print(f"       - RF AUC: {metadata.get('rf_auc', 'N/A')}")
except Exception as e:
    print(f"    ✗ Error loading metadata: {e}")
    sys.exit(1)

try:
    with open(f"{models_dir}/feature_names.pkl", "rb") as f:
        features = pickle.load(f)
    print(f"    ✓ Loaded: feature_names ({len(features)} features)")
except Exception as e:
    print(f"    ✗ Error loading features: {e}")
    sys.exit(1)

# Step 5: Test Streamlit import
print("\n[5] Testing Streamlit app import...")
try:
    with open("fraud_detection_app.py", "r") as f:
        app_code = f.read()
    print(f"    ✓ fraud_detection_app.py loaded ({len(app_code)} bytes)")
    
    # Check for syntax errors
    compile(app_code, "fraud_detection_app.py", "exec")
    print(f"    ✓ No syntax errors found")
except SyntaxError as e:
    print(f"    ✗ Syntax error in app: {e}")
    sys.exit(1)
except Exception as e:
    print(f"    ✗ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL DIAGNOSTICS PASSED!")
print("=" * 70)
print("\nReady to launch. Running: streamlit run fraud_detection_app.py")
print("\nPress Ctrl+C to stop the server\n")

# Launch streamlit
import subprocess
subprocess.run([sys.executable, "-m", "streamlit", "run", "fraud_detection_app.py"])
