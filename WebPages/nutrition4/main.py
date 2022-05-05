from typing import Optional
from urllib import response
from fastapi import FastAPI, Response, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Cookie, FastAPI
from PIL import Image

import get_food_list
import pickle
import datetime
import my_func
import requests
import json
import pandas as pd

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/img', StaticFiles(directory='img'), name='img')
app.mount('/image', StaticFiles(directory='image'), name='image')
app.mount('/pred_image', StaticFiles(directory='pred_image'), name='pred_image')
templates = Jinja2Templates(directory="templates")


# 루트 url 페이지 index.html 반환
@app.get('/', response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request })

# 카카오 로그인 페이지 code 받기
@app.get("/kakao")
async def kakao():
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    REDIRECT_URI = "http://110.165.18.242:8000/oauth"
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    response = RedirectResponse(url)
    return response

# 받은 code를 활용하여 access_token을 받아 url로 반환
@app.get('/oauth')
async def kakaoAuth(response: Response, code: Optional[str]="NONE"):
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    REDIRECT_URI = 'http://110.165.18.242:8000/oauth'
    _url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&code={code}&redirect_uri={REDIRECT_URI}'
    _res = requests.post(_url)
    _result = _res.json()
    response = RedirectResponse('http://110.165.18.242:8000/info/{}'.format(_result['access_token']))
    return response

# 쿼리 파라미터를 사용한 token 값 사용(개인 정보: 메일, 성별, 나이 얻기)
# 사진 업로드 페이지인 main.html 반환
@app.get('/info/{KEY}', response_class=HTMLResponse)
async def user_info(response: Response, request: Request, KEY: Optional[str]):
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    url = "https://kapi.kakao.com/v2/user/me?property_keys=[\"kakao_account.email\", \"kakao_account.age_range\", \"kakao_account.gender\"]"
    headers = {
      'Authorization': f'Bearer {KEY}'
    }
    
    response = requests.request("GET", url, headers=headers)
    data = response.json()['kakao_account']
    
    with open('./data/data.json', 'w') as outfile:
      json.dump(data, outfile)

    return templates.TemplateResponse("main.html", {"request": request })

# 예측된 이미지 정보, 사용자 정보를 활용
# 현재 식단의 영양성분, 한끼 권장량별 성분, 질병별 주의할 성분, 경고메시지 출력
# tts 서비스, popup 창 정보 html 전달 및 print.html 반환
@app.post('/print', response_class=HTMLResponse)
async def get_page(request: Request, img_s: UploadFile = File(...), disease : list= Form(...)):
    # 질병명 저장하기 history 페이지에서 사용하기 위함
    with open('./disease/disease.pickle', 'wb') as f:
      pickle.dump(disease, f, pickle.HIGHEST_PROTOCOL)
      
    # 업로드한 이미지 저장 예측 이전 단계
    file_location = f"./image/{img_s.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(img_s.file.read())
    
    # 사용자 로그인 정보 가져오기
    with open('data/data.json', "r") as json_file:
      json_data = json.load(json_file)
      
    email = json_data['email']
    if json_data['gender'] == 'male':
      gender = '남자'
    else:
      gender = '여자'
    age_range = json_data['age_range']

    # 예측 수행 및 음식 리스트 생성 
    # 예측 된 이미지는 2개이더라도 1인분 기준 섭취량을 추가 할 수 있게 중복제거
    my_func.pred(file_location)
    pred_file = file_location.split('/')[-1]
    pred_file_path = "../pred_image/result/"+pred_file
    food_list_temp = my_func.get_result()
    
    food_list = []
    for value in food_list_temp: 
      if value not in food_list: 
        food_list.append(value) 
    
    # 현재식단의 영양성분 
    # DataFrame을 html 형태로 변환
    df = pd.DataFrame(my_func.nutrition_info(food_list)[1])
    food_info = df.to_html(justify="center")
    
    ## 한끼 영양소 섭취량 그래프 데이터 생성
    nutri_reco = my_func.nutri_reco()
    condition = ((nutri_reco['성별'] == gender) & (nutri_reco['연령'] == age_range))
    nutri_reco_id = nutri_reco[condition]['권장(g/회)']
    nutri_reco_id = list(nutri_reco_id)
    energe = my_func.nutri_limit(['비만', gender, age_range])
    
    nutri_addition = my_func.nutri_add(food_list)
    nutri_list = list(nutri_addition.values())
    for i in range(len(nutri_reco_id)):
          if i == 0:
            nutri_list[i] = round((nutri_list[i] / list(energe['섭취기준(1일)'])[0])*300, 2)  
          else:
            nutri_list[i+1] = round((nutri_list[i+1] / nutri_reco_id[i])*100, 2)
    nutri_list = nutri_list[:-2]
    
    ## 질병별 주의할 성분 데이터 생성
    for idx, dise in enumerate(disease):
      if idx == 0:
        dise_nutri = my_func.nutri_limit([dise, gender, age_range])
        total_df = dise_nutri[['질병명', '영양성분', '섭취기준(1일)', '단위', '※추가생생정보※']]
      else:
        dise_nutri = my_func.nutri_limit([dise, gender, age_range])
        temp_df = dise_nutri[['질병명', '영양성분', '섭취기준(1일)', '단위', '※추가생생정보※']]
        total_df = pd.concat([total_df, temp_df])
    total_df = total_df.set_index('질병명').reset_index()
    dise_info = total_df.to_html(justify="center")
    
    ## 경고메시지 생성
    temp = my_func.calc_nutri(gender, age_range, food_list)
    temp = pd.DataFrame(temp)
    temp.columns = ['경고메세지']
    temp2 = temp.values
    temp = temp.style.hide_index()
    message = temp.to_html()
    
    temp2 = list(temp2)
    temp_message = ''
    for mess in temp2:
          temp_message += mess

    ## 네이버 클로바 TTS 서비스
    my_func.voice("권장량을 초과한 영양소가 있습니다! 경고메시지를 확인해주세요!")
    fn = app.url_path_for('static', path='/voice.mp3')
  
    return templates.TemplateResponse("print.html", {"request": request, 'food_names': food_list, 
                                                     'email':email, 'gender':gender, 'age_range':age_range, 
                                                     'disease':disease, 'img_path':pred_file_path, 'nutri_list':nutri_list,
                                                     'dise_info':dise_info, 'food_info': food_info, 'fn': fn, 'message': message,
                                                     'temp_message': temp_message
                                                     }
                                      )
    
