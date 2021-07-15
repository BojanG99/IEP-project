from redis import Redis;
from datetime import  datetime,timedelta;
from configuration import Configuration
from models import Glas,database,IzborUcesnik,Izbor
import pymysql
from flask import Flask
import time
from sqlalchemy import and_;
import os

application=Flask(__name__)
application.config.from_object(Configuration)
if ( __name__ == "__main__" ):
    database.init_app(application)
    application.app_context().push()
print("*")
bazastr=os.environ["DATABASE_URL"]
redishost=os.environ["redishost"]
#with Redis(host=redishost) as redis:

 #   kraj=False
  #  while not kraj:
   #     try:
    #        redis.publish("stiglo", "stiglo")
     #       connection = pymysql.connect(

      #          host=bazastr,
       #         user="root",
        #        password="root",
         #       database="voting",
          #      cursorclass=pymysql.cursors.DictCursor)
       #     if(not(connection)):
        #        time.sleep(30);
         #       continue
          #  kraj=True
        #except:
         #   time.sleep(30);


with Redis(host=redishost) as redis:

    print("*")
    sub=redis.pubsub()
    sub.subscribe("vote");
    mess = sub.get_message(timeout=1000)["data"]
    while(True):
        print("*")
        mess=sub.get_message(timeout=1000)["data"].decode('UTF-8').split(",");
           #

       #     izbori=[]
       #     izb=-1
       #     query="select * from izbori";
       #     cursor.execute(query)
          #  izbori=cursor.fetchall();

        #    find=False
         #   for izbor in izbori:

          #      if(izbor["start"]<=datetime.now() and izbor["end"]>=datetime.now()):
                    #print("provjera")
          #          izb=izbor;
        #            find=True;
         #           break;
        #    if(find==False):
        #        redis.publish("stiglo", "nema izbora")
         #       continue

           # query = "select * from `glasovi` where `guid`= %s";
        izbori=Izbor.query.all()
        izb=-1;
        find=False
        current_date_and_time=datetime.now()
        hours=2
        hours_added = timedelta(hours=hours)
        future_date_and_time = current_date_and_time + hours_added
        for izbor in izbori:
            redis.publish("stiglo", str(izbor.id))
            redis.publish("stiglo", str(future_date_and_time))
            if(izbor.start<=future_date_and_time and izbor.end>=future_date_and_time):
                izb=izbor;
                find=True;
                break;
        if(find==False):
            continue

           # cursor.execute(query,(mess[0]))
           # glas = cursor.fetchall();
        brojgl=Glas.query.filter(Glas.guid==mess[0]).count()





        if (brojgl!=0):
    #            izid = izb["id"];
     #           query1 = "Insert into `glasovi`(`jmbg`,`izborId`,`guid`,`validan`,`duplikat`,`poolNum`) values ( %s, %s, %s,false,true, %s)"
      #          polln = (int)(mess[1])
       #         cursor.execute(query1, (mess[2], izid, mess[0], polln));
        #        connection.commit()
         #       redis.publish("stiglo", "duplikat")
          #      continue;
            glas = Glas(guid=mess[0], jmbg=mess[2], izborId=izb.id, poolNum=int(mess[1]), validan=False, duplikat=True)
            database.session.add(glas);
            database.session.commit();
            continue
          #  izuc=IzborUcesnik.query.filter(IzborUcesnik.poolNum==int(mess[1]), IzborUcesnik.izborId==izb.id);

         #   prom=izb["id"]
         #
    #   query = f"select * from izborucesnik where poolNum={int(mess[1])} and izborId={prom}";
         #   cursor.execute(query)
         #   izuc = cursor.fetchall();
        broj=IzborUcesnik.query.filter(and_(IzborUcesnik.poolNum==(int(mess[1])),IzborUcesnik.izborId==izb.id)).count()
        if(broj==0):

    #            izid = izb["id"];
     #           query1 = "Insert into `glasovi`(`jmbg`,`izborId`,`guid`,`validan`,`duplikat`,`poolNum`) values ( %s, %s, %s,false,false, %s)"
      #          polln = (int)(mess[1])
       #         cursor.execute(query1, (mess[2], izid, mess[0], polln));
        #        connection.commit()
         #       redis.publish("stiglo", "nevazeci pollNum")
          #      continue;
            glas = Glas(guid=mess[0], jmbg=mess[2], izborId=izb.id, poolNum=int(mess[1]), validan=False, duplikat=False)
            database.session.add(glas);
            database.session.commit();
            continue

        glas = Glas(guid=mess[0], jmbg=mess[2], izborId=izb.id, poolNum=int(mess[1]), validan=True,duplikat=False)
        database.session.add(glas);
        database.session.commit();

        #    izid=izb["id"];

        #    query1="Insert into `glasovi`(`jmbg`,`izborId`,`guid`,`validan`,`duplikat`,`poolNum`) values ( %s, %s, %s,true,false, %s)"
        #    polln=(int)(mess[1])
        #    cursor.execute(query1,(mess[2],izid,mess[0],polln));
        #    connection.commit()
        #    redis.publish("stiglo", "dodato")
