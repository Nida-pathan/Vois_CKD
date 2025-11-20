# Vercel WSGI entry point for Flask application
from app import app

# Vercel looks for an 'application' object
application = app

# For local testing
if __name__ == "__main__":
    application.run()