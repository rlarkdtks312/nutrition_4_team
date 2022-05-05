# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 15:32:37 2022

@author: jjunghu
"""


# ex1) 다음의 성(family_name)과 이름을 이용하여 임의의 학생데이터 100개를
# prac4.db.Student 테이블에 insert 하시오

fam_names = list("김이박최강고윤엄한배성백전황서천방지마피")
first_names = list("건성현욱정민현주희진영래주동혜도모영진선재현호시우인성마무병별솔하라")


import sqlite3
import random

def make_name():
    sung = random.choice(fam_names)
    name = "".join(random.sample(first_names, 2))
    # name이 list형태로 반환되어 join 써서 string으로 바꾸기
    return (sung + name,)
    # ( ,) -> tuple로 변환


data = []
for i in range(0, 100):
    data.append(make_name())
    
conn = sqlite3.connect('prac4.db')

with conn:
    cur = conn.cursor()
    cur.execute(
        """
        create table Student(
            id integer primary key autoincrement not null,
            name text not null default 'aaa',
            mobile text null)
        """)
    sql = "insert into Student(name) values(?)"
    cur.executemany(sql, data)
    
    conn.commit()



