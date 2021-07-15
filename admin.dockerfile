FROM python:3

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin

COPY UIP/applicationA.py ./application.py
COPY UIP/configuration.py ./configuration.py
COPY UIP/models.py ./models.py
COPY UpravljanjeKorisnickimNalozima/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
#ENTRYPOINT [ "sleep" , "1200"]
ENV PYTHONPATH="/opt/src/admin"
ENTRYPOINT ["python","./application.py"]