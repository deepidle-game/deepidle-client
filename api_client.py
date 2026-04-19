import requests

class APIClient:
    def __init__(self, base_url="http://localhost:3000/api", source="Unknown"):
        self.base_url = base_url
        self.token = None
        self.headers = {
            "Content-Type": "application/json",
            "X-Client-Source": source
        }

    def set_token(self, token):
        self.token = token
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        else:
            if "Authorization" in self.headers:
                del self.headers["Authorization"]

    def login(self, username, password):
        url = f"{self.base_url}/auth/signin"
        response = requests.post(url, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            self.set_token(data.get("token"))
            return data
        return None

    def signup(self, username, password):
        url = f"{self.base_url}/auth/signup"
        response = requests.post(url, json={"username": username, "password": password})
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        return None

    def get_character_detail(self):
        url = f"{self.base_url}/character/detail"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def set_action(self, action):
        url = f"{self.base_url}/character/action"
        response = requests.post(url, headers=self.headers, json={"action": action})
        if response.status_code == 200:
            return response.json()
        return None

    def claim_resources(self):
        url = f"{self.base_url}/character/claim"
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_inventory(self):
        url = f"{self.base_url}/inventory"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_upgrade_options(self):
        url = f"{self.base_url}/inventory/upgrade-options"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def upgrade_item(self, item_id):
        url = f"{self.base_url}/inventory/upgrade"
        response = requests.post(url, headers=self.headers, json={"item_id": item_id})
        if response.status_code == 200:
            return response.json()
        return None

    def update_character_name(self, new_name):
        url = f"{self.base_url}/character/name"
        response = requests.patch(url, headers=self.headers, json={"name": new_name})
        if response.status_code == 200:
            return response.json()
        return None

    def get_global_storage(self):
        url = f"{self.base_url}/storage"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def deposit_to_storage(self, item_id, quantity):
        url = f"{self.base_url}/storage/deposit"
        response = requests.post(url, headers=self.headers, json={"item_id": item_id, "quantity": quantity})
        if response.status_code == 200:
            return response.json()
        return None

    def withdraw_from_storage(self, item_id, quantity):
        url = f"{self.base_url}/storage/withdraw"
        response = requests.post(url, headers=self.headers, json={"item_id": item_id, "quantity": quantity})
        if response.status_code == 200:
            return response.json()
        return None

