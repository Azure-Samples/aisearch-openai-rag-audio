FROM python:3.12-bullseye

WORKDIR /app

COPY ./ /app

RUN python -m pip install -r requirements.txt

RUN python -m pip install gunicorn

CMD ["python3", "-m", "gunicorn", "app:create_app", "-b", "0.0.0.0:8000", "--worker-class", "aiohttp.GunicornWebWorker"]