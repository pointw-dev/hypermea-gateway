FROM python:3.9-slim

ENV HY_API_PORT=80
EXPOSE 80

WORKDIR app
COPY hypermea-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hypermea-gateway .

CMD ["python", "run.py"]
