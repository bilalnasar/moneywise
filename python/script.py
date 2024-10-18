import requests

BASE_URL = "http://localhost:8000"  # Adjust if your server is running on a different port

# Step 1: Register a new user
register_response = requests.post(f"{BASE_URL}/register", data={
    "username": "testuser",
    "password": "testpassword"
})
print("Register response:", register_response.json())

# Step 2: Get an access token
token_response = requests.post(f"{BASE_URL}/token", data={
    "username": "testuser",
    "password": "testpassword"
})
access_token = token_response.json()["access_token"]
print("Access token:", access_token)

# Step 3: Set the Plaid access token
set_access_token_response = requests.post(
    f"{BASE_URL}/api/set_access_token",
    headers={"Authorization": f"Bearer {access_token}"},
    data={"public_token": "your_plaid_public_token_here"}
)

print("Status Code:", set_access_token_response.status_code)
print("Response Text:", set_access_token_response.text)

if set_access_token_response.status_code == 200:
    try:
        print("Set access token response:", set_access_token_response.json())
    except ValueError:
        print("Response is not valid JSON.")
else:
    print("Error occurred:", set_access_token_response.status_code)

print("Set access token response:", set_access_token_response.json())