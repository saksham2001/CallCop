import firebase_admin
from firebase_admin import credentials, db
import logging

class FirebaseOps:
    def __init__(self, credential_path, database_url):
        try:
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            self.db_ref = db.reference()
            logging.info("Firebase connection initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing Firebase: {str(e)}")
            raise

    def update_data(self, data):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        try:
            self.db_ref.update(data)
            logging.info("Data updated successfully in Firebase.")
        except Exception as e:
            logging.error(f"Error updating data in Firebase: {str(e)}")
            raise
