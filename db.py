import mysql.connector as db
from faker import Faker

def __init__(self):
        self.db_connection = db.connect(
            host="localhost",
            user="root",
            password="SathishMyilsamy@21601",
            database="zomato_db"
        )
        self.cursor = self.db_connection.cursor()
        self.fake = Faker()
        self.create_tables()
