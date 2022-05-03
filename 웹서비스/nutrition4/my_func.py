# FastAPI
import sqlite3
import pandas as pd
from IPython.display import display, Image
import os
import time
import shutil
import pickle
import json
from PIL import Image
import matplotlib.pyplot as plt
import yaml
import urllib.request

def pred(img_path):
    result_file_path = './pred_image/result'
    if os.path.exists(result_file_path):
        shutil.rmtree(result_file_path)
    os.system(f'python ./yolov5/detect.py --weights ./yolov5/model/last.pt --img 640 --conf 0.3 --source "{img_path}" --save-txt --name result --project ./pred_image ')
    global image_name
    image_name = img_path.split('/')[-1]

# predict된 음식명에 따라 영양성분 출력 함수 정의
def nutrition_info(food_list):
    conn = sqlite3.connect('./db/food_nutrition.db')
    sql = "select * from food_nutrition"
    food_nutri = pd.read_sql(sql, conn)
    food_nutri.set_index('음식명', inplace=True)
    
    # 예측된 음식명 담기
    food_name = []
    # 없는 음식명 담기
    food_name_x = []
    # 예측된 음식의 영양성분 담기
    food_info = {}
    # 음식명별 영양성분 정보
    Nutrition = {'중량': ['중량(g)'],
             '성분': ['에너지(kcal)', '탄수화물(g)', '당류(g)', '지방(g)', '단백질(g)', '칼슘(mg)', '인(mg)', 
                    '나트륨(mg)', '칼륨(mg)', '마그네슘(mg)', '철(mg)', '아연(mg)', '콜레스테롤(mg)', '트랜스지방(g)']}
    # 예측된 음식명들중에 하나씩 반복해서 이름은 음식명에 담고, 영양정보는 영양성분에 담기
    for name in food_list:
        if name in food_nutri.index:
            food_name.append(name)
            food_info[name] = dict(food_nutri.loc[name][Nutrition['성분']])
        # 음식명이 없으면 없는 음식명에 담고 없는 정보를 출력할 준비 함
        else:
            food_name_x.append(name)
            a = '없는 정보 :', food_name_x
    # 결과1: 없는음식명이 없다면 예측된 음식명 리스트와 그에대한 영양성분 정보 출력
    if food_name_x == []:
        return food_name, food_info
    # 결과2: 음식명이 없으면 없는음식명 정보를 출력
    elif food_name == []:
        return  print(a)
    # 결과3: 음식명이 있고, 없는것도 있으면 없는 음식명정보도 출력하고 예측된 음식명 리스트와 영양성분정보 출력
    else:
        print(a)
        return food_name, food_info

# 음식별 영양성분 더하기
def nutri_add(food_list):
    # 음식명별 영양성분 정보
    nut_info = nutrition_info(food_list)
    Nutrition = {'중량': ['중량(g)'],
             '성분': ['에너지(kcal)', '탄수화물(g)', '당류(g)', '지방(g)', '단백질(g)', '칼슘(mg)', '인(mg)', 
                    '나트륨(mg)', '칼륨(mg)', '마그네슘(mg)', '철(mg)', '아연(mg)', '콜레스테롤(mg)', '트랜스지방(g)']}
    # 전체음식의 영양성분을 한번에 담을 변수 생성 Nutri
    Nutri = {'에너지(kcal)': 0, '탄수화물(g)': 0, '당류(g)': 0, '지방(g)': 0, '단백질(g)': 0, '칼슘(mg)': 0, '인(mg)': 0,
             '나트륨(mg)': 0, '칼륨(mg)': 0, '마그네슘(mg)': 0, '철(mg)': 0, '아연(mg)': 0, '콜레스테롤(mg)': 0, '트랜스지방(g)': 0}
    # 추출된 전체 음식의 성분별로 영양성분 더하여 dict에 저장
    for name in nut_info[0]:
        for k in Nutrition['성분']:
            Nutri[k] += nut_info[1][name][k]
    return Nutri


