# Stage 1: Build the Vite app
FROM node:20-slim AS build-stage

# Set the working directory inside the container
COPY frontend ./

WORKDIR /frontend
RUN npm install
RUN npm run build

# Stage 2: Serve the built app with a static file server
FROM python:3.12-slim AS production-stage

WORKDIR /app
COPY --from=build-stage /backend/static /app/static
COPY ./backend/ /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python -m pip install -r requirements.txt

RUN python -m pip install gunicorn

CMD ["python3", "-m", "gunicorn", "app:create_app", "-b", "0.0.0.0:8000", "--worker-class", "aiohttp.GunicornWebWorker"]
