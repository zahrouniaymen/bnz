import requests
import json

base_url = "http://127.0.0.1:8000"

def test_get_reasons():
    # Attempt login to get token
    login_url = f"{base_url}/auth/login"
    payload = {
        "username": "admin",
        "password": "password" 
    }
    
    try:
        r = requests.post(login_url, data=payload)
        if r.status_code != 200:
            print(f"Login failed: {r.status_code}")
            # Try 8001 if 8000 is not responding correctly
            return
        
        token = r.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test Get Reasons
        year = 2024
        reasons_url = f"{base_url}/analytics/reasons/{year}"
        r = requests.get(reasons_url, headers=headers)
        
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Data for {year}:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {r.text}")
            
    except Exception as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    test_get_reasons()
