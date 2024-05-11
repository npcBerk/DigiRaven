import firebase_admin
from firebase_admin import credentials, db

class Firebase:
    def __init__(self):
        # Initialize Firebase Admin SDK with credentials and database URL
        CREDENTIALS_FILE = "cred.json"
        DATABASE_URL = "https://sftproject-a6eeb-default-rtdb.europe-west1.firebasedatabase.app/"
        self.cred = credentials.Certificate(CREDENTIALS_FILE)
        firebase_admin.initialize_app(self.cred, {"databaseURL": DATABASE_URL})

        # Reference to the root of the Firebase Realtime Database
        self.ref = db.reference("/")

    def login(self, email, password):
        # Implement authentication logic using Firebase Admin SDK
        try:
            user = firebase_admin.auth().sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            raise e

    def register(self, email, password):
        # Implement user registration logic using Firebase Admin SDK
        try:
            user = firebase_admin.auth().create_user(email=email, password=password)
            return user
        except Exception as e:
            raise e

    def get_current_user(self):
        # Get current authenticated user from Firebase Admin SDK
        user = firebase_admin.auth().get_user(firebase_admin.auth.current_user().uid)
        return user

    def logout(self):
        # Clear current authenticated user (not supported directly in Firebase Admin SDK)
        pass  # You may need to implement this based on your application needs


if __name__ == "__main__":
    # Instantiate Firebase object
    f = Firebase()

    # Access and modify data in Realtime Database
    print(f.ref.get())
    f.ref.set({"name": "Melisa Uyar"})
    print(f.ref.get())

    try:
        # Try logging in with existing user credentials
        f.login("example@gmail.com", "password")
    except Exception as e:
        # If login fails, register a new user
        f.register("example@gmail.com", "password")

    # Get details of current authenticated user
    print(f.get_current_user())
