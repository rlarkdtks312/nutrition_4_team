# Get the Fast API image with python version 3.9
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Create the directory for the container
WORKDIR ./

# 현제 디렉터리에 있는 파일들을 이미지 내부 /app 디렉터리에 추가
ADD ./ ./

# Install the dependencies
RUN python -m pip install --upgrade pip
RUN pip install -r ./requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
# Run by specifying the host and port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]