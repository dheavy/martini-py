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

WORKDIR /app

# requirements should be added before code, to leverage Docker cache
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY iac/docker-entrypoint.sh ./docker-entrypoint.sh
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

COPY iac/celery/worker/start.sh ./start-celery-worker.sh
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' ./start-celery-worker.sh
RUN chmod +x ./start-celery-worker.sh

COPY iac/celery/beat/start.sh ./start-celery-beat.sh
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' ./start-celery-beat.sh
RUN chmod +x ./start-celery-beat.sh

COPY iac/celery/flower/start.sh ./start-celery-flower.sh
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' ./start-celery-flower.sh
RUN chmod +x ./start-celery-flower.sh

COPY iac/django/start.sh ./start.sh
# process line endings for Windows, convert to UNIX format
RUN sed -i 's/\r$//g' ./start.sh
RUN chmod +x ./start.sh

COPY martini ./martini

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
