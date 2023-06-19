
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

creds = {
     "host": os.getenv("host"),
    "user": os.getenv("user"), 
    "password": os.getenv("password"),
    "dbname": os.getenv("dbname")
}

#запуск etl процесса
with psycopg2.connect(**creds) as conn:
    with conn.cursor() as cur:
        cur.execute("call etl.load_from_src_to_target()")
        mes = '\n'.join(conn.notices)
        print(mes)
