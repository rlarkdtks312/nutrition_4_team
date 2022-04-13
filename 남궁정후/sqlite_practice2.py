# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 12:17:54 2022

@author: jjunghu
"""


# CREATE TABLE & INSERT DATA
import sqlite3

conn = sqlite3.connect("employee.db")
# employee.db가 없을 경우 새로 생성하면서 연결
# 이미 있을 경우 해당 db로 연결

cur = conn.cursor()
conn.execute("CREATE TABLE employee_data(id INTEGER, name TEXT, nickname TEXT, department TEXT, employment_date TEXT)")

cur.executemany(
    "INSERT INTO employee_data VALUES(?, ?, ?, ?, ?)",
    [(1001, 'Junghu', 'Dal9', 'Development', '2020-04-01 00:00:00.000'),
     (2001, 'Seonghyun', 'Babo', 'Marketing', '2020-04-01 00:00:00.000'),
     (2002, 'Moonsuk', 'Bibo', 'Marketing', '2020-04-01 00:00:00.000'),
     (1002, 'Chaeyoung', 'Ggaeyong', 'Development', '2020-04-01 00:00:00.000'),
     (1003, 'Buyong', 'Oliveyong', 'Development', '2020-04-01 00:00:00.000')
     ]
    )

conn.commit()    # 변경사항 저장
conn.close()     # db 연결 해제



# SELECT & PRINT DATA FROM DB
# 모든 데이터 가져와서 출력
conn = sqlite3.connect('employee.db')

cur = conn.cursor()

cur.execute("SELECT * FROM employee_data")

rows = cur.fetchall()

for row in rows:
    print(row)
    
conn.close()



# 원하는 값만 출력
# ex1) employee_data 테이블에서 id가 2000보다 큰 사람의 이름과 부서만 가져오기
conn = sqlite3.connect('employee.db')
cur = conn.cursor()
cur.execute("SELECT name, department FROM employee_data WHERE employee_data.id > 2000")
print(cur.fetchall())


# ex2) employee_data 테이블에서 이름이 Junghu인 사람의 닉네임만 가져오기
cur.execute("SELECT nickname FROM employee_data WHERE employee_data.name=='Junghu'")
print(cur.fetchall())

conn.close()


# 모든 데이터를 가져와서 DataFrame 형태로 출력하기
import pandas as pd

conn = sqlite3.connect('employee.db')
cur = conn.cursor()
cur.execute("SELECT * FROM employee_data")
rows = cur.fetchall()
cols = [column[0] for column in cur.description]
data_df = pd.DataFrame.from_records(data=rows, columns=cols)
conn.close()

data_df



# Table 삭제하기
conn = sqlite3.connect('employee.db')
cur = conn.cursor()
conn.execute("DROP TABLE employee_data2")
conn.close()