# Test script to verify Flask app works correctly
from app import app

def test_app():
    with app.test_client() as client:
        # Test the root route
        response = client.get('/')
        print(f"Root route status code: {response.status_code}")
        
        # Test the landing route
        response = client.get('/landing')
        print(f"Landing route status code: {response.status_code}")
        
        # Test the test route
        response = client.get('/test')
        print(f"Test route status code: {response.status_code}")
        print(f"Test route content: {response.data.decode()}")

if __name__ == "__main__":
    test_app()