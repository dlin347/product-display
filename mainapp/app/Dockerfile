FROM python:3.13

ADD requirements.txt .
ADD html html
ADD static static
ADD app.py ..

RUN pip install -r ./requirements.txt
RUN python -m playwright install
RUN playwright install-deps

RUN apt-get update && apt-get install -y tzdata && apt-get clean

ENTRYPOINT ["python"]
CMD ["./app.py"]