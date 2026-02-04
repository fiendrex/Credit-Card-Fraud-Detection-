#!/usr/bin/env python
"""
Quick test to verify the app will run correctly
"""
import os
import sys
import pickle

print("\n" + "=" * 70)
print("TESTING FRAUD DETECTION APP")
print("=" * 70)

# Test 1: Load all pickle files
print("\n[TEST 1] Loading all model files...")
try:
    with open("fraud_detection_models/logistic_regression_model.pkl", "rb") as f:
        lr_model = pickle.load(f)
    print("  ✓ Logistic Regression model")
    
    with open("fraud_detection_models/random_forest_model.pkl", "rb") as f:
        rf_model = pickle.load(f)
    print("  ✓ Random Forest model")
    
    with open("fraud_detection_models/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    print("  ✓ Scaler")
    
    with open("fraud_detection_models/model_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    print("  ✓ Metadata")
    
    with open("fraud_detection_models/feature_names.pkl", "rb") as f:
        features = pickle.load(f)
    print("  ✓ Feature names")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Test 2: Verify metadata has all required keys
print("\n[TEST 2] Checking metadata keys...")
required_keys = ['lr_auc', 'rf_auc', 'lr_f1', 'rf_f1', 'test_fraud_rate', 
                'train_fraud_rate', 'num_features', 'train_samples', 'test_samples']

missing = []
for key in required_keys:
    if key in metadata:
        print(f"  ✓ {key}: {metadata[key]}")
    else:
        print(f"  ✗ {key}: MISSING")
        missing.append(key)

if missing:
    print(f"\n✗ Missing keys: {missing}")
    sys.exit(1)

# Test 3: Test model predictions
print("\n[TEST 3] Testing model predictions...")
try:
    import numpy as np
    
    # Create dummy transaction (30 features)
    test_input = np.random.randn(1, 30)
    test_scaled = scaler.transform(test_input)
    
    lr_pred = lr_model.predict(test_scaled)
    lr_prob = lr_model.predict_proba(test_scaled)
    print(f"  ✓ LR Prediction: {lr_pred[0]} (prob: {lr_prob[0][1]:.4f})")
    
    rf_pred = rf_model.predict(test_scaled)
    rf_prob = rf_model.predict_proba(test_scaled)
    print(f"  ✓ RF Prediction: {rf_pred[0]} (prob: {rf_prob[0][1]:.4f})")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Test 4: Import Streamlit
print("\n[TEST 4] Checking Streamlit...")
try:
    import streamlit
    print(f"  ✓ Streamlit {streamlit.__version__}")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    print("  Install: pip install streamlit")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - READY TO LAUNCH!")
print("=" * 70)
print("\nLaunching app in 2 seconds...\n")

import time
time.sleep(2)

# Launch app
import subprocess
result = subprocess.run([sys.executable, "-m", "streamlit", "run", "fraud_detection_app.py"])
sys.exit(result.returncode)
