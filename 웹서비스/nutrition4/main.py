from typing import Optional
from urllib import response
from fastapi import FastAPI, Response, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Cookie, FastAPI
from PIL import Image

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

@app.get('/', response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request })


@app.get("/kakao")
async def kakao():
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    REDIRECT_URI = "http://localhost:8000/oauth"
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    response = RedirectResponse(url)
    return response

@app.get('/oauth')
async def kakaoAuth(response: Response, code: Optional[str]="NONE"):
    REST_API_KEY = "7f4c07a7aabae79cb7848959a5d66f37"
    REDIRECT_URI = 'http://localhost:8000/oauth'
    _url = f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&code={code}&redirect_uri={REDIRECT_URI}'
    _res = requests.post(_url)
    _result = _res.json()
    response = RedirectResponse('http://localhost:8000/info/{}'.format(_result['access_token']))
    return response

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

@app.post('/print', response_class=HTMLResponse)
async def get_page(request: Request, img_s: UploadFile = File(...), disease : str= Form(...)):
    ## 업로드한 {img_s.filename}으로 image폴더에 파일 저장하기
    file_location = f"./image/{img_s.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(img_s.file.read())
    
    ## 로그인 정보 가져오기
    with open('data/data.json', "r") as json_file:
      json_data = json.load(json_file)
      
    email = json_data['email']
    if json_data['gender'] == 'male':
      gender = '남자'
    else:
      gender = '여자'
    age_range = json_data['age_range']

    ## 업로드한 이미지 파일 예측 수행 및 음식 리스트 생성
    my_func.pred(file_location)

    pred_file = file_location.split('/')[-1]
    pred_fild_path = "../pred_image/result/"+pred_file
    food_list = my_func.get_result()
    
    ## 예측된 음식의 영양성분 가져와서 id_record db에 넣기
    # 현재 시간 가져오기
    now = datetime.datetime.now()
    cur_time = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
    
    nutri_add2 = my_func.nutri_add(food_list)
    record_list = [email, cur_time, gender, age_range]
    
    for nutri in nutri_add2.values():
          record_list.append(nutri)
  
    my_func.add_record([record_list])
    
    ## histoty histogram
    nutri_reco = my_func.nutri_reco()
    condition = ((nutri_reco['성별'] == gender) & (nutri_reco['연령'] == age_range))
    nutri_reco_id = nutri_reco[condition]['권장(g/일)']
    nutri_reco_id = list(nutri_reco_id)
    history = my_func.id_history([email])
    nutri_list = list(history.groupby('id').sum().iloc[0])
    energe = my_func.nutri_limit(['비만', gender, age_range])
    
    for i in range(len(nutri_reco_id)):
          if i == 0:
            nutri_list[i] = round((nutri_list[i] / list(energe['섭취기준\n(1일)'])[0])*100, 2)  
          else:
            nutri_list[i+1] = round((nutri_list[i+1] / nutri_reco_id[i])*100, 2)
    dise_nutri = my_func.nutri_limit([disease, gender, age_range])
    dise_labels = list(dise_nutri['영양성분'])
    dise_datas = list(dise_nutri['섭취기준\n(1일)'])

    message = '소금 그만!!'
    return templates.TemplateResponse("print.html", {"request": request, 'food_names': food_list, 
                                                     'email':email, 'gender':gender, 'age_range':age_range, 
                                                     'disease':disease, 'img_path':pred_fild_path, 'nutri_list':nutri_list[:-2], 
                                                     'nutri_list2':nutri_list[:-2], 'dise_labels':dise_labels, 'dise_datas':dise_datas,
                                                     'message':message
                                                     }
                                      )
    
# @app.post('/his', response_class=HTMLResponse)
# async def get_history(request: Request, disease : str= Form(...)):
#   with open('data/data.json', "r") as json_file:
#     json_data = json.load(json_file)
    
#     email = json_data['email']
#     if json_data['gender'] == 'male':
#       gender = '남자'
#     else:
#       gender = '여자'
#     age_range = json_data['age_range']
  
#   ## histoty histogram
#     nutri_reco = my_func.nutri_reco()
#     condition = ((nutri_reco['성별'] == gender) & (nutri_reco['연령'] == age_range))
#     nutri_reco_id = nutri_reco[condition]['권장(g/일)']
#     nutri_reco_id = list(nutri_reco_id)
#     history = my_func.id_history([email])
#     nutri_list = list(history.groupby('id').sum().iloc[0])
#     energe = my_func.nutri_limit(['비만', gender, age_range])
    
#     for i in range(len(nutri_reco_id)):
#           if i == 0:
#             nutri_list[i] = round((nutri_list[i] / list(energe['섭취기준\n(1일)'])[0])*100, 2)  
#           else:
#             nutri_list[i+1] = round((nutri_list[i+1] / nutri_reco_id[i])*100, 2)
#     dise_nutri = my_func.nutri_limit([disease, gender, age_range])
#     dise_labels = list(dise_nutri['영양성분'])
#     dise_datas = list(dise_nutri['섭취기준\n(1일)'])
#     temp1 = []
#     temp2 = []
#     for i in dise_labels:
#           temp1.append(i)
#     for i in dise_datas:
#           temp2.append(i)
    
#     message = '소금 조심!'
    
#   return templates.TemplateResponse("history.html", {"request": request, 'nutri_list':nutri_list[:-2], 
#                                                      'nutri_list2':nutri_list[:-2], 'dise_labels':dise_labels[0], 'dise_datas':dise_datas[0],
#                                                      'temp1':temp1, 'temp2':temp2, 'message':message})