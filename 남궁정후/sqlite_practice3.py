# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 13:08:25 2022

@author: jjunghu
"""


import sqlite3
conn = sqlite3.connect('prac1.db')

cur = conn.cursor()

cur.execute(
    """
    create table Student(
        id integer primary key autoincrement not null,
        name text not null default 'aaa',
        mobile text null)
    """)
    
cur.execute("insert into Student(name, mobile) values('나희도', '010-2323-4545')")
cur.execute("insert into Student(name) values('백이진')")

cur.execute("select * from Student")

rows = cur.fetchall()
for row in rows:
    print(row)
    
conn.commit()
conn.close()


# with 문 --> conn.close() 실행 안해도 됨
import sqlite3

conn = sqlite3.connect('prac1.db')

with conn:
    cur = conn.cursor()
    sql = "select * from Student where id=? or name=?"
    cur.execute(sql, (1, '나희도'))
    rows = cur.fetchall()
    
    for row in rows:
        print(row)

# -----------------------------------------------------

import sqlite3

conn = sqlite3.connect('prac1.db')

with conn:
    cur = conn.cursor()
    sql = "insert into Student(name, mobile) values(?,?)"
    cur.execute(sql, ('고유림', None))
    
    conn.commit()


# ------------------------------------------------------

import sqlite3

conn = sqlite3.connect('prac1.db')

data = (
        ('문지웅', '010-5555-6666'),
        ('지승완', '010-6666-7777')
        )

with conn:
    cur = conn.cursor()
    sql = "insert into Student(name, mobile) values(?,?)"
    cur.executemany(sql, data)
    
    conn.commit()



# -----------------------------------------------------




