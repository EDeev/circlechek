FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY code/ code/
RUN useradd --create-home --uid 1000 app \
    && mkdir -p data/circles data/video_notes data/videos \
    && chown -R app:app /app
USER app
VOLUME ["/app/data"]

# пути к данным в коде — относительно папки code/ (../data)
WORKDIR /app/code
CMD ["python", "bot.py"]
