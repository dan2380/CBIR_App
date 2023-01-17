#syntax=docker/dockerfile:1
FROM python:3.8
COPY requirements.txt requirements.txt
ENV DISPLAY=host.docker.internal:0.0
RUN pip install --upgrade pip && \
pip install tk && \
pip install --no-cache-dir -r requirements.txt && \
xhost + 127.0.0.1
COPY . .
CMD ["python", "./python/ImageViewer.py"]