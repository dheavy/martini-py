FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
  # deps for Python packages building
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # additional dependencies (useful for debugging Celery tasks)
  && apt-get install -y telnet netcat \
  # cleaning
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# requirements should be added before code, to leverage Docker cache
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY iac/entrypoint /entrypoint
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY iac/start /start
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY iac/celery/worker/start /start-celery-worker
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' /start-celery-worker
RUN chmod +x /start-celery-worker

COPY iac/celery/beat/start /start-celery-beat
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' /start-celery-beat
RUN chmod +x /start-celery-beat

COPY iac/celery/flower/start /start-celery-flower
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' /start-celery-flower
RUN chmod +x /start-celery-flower

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
