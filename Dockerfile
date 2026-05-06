FROM python:3.11-slim
WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["python", "web/app.py", "--host", "0.0.0.0", "--port", "8000"]
