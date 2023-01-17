FROM python:3.9

ARG NEXUS_LOGIN_USR
ARG NEXUS_LOGIN_PSW

ENV NEXUS_LOGIN_USR=${NEXUS_LOGIN_USR}
ENV NEXUS_LOGIN_PSW=${NEXUS_LOGIN_PSW}
ENV PYTHONUNBUFFERED=1

WORKDIR /root/.pip
#COPY pip.ini pip.conf
RUN printf "[global]\nindex-url=http://${NEXUS_LOGIN_USR}:${NEXUS_LOGIN_PSW}@myplan.ddns.net:8081/repository/pypi-repos/simple\ntrusted-host=myplan.ddns.net" > pip.conf

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["-u", "main.py"]
