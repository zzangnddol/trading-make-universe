FROM python:3.9

ARG NEXUS_LOGIN_USR
ARG NEXUS_LOGIN_PSW

ENV NEXUS_LOGIN_USR=${NEXUS_LOGIN_USR}
ENV NEXUS_LOGIN_PSW=${NEXUS_LOGIN_PSW}

WORKDIR /root/.pip
COPY pip.ini pip.conf

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["-u", "main.py"]
