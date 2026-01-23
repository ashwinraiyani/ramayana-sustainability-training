#!/usr/bin/env python3
"""Setup Script - One-command setup for Ramayana Sustainability Training Platform"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(command, description, use_shell=True):
    """Run shell command with error handling"""
    print(f"⏳ {description}...")
    try:
        if isinstance(command, list):
            subprocess.run(command, check=True, shell=False)
        else:
            subprocess.run(command, check=True, shell=use_shell)
        print(f"✅ {description} completed!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}\n")
        return False

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_env_file():
    """Create .env from .env.example"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("⏳ Creating .env file...")
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created!")
            print("⚠️  Please update .env with your credentials!\n")
        else:
            print("❌ .env.example not found!")
            return False
    else:
        print("ℹ️  .env file already exists.\n")
    return True

def setup():
    """Main setup function"""
    print_header("Ramayana Sustainability Training Platform Setup")
    
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment using list format to handle spaces in path
    if not os.path.exists('venv'):
        python_exe = sys.executable
        if not run_command([python_exe, '-m', 'venv', 'venv'], "Creating virtual environment", use_shell=False):
            sys.exit(1)
    else:
        print("ℹ️  Virtual environment exists.\n")
    
    # Determine OS-specific commands
    if sys.platform == "win32":
        pip_cmd = os.path.join('venv', 'Scripts', 'pip.exe')
        python_cmd = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        pip_cmd = os.path.join('venv', 'bin', 'pip')
        python_cmd = os.path.join('venv', 'bin', 'python')
    
    # Install dependencies using list format
    if not run_command([pip_cmd, 'install', '--upgrade', 'pip'], "Upgrading pip", use_shell=False):
        sys.exit(1)
    
    if not run_command([pip_cmd, 'install', '-r', 'requirements.txt'], "Installing dependencies", use_shell=False):
        sys.exit(1)
    
    # Create .env
    if not create_env_file():
        sys.exit(1)
    
    # Create directories
    print("⏳ Creating directories...")
    for dir_name in ['logs', 'uploads', 'temp']:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Directories created!\n")
    
    # Ask about database initialization
    response = input("Initialize database now? (y/n): ")
    if response.lower() == 'y':
        run_command([python_cmd, 'scripts/init_database.py'], "Initializing database", use_shell=False)
    
    print_header("Setup Completed Successfully!")
    print("\n📝 Next Steps:\n")
    print("1. Update .env with your credentials")
    print(f"2. Start backend: {python_cmd} -m uvicorn backend.main:app --reload")
    print(f"3. Start frontend: {python_cmd} -m streamlit run frontend/app.py\n")
    print("="*60)

if __name__ == '__main__':
    try:
        setup()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)