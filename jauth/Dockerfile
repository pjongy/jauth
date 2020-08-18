FROM python:3.7

ARG WORKER_COUNT
ENV WORKER_COUNT ${WORKER_COUNT}

ADD jauth /jauth

RUN pip3 install -r /jauth/requirements.txt --no-cache-dir
CMD gunicorn jauth.application:application --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornWebWorker --workers=$WORKER_COUNT --logger-class jauth.util.logger.gunicorn.CustomLogger --access-logfile -
EXPOSE 8080