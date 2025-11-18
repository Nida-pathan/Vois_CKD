# Vercel entry point for the Flask application
from app import app

# Vercel requires a 'application' object for the Flask app
application = app

# Also provide a 'handler' function for compatibility
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    application.run()