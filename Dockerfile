FROM python:3.9

WORKDIR /root/.pip
COPY pip.ini pip.conf

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["-u", "main.py"]
