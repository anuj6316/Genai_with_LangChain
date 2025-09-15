"""
Startup script for Authentication API
"""
import uvicorn
import os
from dotenv import load_dotenv

def main():
    """Start the Authentication API server"""
    load_dotenv()
    
    # Check required environment variables
    required_vars = ["SECRET_KEY", "MONGODB_URI"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease copy env.example to .env and configure your settings")
        return
    
    print("Starting Authentication API Server")
    print("=" * 50)
    print(f"Server: http://localhost:8000")
    print(f"Documentation: http://localhost:8000/docs")
    print(f"ReDoc: http://localhost:8000/redoc")
    print("=" * 50)
    
    # Start server
    uvicorn.run(
        "auth_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

if __name__ == "__main__":
    main()