"""
Setup & Configuration Script for Fraud Detection Deployment
Run this script to prepare the environment and start the app
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python 3.8+ required (found {version.major}.{version.minor})")
        return False

def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ {requirements_file} not found")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def verify_models():
    """Verify that all model files exist"""
    print_header("Verifying Model Files")
    
    models_dir = Path("models")
    required_files = [
        "logistic_regression_model.pkl",
        "random_forest_model.pkl",
        "scaler.pkl",
        "model_metadata.json",
        "feature_names.pkl"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = models_dir / file
        if file_path.exists():
            size = file_path.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"✅ {file} ({size:.2f} MB)")
        else:
            print(f"❌ {file} - NOT FOUND")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  Some model files are missing!")
        print("   Please run main.ipynb to train and save models.")
        return False
    
    return True

def create_folders():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    folders = ["models", "data", "logs"]
    
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"✅ {folder}/ created/verified")

def display_launch_info():
    """Display information about launching the app"""
    print_header("Ready to Launch! 🚀")
    
    print("""
    To start the Fraud Detection Web App, run:
    
    ┌────────────────────────────────────────────────┐
    │  streamlit run fraud_detection_app.py          │
    └────────────────────────────────────────────────┘
    
    The app will open automatically at:
    
    🌐 http://localhost:8501
    
    """)

def main():
    """Main setup function"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║   🔒 FRAUD DETECTION SYSTEM - DEPLOYMENT SETUP 🔒    ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    # Run setup checks
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", create_folders),
        ("Model Files", verify_models),
        ("Dependencies", install_dependencies),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print_header("Setup Summary")
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ All checks passed! System is ready for deployment.")
        display_launch_info()
        
        # Ask if user wants to launch app
        response = input("\n🚀 Launch the app now? (y/n): ").strip().lower()
        if response == 'y':
            print("\nStarting Streamlit app...")
            os.system("streamlit run fraud_detection_app.py")
    else:
        print("\n❌ Some checks failed. Please fix issues and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
