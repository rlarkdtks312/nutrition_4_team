import sqlite3
import sys

def add_record(data):
    conn = sqlite3.connect('./db/id_record.db')
    
    with conn:
        cur = conn.cursor()
        sql = "insert into id_record values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        cur.executemany(sql, data)
        
        conn.commit()
        
if __name__ == '__main__': 
    add_record(sys.argv[1:])