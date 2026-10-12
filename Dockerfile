FROM python:3.12-alpine

WORKDIR /app

COPY . /app

RUN chmod -R 755 /app

ENV PORT=8092
EXPOSE 8092

CMD ["python", "server.py"]
