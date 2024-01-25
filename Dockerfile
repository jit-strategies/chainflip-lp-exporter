FROM python:3.12-alpine

WORKDIR /app
COPY ./requirements.txt .

RUN pip install -r requirements.txt
COPY ./chainflip-lp-exporter.py .

ENTRYPOINT ["python3", "chainflip-lp-exporter.py"]