"""
FastAPI Authentication System Runner
Run this file to start the application
"""
import sys
import os
import uvicorn

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting FastAPI Authentication System...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)