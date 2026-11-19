FROM python:3.12-slim
WORKDIR /app
COPY measurement/requirements.txt /app/measurement/requirements.txt
RUN pip install --no-cache-dir -r measurement/requirements.txt && useradd --uid 10001 --create-home counter && mkdir /data && chown counter:counter /data
COPY measurement/ /app/measurement/
COPY _site/ /app/_site/
USER counter
ENV CN_DB=/data/measurement.sqlite3 CN_SITE=/app/_site PYTHONDONTWRITEBYTECODE=1
VOLUME /data
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--access-logfile", "/dev/null", "--error-logfile", "-", "measurement.collector:application"]
