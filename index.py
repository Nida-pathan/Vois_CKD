# Vercel entry point for the Flask application
from app import app

application = app

if __name__ == "__main__":
    application.run()