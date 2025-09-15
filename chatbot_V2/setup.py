"""
Setup script for Authentication API
"""
import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing Authentication API requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_mongodb():
    """Check if MongoDB is available"""
    print("🔍 Checking MongoDB availability...")
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible!")
        return True
    except Exception as e:
        print(f"❌ MongoDB not accessible: {e}")
        print("💡 Please ensure MongoDB is installed and running, or use MongoDB Atlas")
        return False

def check_env_file():
    """Check if .env file exists"""
    print("🔍 Checking environment configuration...")
    if os.path.exists('.env'):
        print("✅ .env file found!")
        return True
    else:
        print("⚠️  .env file not found!")
        print("💡 Please copy env.example to .env and configure your settings")
        return False

def check_required_vars():
    """Check if required environment variables are set"""
    print("🔍 Checking required environment variables...")
    required_vars = ["SECRET_KEY", "MONGODB_URI"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set!")
        return True

def run_tests():
    """Run API tests"""
    print("🧪 Running API tests...")
    try:
        subprocess.check_call([sys.executable, "test_auth_api.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Authentication API Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        return
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check MongoDB
    mongodb_ok = check_mongodb()
    
    # Check environment file
    env_ok = check_env_file()
    
    # Check environment variables
    vars_ok = check_required_vars()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Setup Summary:")
    print(f"✅ Requirements installed")
    print(f"{'✅' if mongodb_ok else '❌'} MongoDB connection")
    print(f"{'✅' if env_ok else '❌'} Environment configuration")
    print(f"{'✅' if vars_ok else '❌'} Required environment variables")
    
    if mongodb_ok and env_ok and vars_ok:
        print("\n🎉 Setup complete! You can now run the Authentication API.")
        print("💡 Run 'python start_auth_api.py' to start the server")
        print("💡 Visit http://localhost:8000/docs for API documentation")
        
        # Ask if user wants to run tests
        run_test = input("\nWould you like to run the API tests? (y/n): ").strip().lower()
        if run_test == 'y':
            run_tests()
    else:
        print("\n⚠️  Setup incomplete. Please resolve the issues above.")
        if not mongodb_ok:
            print("💡 Install MongoDB locally or set up MongoDB Atlas")
        if not env_ok:
            print("💡 Copy env.example to .env")
        if not vars_ok:
            print("💡 Configure required environment variables in .env")

if __name__ == "__main__":
    main()
