import requests

def main():
    base_url = "http://localhost:8088"
    username = "admin"
    password = "BI2026!"
    
    # Authenticate to get JWT token
    login_url = f"{base_url}/api/v1/security/login"
    res = requests.post(login_url, json={
        "password": password,
        "provider": "db",
        "username": username
    })
    token = res.json()["access_token"]
    
    # Fetch detailed database info
    headers = {"Authorization": f"Bearer {token}"}
    detail_url = f"{base_url}/api/v1/database/2"
    res_detail = requests.get(detail_url, headers=headers)
    db_detail = res_detail.json()["result"]
    
    # Print keys and values
    for k, v in db_detail.items():
        print(f"{k}: {v}")

if __name__ == '__main__':
    main()
