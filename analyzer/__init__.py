from dotenv import load_dotenv
import os

load_dotenv()

base_dir = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
data_dir = os.path.join(base_dir, "analyzer", "data")

COUNTRIES = ['IND', 'GBR', 'KEN', 'ZAF', 'AUS', 'PHL', 'USA']
