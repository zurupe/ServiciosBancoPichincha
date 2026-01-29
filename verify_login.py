import requests
import sys

URL = "http://localhost:5001/api/auth/login"

try:
    print(f"Testing Login at {URL}")
    response = requests.post(URL, json={
        "usuario": "carlos.garcia0@example.com",
        "password": "1234"
    })
    
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", response.json())
    except:
        print("Response Text:", response.text)

except Exception as e:
    print(f"Error: {e}")
