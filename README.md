# 영양4조

### 프로젝트 소개

- 멀티캠퍼스 빅데이터 기반 지능형 서비스 개발(7,8회차) 기업요구사항기반의 문제해결PJT
- 제목: WI-ME (wisdom menu), 개인 맟춤형 식단 필터링 서비스
- 목적
  - 일상 속 행동을 건강하게 바꾸는 것에 도전
  - 서비스를 통하여 영양소별 섭취량 조정에 도움 및 균형잡힌 식단 관리를 통하여 건강 관리 실현
  - 개인별 건강상태에 맞는 음식을 선정하는데에 도움을 주고자 함

### 빠른 시작 예제

#### 설치 및 데모 실행

- yolov5 수정 폴더를 nutrition4 폴더 내로 이동

- 아래 명령어 실행

  ```python
  git clone https://github.com/rlarkdtks312/nutrition_4_team.git
  
  cd nutrition4
  pip install -r requirements.txt
  
  cd yolo
  pip install -r requirements.txt
  
  cd ../
  uvicorn main:app --reload
  ```

- 데모 사용법

  1. 카카오 계정 설정 &rarr; 개인 보안 &rarr; 카카오계정 &rarr; 내정보 관리 &rarr; 생일, 성별 이용 동의
  2. http://localhost:8000
  3. 접속 후 좌측 상단  사용법 참고 및 아래 사용 예시 참고

### 사용 예시

- 로그인 및 사용방법 링크 페이지

![1](README.assets/1-16514710561801.png)

- kakao 로그인 페이지
  - 선택 동의 내용까지 동의 하셔야 정확한 정보를 얻을 수 있습니다.



![2](README.assets/2-16514710652732-16514710682813.png)

- 식단 사진 및 질병 체크
  - 식단 사진 업로드
  - 5대 만성 질환 중 선택
  - 추가 및 수정 내용
    - 체크 박스 형태의 다중 질환 선택 기능 추가
    - 아침, 점심, 저녁 구분 기능 추가

![3](README.assets/3-16514710878384.png)

- 식단 사진 업로드 예시

![4](README.assets/4-16514710967885.png)

- 섭취 음식명, 한끼 기준 영양소, 주의 성분, 경고 메세지 정보 제공
  - 히스토리 기능 버튼 사용하여 히스토리 기능 이용 가능
  - 경고 메시지를 팝업 창 or TTS 형태로 변경 예정

![5](README.assets/5-16514715744286.png)

![6](README.assets/6-16514715840827.png)

![7](README.assets/7-16514716133368.png)

![8](README.assets/8.png)

![9](README.assets/9-165147169703711.png)

- 일일 섭취 영양소 기준, 일일 기준 주의할 성분 그래프 정보 제공
  - 차후 1주일, 한 달 주기의 히스토리를 추가할 예정

![9](README.assets/10-165147166367210.png)

![11](README.assets/11.png)
