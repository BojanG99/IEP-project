FROM python:3

RUN mkdir -p /opt/src/voting

WORKDIR /opt/src/voting

COPY UIP/migrate.py ./migrate.py
COPY UIP/configuration.py ./configuration.py
COPY UIP/models.py ./models.py
COPY UpravljanjeKorisnickimNalozima/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
#ENTRYPOINT [ "sleep" , "1200"]

ENTRYPOINT ["python","./migrate.py"]