import os

CSV_NAME = "covid19.csv"

def current_path():
    return os.path.dirname(os.path.abspath(__file__))

def handle_csv_path():
    return current_path() + "/" + CSV_NAME
