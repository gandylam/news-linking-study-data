from dotenv import load_dotenv
import os

load_dotenv()

MC_API_KEY = os.environ.get('MC_API_KEY', None)

DB_URI = os.environ.get('DB_URI', None)
DB_NAME = os.environ.get('DB_NAME', None)
DB_COLLECTION_NAME = os.environ.get('DB_COLLECTION_NAME', None)

BROKER_URL = os.environ.get('BROKER_URL', None)
