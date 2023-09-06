FROM python:3.11-slim-bookworm
LABEL authors="cloud441"

RUN mkdir /app
COPY src/web_app/ /app
COPY config/web_app/requirement.txt .

RUN pip install --no-cache-dir -r requirement.txt

WORKDIR app

EXPOSE 5000

CMD ["python", "web_app.py"]