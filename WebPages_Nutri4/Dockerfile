# Get the Fast API image with python version 3.9
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Create the directory for the container
WORKDIR ./
COPY ./ ./

# Install the dependencies
RUN python -m pip install --upgrade pip
RUN pip install -r ./requirements.txt
RUN apt-get install
RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx

# Run by specifying the host and port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
