#!/usr/bin/env python
"""
Simple launcher for the Streamlit fraud detection app
Helps bypass terminal issues
"""
import os
import sys
import subprocess

def main():
    # Change to app directory
    app_dir = r"d:\credit card\archive (5)"
    os.chdir(app_dir)
    
    print("=" * 60)
    print("FRAUD DETECTION SYSTEM - STREAMLIT LAUNCHER")
    print("=" * 60)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print(f"✓ Streamlit is installed: {streamlit.__version__}")
    except ImportError:
        print("✗ Streamlit is not installed")
        print("  Run: pip install streamlit")
        sys.exit(1)
    
    # Check if fraud_detection_models directory exists
    models_dir = os.path.join(app_dir, "fraud_detection_models")
    if not os.path.exists(models_dir):
        print("✗ Models directory not found!")
        print(f"  Expected: {models_dir}")
        sys.exit(1)
    
    # Check for required pickle files
    required_files = [
        "logistic_regression_model.pkl",
        "random_forest_model.pkl",
        "scaler.pkl",
        "model_metadata.pkl",
        "feature_names.pkl"
    ]
    
    print(f"\n✓ Models directory found")
    missing = []
    for fname in required_files:
        fpath = os.path.join(models_dir, fname)
        if os.path.exists(fpath):
            size_mb = os.path.getsize(fpath) / (1024 * 1024)
            print(f"  ✓ {fname} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {fname} (MISSING)")
            missing.append(fname)
    
    if missing:
        print(f"\n✗ Missing required files: {missing}")
        print("  Please run the notebook Cell 14 to generate models")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("LAUNCHING STREAMLIT APP...")
    print("=" * 60)
    print("\nStreamlit will open in your browser at:")
    print("http://localhost:8501")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Launch streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "fraud_detection_app.py"
    ])

if __name__ == "__main__":
    main()
