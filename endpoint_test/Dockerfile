FROM python:3.9

ADD jauth /jauth
RUN pip3 install -r /jauth/requirements.txt

ADD endpoint_test /endpoint_test
CMD gunicorn endpoint_test.jauth.application:application \
    --bind 0.0.0.0:8080 \
    --worker-class aiohttp.GunicornWebWorker \
    --workers=$WORKER_COUNT \
    --access-logfile log.txt \
    --daemon \
    && python3 -m endpoint_test.tester \
    && cat log.txt