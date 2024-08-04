# FastAPI-boilerplate

boilerplate code for starting a fastapi project

## Features:
  - async sqlalchemy session
  - setup for tests using pytest

## Instructions:
1) Install Dependencies
```
poetry shell
poetry install
```

2) Create / Run Migrations
```
alembic revision --autogenerate -m <migration_name>
alembic upgrade heads
```

3) Start server
```
fastapi dev app/main.py
```

  
  
