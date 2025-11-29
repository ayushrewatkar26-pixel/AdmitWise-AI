#!/usr/bin/env python3
"""
AdmitWise AI - Complete Installation Script
This script installs ALL dependencies for the entire project in one go.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("=" * 70)
    print("🚀 AdmitWise AI - Complete Installation Script")
    print("=" * 70)
    print("This will install ALL dependencies for:")
    print("  • Backend (Python Flask + AI + Database)")
    print("  • Frontend (React + Node.js)")
    print("  • Chatbot (Gemini AI + Hybrid RAG)")
    print("=" * 70)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_system_requirements():
    """Check system requirements."""
    print("\n🔍 Checking system requirements...")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    # Check npm (try multiple paths for Windows)
    npm_paths = ['npm', r'C:\Program Files\nodejs\npm.cmd', r'C:\Program Files\nodejs\npm']
    npm_found = False
    
    for npm_path in npm_paths:
        try:
            result = subprocess.run([npm_path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm: {result.stdout.strip()} (found at {npm_path})")
                npm_found = True
                break
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    
    if not npm_found:
        print("❌ npm not found")
        return False
    
    return True

def install_python_dependencies():
    """Install all Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    print("   This includes: Flask, AI, Database, OCR, ML libraries...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        print("✅ pip upgraded")
        
        # Install all requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], check=True)
        print("✅ All Python dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Python dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def install_node_dependencies():
    """Install all Node.js dependencies."""
    print("\n📦 Installing Node.js dependencies...")
    print("   This includes: React, Axios, Tailwind CSS...")
    
    try:
        frontend_dir = os.path.join(os.getcwd(), 'frontend')
        if not os.path.exists(frontend_dir):
            print("❌ Frontend directory not found")
            return False
        
        # Change to frontend directory
        original_dir = os.getcwd()
        os.chdir(frontend_dir)
        
        # Try multiple npm paths
        npm_paths = ['npm', r'C:\Program Files\nodejs\npm.cmd', r'C:\Program Files\nodejs\npm']
        npm_installed = False
        
        for npm_path in npm_paths:
            try:
                subprocess.run([npm_path, 'install'], check=True)
                print("✅ All Node.js dependencies installed successfully")
                npm_installed = True
                break
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        
        # Return to original directory
        os.chdir(original_dir)
        
        if not npm_installed:
            print("❌ Could not install Node.js dependencies")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_environment_files():
    """Create environment configuration files."""
    print("\n🔧 Creating environment configuration files...")
    
    try:
        # Create backend .env template
        backend_dir = os.path.join(os.getcwd(), 'backend')
        env_template = os.path.join(backend_dir, '.env.template')
        
        env_content = """# ======================================================
# AdmitWise AI Environment Configuration
# ======================================================
# Copy this file to .env and update with your actual values

# ======================================================
# Database Configuration
# ======================================================
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=cutoff_db
DB_PORT=3306

# ======================================================
# Gemini AI Configuration
# ======================================================
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# ======================================================
# Flask Configuration
# ======================================================
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=your_secret_key_here
"""
        
        with open(env_template, 'w') as f:
            f.write(env_content)
        
        print("✅ Environment template created at backend/.env.template")
        
        # Check if .env already exists
        env_file = os.path.join(backend_dir, '.env')
        if os.path.exists(env_file):
            print("ℹ️  .env file already exists - keeping existing configuration")
        else:
            print("ℹ️  Please copy .env.template to .env and update with your values")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating environment files: {e}")
        return False

def verify_installation():
    """Verify that all components are properly installed."""
    print("\n🔍 Verifying installation...")
    
    try:
        # Test Python imports
        test_imports = [
            'flask', 'pandas', 'numpy', 'xgboost', 
            'sklearn', 'cv2', 'pytesseract', 'fitz',
            'mysql.connector', 'google.generativeai', 'dotenv'
        ]
        
        failed_imports = []
        for module in test_imports:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module}")
                failed_imports.append(module)
        
        if failed_imports:
            print(f"\n⚠️  Some modules failed to import: {failed_imports}")
            return False
        
        print("✅ All Python modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def print_success_message():
    """Print success message with next steps."""
    print("\n" + "=" * 70)
    print("🎉 INSTALLATION COMPLETE!")
    print("=" * 70)
    print()
    print("✅ All dependencies installed successfully:")
    print("   • Python backend with AI capabilities")
    print("   • React frontend with modern UI")
    print("   • Chatbot with hybrid RAG approach")
    print()
    print("🚀 Next Steps:")
    print("   1. Configure your environment:")
    print("      - Copy backend/.env.template to backend/.env")
    print("      - Add your Gemini API key")
    print("      - Update database credentials")
    print()
    print("   2. Start the application:")
    print("      # Terminal 1 - Backend")
    print("      cd backend && python app.py")
    print()
    print("      # Terminal 2 - Frontend")
    print("      cd frontend && npm start")
    print()
    print("   3. Test the chatbot:")
    print("      - Open http://localhost:3000")
    print("      - Click the floating chat button")
    print("      - Try: 'Show me VNIT Nagpur CSE cutoff'")
    print()
    print("📚 Documentation: CHATBOT_SETUP.md")
    print("🐛 Issues? Check console logs and documentation")
    print()

def main():
    """Main installation function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met.")
        print("Please install Node.js and npm, then run this script again.")
        sys.exit(1)
    
    # Install all dependencies
    success = True
    
    if not install_python_dependencies():
        success = False
    
    if not install_node_dependencies():
        success = False
    
    # Create environment files
    if not create_environment_files():
        success = False
    
    # Verify installation
    if not verify_installation():
        success = False
    
    if success:
        print_success_message()
    else:
        print("\n❌ Installation completed with some errors.")
        print("Please check the output above and resolve any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()

