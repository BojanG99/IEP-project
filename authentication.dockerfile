FROM python:3

RUN mkdir -p /opt/src/authentication

WORKDIR /opt/src/authentication

COPY UpravljanjeKorisnickimNalozima/application.py ./application.py
COPY UpravljanjeKorisnickimNalozima/configuration.py ./configuration.py
COPY UpravljanjeKorisnickimNalozima/models.py ./models.py
COPY UpravljanjeKorisnickimNalozima/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
#ENTRYPOINT [ "sleep" , "1200"]
ENV PYTHONPATH="/opt/src/authentication"
ENTRYPOINT ["python","./application.py"]