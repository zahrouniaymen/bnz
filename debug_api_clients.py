import requests
import json

base_url = "http://127.0.0.1:8000"

def test_get_clients():
    # Attempt login to get token
    login_url = f"{base_url}/auth/login"
    payload = {
        "username": "admin",
        "password": "password"  # Using standard local password
    }
    
    try:
        r = requests.post(login_url, data=payload)
        if r.status_code != 200:
            print(f"Login failed: {r.status_code} - {r.text}")
            return
        
        token = r.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test Get Clients
        clients_url = f"{base_url}/clients/?skip=0&limit=500"
        r = requests.get(clients_url, headers=headers)
        
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Total clients returned: {len(data)}")
            if len(data) > 0:
                print(f"First client: {json.dumps(data[0], indent=2)}")
        else:
            print(f"Error: {r.text}")
            
    except Exception as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    test_get_clients()
