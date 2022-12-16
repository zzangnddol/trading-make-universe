FROM python:3.9

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["main.py"]
ENTRYPOINT ["python3"]
