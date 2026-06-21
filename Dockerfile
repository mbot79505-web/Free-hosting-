FROM python:3.8-slim

WORKDIR /app

RUN pip install --no-cache-dir jupyterlab flask

COPY app.py /app/app.py
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV PORT=8080

EXPOSE 8080

CMD ["/app/start.sh"]
