import requests
import sys
import os

def test_client_ranking():
    print("Logging in...")
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            data={"username": "test_debug", "password": "debug123"}
        )
    except Exception as e:
        print(f"FAILED to connect: {e}")
        return

    if response.status_code != 200:
        print(f"FAILED to login: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Fetching client-ranking for 2024...")
    resp = requests.get("http://localhost:8000/analytics/client-ranking/2024", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Items returned: {len(data)}")
        if len(data) > 0:
            print("First item:", data[0])
        else:
            print("No data returned!")
    else:
        print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    test_client_ranking()
