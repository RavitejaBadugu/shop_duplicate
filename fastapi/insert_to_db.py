import os
import time
import psycopg2
import pandas as pd
from tqdm import tqdm
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

def Make_Connection():
    no_connect=True
    while no_connect:
        try:
            conn=psycopg2.connect(
            host="localhost",
            password="my-password",
            user="admin",
            port=5432,
            database="DB",
            cursor_factory = RealDictCursor
            )   
            cursor = conn.cursor()
            no_connect=False
        except:
            print("connection is not made. Wait for some time")
            time.sleep(10)
    return conn,cursor


def Creator():
    conn,cursor=Make_Connection()
    query=sql.SQL("""
    CREATE TABLE IF NOT EXISTS post_info
    (id serial,
    post_names varchar(100) not null,
    PRIMARY KEY (id,post_names)
    );
    """)
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

def Insert_To_Table(path):
    conn,cursor=Make_Connection()
    for chunck in tqdm(pd.read_csv(path,chunksize=10_000,usecols=["posting_id"])):
      tuples = [tuple(x) for x in chunck.to_numpy()]
      query=sql.SQL('''
         INSERT INTO post_info (post_names)
         VALUES
         (%s)
         ''')
      cursor.executemany(query,tuples)
    conn.commit()
    cursor.close()
    conn.close()

if __name__=="__main__":
    Creator()
    Insert_To_Table(path="train.csv")