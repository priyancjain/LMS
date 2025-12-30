web: uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers
release: python -c "from models import init_db; init_db()"
