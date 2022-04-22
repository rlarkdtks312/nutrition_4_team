from typing import Optional
from urllib import response
from fastapi import FastAPI, Response, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Cookie, FastAPI
from PIL import Image

import my_func
import requests
import json

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/img', StaticFiles(directory='img'), name='img')
app.mount('/image', StaticFiles(directory='image'), name='image')
app.mount('/pred_image', StaticFiles(directory='pred_image'), name='pred_image')
templates = Jinja2Templates(directory="templates")

global gkey

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
async def user_info(response: Response, request: Request, KEY: Optional[str] = Cookie(None)):
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
    # 업로드한 {img_s.filename}으로 image폴더에 파일 저장하기
    file_location = f"./image/{img_s.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(img_s.file.read())
    
    # 로그인 정보 가져오기
    with open('data/data.json', "r") as json_file:
      json_data = json.load(json_file)
      
    email = json_data['email']
    gender = json_data['gender']
    age = json_data['age_range']

    my_func.pred(file_location)

    pred_file = file_location.split('/')[-1]

    pred_fild_path = "../pred_image/result/"+pred_file
    
    # my_func.make_pickle()
    # pickle = my_func.load_pickle()
    food_list = my_func.get_result()
    print('asdsadsadasddsasadsad', food_list)
    results_text = '나트륨 조심하세요'
    
    return templates.TemplateResponse("print.html", {"request": request, 'food_names': food_list, 'result' : results_text, 
                                                     'email':email, 'gender':gender, 'age_range':age, 
                                                     'disease':disease, 'img_path':pred_fild_path})