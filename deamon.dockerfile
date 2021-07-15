FROM python:3

RUN mkdir -p /opt/src/deamon

WORKDIR /opt/src/deamon

COPY UIP/proccess.py ./proccess.py
COPY UIP/configuration.py ./configuration.py
COPY UIP/models.py ./models.py
COPY UpravljanjeKorisnickimNalozima/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
#ENTRYPOINT [ "sleep" , "1200"]
ENV PYTHONPATH="/opt/src/deamon"
ENTRYPOINT ["python","./proccess.py"]