# 1회 섭취량 합과 1회 권장 섭취량 합 비교
def calc_nutri(gender, age_range, food_list):
    conn = sqlite3.connect('./db/nutrition_recommend.db')
    sql = "select * from nutrition_recommend"
    nutri_reco = pd.read_sql(sql, conn)
    
    df = nutri_reco[(nutri_reco['성별'] == gender) & (nutri_reco['연령']== age_range)]
    result = nutri_add(food_list)
    temp = []
    for aug in df['영양성분']:
        if int(result[aug]) >= int(df[df['영양성분']==aug]['권장(g/회)']):
            c = int(result[aug])
            f = int(df[df['영양성분']==aug]['권장(g/회)'])
            g = aug.split('(')[1].split(')')[0]
            s = '[경고!]: '+ aug + ' 섭취량 ' + str(round(c-f)) + g + '초과!!'
        else:
            continue
        temp.append(s)
    return temp

def id_history(id) : 
    conn = sqlite3.connect('./db/id_record.db')

    with conn:
        cur = conn.cursor()
        sql = "select * from id_record where id=?"
        cur.execute(sql, id)
        rows = cur.fetchall()
        cols = [column[0] for column in cur.description]
        data_df = pd.DataFrame.from_records(data=rows, columns=cols)
    return data_df


def nutri_limit(data) : 
    conn = sqlite3.connect('./db/nutrition_limit.db')

    with conn:
        cur = conn.cursor()
        sql = "select * from nutrition_limit where 질병명=? and 성별=? and 연령=?"
        cur.execute(sql, data)
        rows = cur.fetchall()
        cols = [column[0] for column in cur.description]
        data_df = pd.DataFrame.from_records(data=rows, columns=cols)
    return data_df

# 1회분 섭취정보 db저장
def add_record(data):
    conn = sqlite3.connect('./db/id_record.db')
    
    with conn:
        cur = conn.cursor()
        sql = "insert into id_record values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        cur.executemany(sql, data)
        
        conn.commit()

# 양식은 이렇게?
# data = [['kangsan', '2022-04-17', '남자', '19-29', 220, 750, 74, 3.3, 20, 6.1, 2.8, 96, 4.3, 151, 0, 0.3, 2.1, 0, 0]]

# 섭취한 음식 DB 불러오기
def food_nut():
    conn = sqlite3.connect('./db/food_nutrition.db')
    sql = "select * from food_nutrition"
    nutri = pd.read_sql(sql, conn)
    nutri.set_index('음식명', inplace=True)
    return nutri

# 1회 섭취 권장량 DB 불러오기
def nutri_reco():
    conn = sqlite3.connect('./db/nutrition_recommend.db')
    sql = "select * from nutrition_recommend"
    reco = pd.read_sql(sql, conn)
    return reco


# 음식을 한글로 변환하기 위해 dictionary 및 pickle로 변환
def make_pickle():
    df = pd.read_csv('./[db]id_food_class_mapping(last_ver).csv')

    name_dict = {}
    name_list = []
    class_id_list = []

    for i in range(len(df)):
      name_list.append(df['음식명'][i])
      class_id_list.append(df['class_id'][i])

    for i in range(len(df)):
      name_dict.update(zip(class_id_list, name_list))

    with open('./data/name_dict.p', 'wb') as f:
      pickle.dump(name_dict, f)

# dictionary pickle 파일 불러오기
def load_pickle():
    try:
        with open("./data/name_dict.p", 'rb') as f: 
            return pickle.load(f)
    except FileNotFoundError:
        return {}

def get_result():
    result_list = []
    name_dict = load_pickle()
    try:
        with open('./pred_image/result/labels/{}.txt'.format(image_name.split('.')[0]), 'r') as f:
            result_line = f.readlines()
        for line in result_line:
            result_list.append(name_dict.get(int(line.split(' ')[0])))     
    except:
        pass
    return result_list

def voice(text):
    client_id = "fr2pmzwe08"
    client_secret = "uzTbsKj83c57qTJNlHRbeIsTiwDdVoZLKDod8UBh"
    encText = urllib.parse.quote(text)
    data = "speaker=nminseo&volume=-3&speed=-2&pitch=0&format=mp3&text=" + encText
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)
    response = urllib.request.urlopen(request, data=data.encode('utf-8'))
    rescode = response.getcode()
    if(rescode == 200):
        response_body = response.read()
        with open('./static/voice.mp3', 'wb') as f:
            f.write(response_body)
    else:
        errormsg = ("Error Code:" + rescode)
        return errormsg