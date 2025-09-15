"""
Test client for Authentication API
"""
import requests
import json
from datetime import datetime

class AuthAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def signup(self, customer_id: str, email: str, password: str):
        """User registration"""
        url = f"{self.base_url}/auth/signup"
        data = {
            "customer_id": customer_id,
            "email": email,
            "password": password
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            return result
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def login(self, customer_id: str, password: str):
        """User login"""
        url = f"{self.base_url}/auth/login"
        data = {
            "customer_id": customer_id,
            "password": password
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            return result
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def get_current_user(self):
        """Get current user info"""
        if not self.token:
            return {"error": "Not authenticated"}
        
        url = f"{self.base_url}/auth/me"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = self.session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def forgot_password(self, customer_id: str):
        """Request password reset"""
        url = f"{self.base_url}/auth/forgot-password"
        data = {"customer_id": customer_id}
        
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def reset_password(self, token: str, new_password: str):
        """Reset password with token"""
        url = f"{self.base_url}/auth/reset-password"
        data = {
            "token": token,
            "new_password": new_password
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def change_password(self, current_password: str, new_password: str):
        """Change password"""
        if not self.token:
            return {"error": "Not authenticated"}
        
        url = f"{self.base_url}/auth/change-password"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "current_password": current_password,
            "new_password": new_password
        }
        
        response = self.session.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
    
    def logout(self):
        """Logout user"""
        if not self.token:
            return {"error": "Not authenticated"}
        
        url = f"{self.base_url}/auth/logout"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = self.session.post(url, headers=headers)
        if response.status_code == 200:
            self.token = None
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}

def test_api():
    """Test the API endpoints"""
    print("🚀 Testing Authentication API")
    print("=" * 50)
    
    client = AuthAPIClient()
    
    # Test 1: Signup
    print("\n1. Testing User Signup...")
    signup_result = client.signup(
        customer_id="CUST001",
        email="test@example.com",
        password="TestPass123"
    )
    
    if "error" in signup_result:
        print(f"❌ Signup failed: {signup_result['error']}")
    else:
        print("✅ Signup successful!")
        print(f"Token: {client.token[:20]}...")
        print(f"User: {signup_result['user']['customer_id']} ({signup_result['user']['email']})")
    
    # Test 2: Get current user
    print("\n2. Testing Get Current User...")
    user_result = client.get_current_user()
    
    if "error" in user_result:
        print(f"❌ Get user failed: {user_result['error']}")
    else:
        print("✅ Get user successful!")
        print(f"User: {user_result['customer_id']} ({user_result['email']})")
    
    # Test 3: Forgot password
    print("\n3. Testing Forgot Password...")
    forgot_result = client.forgot_password("CUST001")
    
    if "error" in forgot_result:
        print(f"❌ Forgot password failed: {forgot_result['error']}")
    else:
        print("✅ Forgot password successful!")
        print(f"Message: {forgot_result['message']}")
    
    # Test 4: Change password
    print("\n4. Testing Change Password...")
    change_result = client.change_password("TestPass123", "NewPass123")
    
    if "error" in change_result:
        print(f"❌ Change password failed: {change_result['error']}")
    else:
        print("✅ Change password successful!")
        print(f"Message: {change_result['message']}")
    
    # Test 5: Login with new password
    print("\n5. Testing Login with New Password...")
    login_result = client.login("CUST001", "NewPass123")
    
    if "error" in login_result:
        print(f"❌ Login failed: {login_result['error']}")
    else:
        print("✅ Login successful!")
        print(f"Token: {client.token[:20]}...")
    
    # Test 6: Logout
    print("\n6. Testing Logout...")
    logout_result = client.logout()
    
    if "error" in logout_result:
        print(f"❌ Logout failed: {logout_result['error']}")
    else:
        print("✅ Logout successful!")
        print(f"Message: {logout_result['message']}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")

def interactive_test():
    """Interactive testing mode"""
    print("🤖 Interactive Authentication API Test Client")
    print("=" * 50)
    
    client = AuthAPIClient()
    
    while True:
        print("\nOptions:")
        print("1. Signup")
        print("2. Login")
        print("3. Get Current User")
        print("4. Forgot Password")
        print("5. Reset Password")
        print("6. Change Password")
        print("7. Logout")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            customer_id = input("Customer ID: ")
            email = input("Email: ")
            password = input("Password: ")
            result = client.signup(customer_id, email, password)
            print(f"Result: {result}")
        
        elif choice == "2":
            customer_id = input("Customer ID: ")
            password = input("Password: ")
            result = client.login(customer_id, password)
            print(f"Result: {result}")
        
        elif choice == "3":
            result = client.get_current_user()
            print(f"Result: {result}")
        
        elif choice == "4":
            customer_id = input("Customer ID: ")
            result = client.forgot_password(customer_id)
            print(f"Result: {result}")
        
        elif choice == "5":
            token = input("Reset Token: ")
            new_password = input("New Password: ")
            result = client.reset_password(token, new_password)
            print(f"Result: {result}")
        
        elif choice == "6":
            current_password = input("Current Password: ")
            new_password = input("New Password: ")
            result = client.change_password(current_password, new_password)
            print(f"Result: {result}")
        
        elif choice == "7":
            result = client.logout()
            print(f"Result: {result}")
        
        elif choice == "8":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        test_api()
