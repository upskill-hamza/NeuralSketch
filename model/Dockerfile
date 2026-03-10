
FROM python:3.11-slim

WORKDIR /app/model

COPY model/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY model/ ./

VOLUME ["/app/model/data", "/app/model/weights"]

CMD ["python", "train.py"]
