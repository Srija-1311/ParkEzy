"""
Entry point for running the Smart Parking System application
"""
import os
from app import app

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Smart Parking System on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
