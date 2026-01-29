import requests
import sys

URL = "http://localhost:5002/api/v1/tipos-servicio"

try:
    print(f"Testing Services API at {URL}")
    response = requests.get(URL)
    
    print(f"Status Code: {response.status_code}")
    print("Response JSON:", response.json())

except Exception as e:
    print(f"Error: {e}")
