import firebase_admin
from firebase_admin import credentials, db
import time
import logging

# Initialize the Firebase app


# Reference to the Firebase database

class FirebaseOps:
    def __init__(self, credentials_path, database_url, database_path):
        self.cred = credentials.Certificate(credentials_path)
        self.firebase_admin.initialize_app(self.cred, {
            'databaseURL': database_url
        })
        self.ref = db.reference(database_path)

    def update_data(self, data):
        # send data to firebase
        try:
            self.ref.set(data)
        except Exception as e:
            logging.error(f"Error updating data: {e}")
            return False
        return True

    def get_data(self, data):
        # get data from firebase
        try:
            return self.ref.get(data)
        except Exception as e:
            logging.error(f"Error getting data: {e}")
            return None 
