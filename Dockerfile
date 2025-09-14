FROM python:3.11-slim
LABEL "language"="python"
LABEL "framework"="flask"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /tmp/podcast_files/audio /tmp/podcast_files/transcripts
RUN mkdir -p public && mv *.html *.css *.js *.ico public/ 2>/dev/null || true
EXPOSE 8080
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "app:app"]