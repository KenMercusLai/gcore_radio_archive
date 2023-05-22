FROM python:3.11-slim

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

CMD ["python", "gcore.py"]
