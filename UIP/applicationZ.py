from flask import Flask, request, jsonify;
from configuration import Configuration;
from models import database,IzborUcesnik,UcesnikIzbora,Izbor,Glas;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from datetime import  datetime;
from dateutil import parser
import json;
import csv;
import io;
import os
redishost=os.environ["redishost"]
from redis import Redis;

application = Flask ( __name__ );
application.config.from_object ( Configuration );


jwt = JWTManager ( application );
@application.route ( "/vote", methods = ["POST"] )
@jwt_required ()
def vote ( ):
    identity = get_jwt_identity();
    refreshClaims = get_jwt();
    try:
        if(not(request.files["file"])):
            return jsonify(message="Field file missing."),400
    except:
        return jsonify(message="Field file is missing."), 400
    content = request.files["file"].stream.read().decode("utf-8");
    stream = io.StringIO(content);
    reader = csv.reader(stream);

    comments = [];
    linija=-1;
    rows=[]
    for row in reader:
        linija+=1;
        rows.append(row)
        if (len(row)!=2):
            return jsonify(message="Incorrect number of values on line "+str(linija)+"."), 400


    linija=-1;
    for row in rows:
        linija+=1;
        try:
            if ((int(row[1])) < 1 or row[1] == ""):
                return jsonify(message="Incorrect poll number on line " + str(linija) + "."), 400
        except:
            return jsonify(message="Incorrect poll number on line " + str(linija) + "."), 400

    with Redis(host=redishost) as redis:
        for row in rows:
            jsonobj={
                "guid":row[0],
                "rb":row[1],
                "jmbg":refreshClaims["jmbg"]
            }
            redis.publish(Configuration.REDIS_VOTE_LIST, row[0]+","+row[1]+","+refreshClaims["jmbg"] );


    return "good",200


if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True,host="0.0.0.0" ,port = 5003 );