@app.get('/his', response_class=HTMLResponse)
async def get_history(request: Request):
  # 질병명 저장하기
  with open('./disease/disease.pickle', 'rb') as f:
    disease_list = pickle.load(f)
    
  # 로그인 정보 가져오기
  with open('data/data.json', "r") as json_file:
    json_data = json.load(json_file)
    
  email = json_data['email']
  if json_data['gender'] == 'male':
    gender = '남자'
  else:
    gender = '여자'
  age_range = json_data['age_range']
  
  # 아이디 기준 먹은 음식 가져오기
  # 예측 된 이미지는 2개이더라도 1인분 기준 섭취량을 추가 할 수 있게 중복제거
  food_list_temp = get_food_list.get_food_list()
  food_list = []
  for value in food_list_temp: 
    if value not in food_list: 
      food_list.append(value) 
      
  # 음식 데이터 저장
  now = datetime.datetime.now()
  cur_time = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
  
  nutri_add2 = my_func.nutri_add(food_list)
  record_list = [email, cur_time, gender, age_range]

  for nutri in nutri_add2.values():
        record_list.append(nutri)
  my_func.add_record([record_list])      
  
  # 일일 영양소 섭취량 계산
  nutri_reco = my_func.nutri_reco()
  condition = ((nutri_reco['성별'] == gender) & (nutri_reco['연령'] == age_range))
  nutri_reco_id = nutri_reco[condition]['권장(g/일)']
  nutri_reco_id = list(nutri_reco_id)
  history = my_func.id_history([email])
  
  condition2 = (history.groupby(['id', 'date']).sum().reset_index()['date'] == cur_time)
  nutri_list = history.groupby(['id', 'date']).sum().reset_index()[condition2].iloc[0].values[2:]
  
  energy = my_func.nutri_limit(['비만', gender, age_range])
  nutri_list = nutri_list[:-2]
  
  for i in range(len(nutri_reco_id)):
        if i == 0:
          nutri_list[i] = (nutri_list[i] / list(energy['섭취기준(1일)'])[0])*100  
        else:
          nutri_list[i+1] = (nutri_list[i+1] / nutri_reco_id[i])*100
          
  for idx, nutri in enumerate(nutri_list):
        nutri_list[idx] = round(nutri,2)
  
  nutri_list = list(nutri_list)
  
  # 질병 별 그래프 그리기
  # having_list : 먹은 음식의 영양소 섭취량
  # nutri_name_list : 먹은 음식 이름
  having_list = []
  nutri_name_list = []
  for disease in disease_list:
    energy_list = my_func.nutri_limit([disease, gender, age_range])
    nutri_name = energy_list["영양성분"]
    nutri_std = energy_list["섭취기준(1일)"].values
    
    unit = energy_list["단위"]
    
    cur_index = []
    nutri_name = nutri_name.values
    
    for idx, column in enumerate(history.groupby(['id', 'date']).sum().reset_index()[condition2].columns):
        for name in nutri_name:
          if column == '에너지(kcal)':
              if '열량' == name:
                  cur_index.append(idx)
          elif column.split('(')[0] == name:
                cur_index.append(idx)
    
    having = history.groupby(['id', 'date']).sum().reset_index()[condition2].iloc[:,cur_index].values[0]
    for i in range(len(nutri_std)):
      having[i] = round((having[i] / nutri_std[i])*100, 2)
    
    for i in range(len(nutri_name)):
          nutri_name[i] += unit[i]
    
    having = list(having)
    nutri_name = list(nutri_name)
    having_list.append(having)
    nutri_name_list.append(nutri_name)
  
  # 질병별 섭취 영양소 그래프 이름 설정 부분
  for idx in range(len(disease_list)):
      disease_list[idx] += ' 주의할 성분 섭취량'

  return templates.TemplateResponse("history.html", {"request": request, 'nutri_list':nutri_list, 'nutri_name_list':nutri_name_list, 'having_list':having_list, 
                                                     'disease_list':disease_list})

# manual.html 반환
@app.get('/use', response_class=HTMLResponse)
async def get_use(request: Request):
  return templates.TemplateResponse("manual.html", {"request": request})