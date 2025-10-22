FROM python:3.12.10-slim-bookworm

RUN apt-get update && apt-get install -y adb tzdata && apt-get clean

COPY requirements.txt .
COPY onoff.py .
COPY chromecasting.py .
COPY android_tv_rc /android_tv_rc

RUN pip install --root-user-action=ignore --upgrade pip
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

RUN mkdir -p /root/.android

ENV PYTHONPATH="/android_tv_rc/:${PYTHONPATH}"

CMD ["sh", "-c", "python ./onoff.py & python ./chromecasting.py"]