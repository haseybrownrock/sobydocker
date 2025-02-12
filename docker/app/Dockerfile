FROM python:3.11-slim
WORKDIR /app
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["streamlit", "run", "home.py", "--server.port=8501", "--server.enableCORS=false"]