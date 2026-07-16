FROM python:3.14

LABEL authors="Ivan"

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry==1.8.0 && poetry config virtualenvs.create false && poetry update

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
