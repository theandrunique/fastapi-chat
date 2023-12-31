FROM python:3.11-alpine

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0"]