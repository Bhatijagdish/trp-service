FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
USER root
COPY ./second_requirements.txt /app
RUN exec bash
RUN #python3 -m pip install --upgrade pip
RUN #python3 -m pip install -r second_requirements.txt
COPY ./app /app
RUN uvicorn main:app  --host 0.0.0.0 --port 8000