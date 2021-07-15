FROM python:3

RUN mkdir -p /opt/src/votingstation
WORKDIR /opt/src/votingstation

COPY UIP/applicationZ.py ./application.py
COPY UIP/configuration.py ./configuration.py
COPY UIP/models.py ./models.py
COPY UpravljanjeKorisnickimNalozima/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
#ENTRYPOINT [ "sleep" , "1200"]
ENV PYTHONPATH="/opt/src/votingstation"
ENTRYPOINT ["python","./application.py"]