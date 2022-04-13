# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 10:07:20 2022

@author: jjunghu
"""

import sqlite3
print(sqlite3.version)
print(sqlite3.sqlite_version)

# DB 실행 (오토 커밋)
conn = sqlite3.connect('test.db', isolation_level=None)

# 커서 획득
c = conn.cursor()

# 테이블 생성 (데이터 타입은 TEXT, NUMERIC, INTEGER, REAL, BLOB 등)
c.execute("CREATE TABLE IF NOT EXISTS table1 \
          (id integer PRIMARY KEY, name text, birthday text)")
# c.execute("CREATE TABLE IF NOT EXISTS 테이블이름()") 
# 안에 문자열로 필드(열) 이름과 데이터 타입을 작성해주면 됨
# 필드명 > 데이터 타입 순으로 입력
# PRIMARY KEY는 테이블 내에 있는 레코드를 식별하는 고유 키, 유일한 것이어야 함


# 개념1. commit & rollback
# 위에서 sqlite3.connect() 안에 isolation_level=None
# (실습을 위해) 쿼리문을 실행하여 DB에 즉시 반영, 즉시 자동 커밋을 하기 위함

# commit(커밋) : 변경사항을 DB에 반영
# conn.commit() : 최종적으로 DB를 수정하려면 마지막에 반드시 실행
# conn.rollback() : commit과 반대되는 개념, 이전 이력으로 되돌린다는 뜻


# 개념2. cursor
# 파이썬에서 파일을 읽고 쓰려면 커서를 가져와야 함
# conn.cursor()로 커서 생성



# 데이터 삽입 방법 1
# 필드명과 순서를 정확히 알고있을 때
c.execute("INSERT INTO table1\
          VALUES(1, 'JUNGHU', '1994-05-16')")

# 데이터 삽입 방법 2 (정석)
c.execute("INSERT INTO table1(id, name, birthday) \
          VALUES(?,?,?)", \
              (2, 'KIM', '1990-01-10'))

# c.executemany() : 튜플이나 리스트 형태의 데이터 세트를 한 번에 삽입하는 방법
test_tuple = (
    (3, 'CHAEYOUNG', '1995-01-18'),
    (4, 'BUYONG', '1994-04-25'),
    (5, 'EUNYOUNG', '1994-11-23')
    )

c.executemany("INSERT INTO table1(id, name, birthday) VALUES(?,?,?)", test_tuple)



# 데이터 불러오기
c.execute("SELECT * FROM table1")
print(c.fetchone())    # 한 줄씩 출력 (fetch: 가져오다)
print(c.fetchone())
print(c.fetchall())    # 이미 읽은 지점 이후에 있는 것들만 출력

# 반복문을 이용해 불러오기
# 방법 1
c.execute("SELECT * FROM table1")
for row in c.fetchall():
    print(row)
    
# 방법 2
for row in c.execute("SELECT * FROM table1 ORDER BY id ASC"):
    print(row)



# 데이터 조회하기 (필터링)
# 방법 1
param1 = (1,)
c.execute("SELECT * FROM table1 WHERE id=?", param1)
print('param1', c.fetchone())
print('param1', c.fetchall())

# 방법 2
param2 = 1
c.execute("SELECT * FROM table1 WHERE id=%s" % param2)  # %s %d %f
print('param2', c.fetchone())
print('param2', c.fetchall())

# 방법 3
c.execute("SELECT * FROM table1 WHERE id=:Id", {"Id":1})
print('param3', c.fetchone())
print('param3', c.fetchall())

# 방법 4
param4 = (1, 4)
c.execute("SELECT * FROM table1 WHERE id IN(?,?)", param4)
print('param4', c.fetchall())

# 방법 5
c.execute("SELECT * FROM table1 WHERE id IN('%d', '%d')" % (1,4))
print('param5', c.fetchall())

# 방법 6
c.execute("SELECT * FROM table1 WHERE id=:id1 OR id=:id2", {"id1":1, "id2":4})
print('param6', c.fetchall())



# 데이터 수정하기
# 방법 1
c.execute("UPDATE table1 SET name=? WHERE id=?", ('NEW1', 1))

# 방법 2
c.execute("UPDATE table1 SET name=:name WHERE id=:id", {'name':'NEW2', 'id':3})

# 방법 3
c.execute("UPDATE table1 SET name='%s' WHERE id='%s'" % ('NEW3', 5))

# 확인
for row in c.execute("SELECT * FROM table1") : 
    print(row)
    


# 데이터 삭제하기
# 방법 1
c.execute("DELETE FROM table1 WHERE id=?", (1,))

# 방법 2
c.execute("DELETE FROM table1 WHERE id=:id", {'id':3})

# 방법 3
c.execute("DELETE FROM table1 WHERE id='%s'" % 5)

# 확인
for row in c.execute("SELECT * FROM table1") : 
    print(row)
    
# conn.execute() : 테이블 내의 데이터 전체 삭제
# 방법 1
# conn.execute("DELETE FROM table1")

# 방법 2
print(conn.execute("DELETE FROM table1").rowcount)
# 뒤에 rowcount를 붙여주면 지운 행 개수를 반환



# DB 연결 해제
# 데이터베이스를 연결해서 이런저런 수정을 했으면 마지막엔 그 연결을 해제해야 함
# 항상 conn.close() 명령으로 마무리

# DB 백업하기 (dump)
with conn:
    with open('dump.sql', 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
        print('Completed.')
        