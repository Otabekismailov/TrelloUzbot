import environs
import psycopg2
import os

env = environs.Env()
env.read_env()
connection = psycopg2.connect(
    dbname=os.getenv('NAMEDB'),
    user=os.getenv('USERDB'),
    password=os.getenv('PASSWORDDB'),
    host=os.getenv('hostdb'),
    port=5432
)
db = connection.cursor()
