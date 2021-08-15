FROM python:3.9

ADD jauth /jauth
ADD endpoint_test/jauth /endpoint_test/jauth

RUN pip3 install -r /jauth/requirements.txt --no-cache-dir
CMD gunicorn endpoint_test.jauth.application:application \
    --bind 0.0.0.0:8080 \
    --worker-class aiohttp.GunicornWebWorker \
    --workers=$WORKER_COUNT \
    --logger-class jauth.util.logger.gunicorn.CustomLogger \
    --access-logfile - \
    --daemon \
    && python3 -m endpoint_test.tester
