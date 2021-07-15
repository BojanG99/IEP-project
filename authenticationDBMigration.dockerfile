FROM python:3

RUN mkdir -p /opt/src/authentication

WORKDIR /opt/src/authentication

COPY UpravljanjeKorisnickimNalozima/migrate.py ./migrate.py
COPY UpravljanjeKorisnickimNalozima/configuration.py ./configuration.py
COPY UpravljanjeKorisnickimNalozima/models.py ./models.py
COPY UpravljanjeKorisnickimNalozima/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
#ENTRYPOINT [ "sleep" , "1200"]

ENTRYPOINT ["python","./migrate.py"]