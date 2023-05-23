FROM python:3.11-slim

RUN apt update && apt install -y python3-psycopg2

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

CMD ["python", "gcore.py"]
