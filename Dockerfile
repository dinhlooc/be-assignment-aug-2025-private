FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*


WORKDIR /code

COPY requirements.txt .
COPY requirements-dev.txt .


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . .


EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]