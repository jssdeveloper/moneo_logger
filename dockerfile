FROM python:3.11-alpine

WORKDIR /app
COPY . .

RUN pip install requests
CMD ["python", "script.py"]