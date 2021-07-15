from flask import Flask, request, jsonify;
from configuration import Configuration;
from models import database,IzborUcesnik,UcesnikIzbora,Izbor,Glas;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from datetime import  datetime;
from dateutil import parser


application = Flask ( __name__ );
application.config.from_object ( Configuration );

def provjera_JMBG(jmbg):
    if (len(jmbg) != 13):
        return False;
    m=0;
    dan=jmbg[0]+jmbg[1];
    if((int)(dan)>31 or (int)(dan)==0 ):
        return False;
    mjesec=jmbg[2]+jmbg[3];
    if ((int)(mjesec) > 12 or (int)(mjesec) == 0):
        return False;
    m = 11 - ((7 * ((int)(jmbg[0]) + (int)(jmbg[6])) + 6 * ((int)(jmbg[1]) + (int)(jmbg[7])) + 5 * ((int)(jmbg[2]) + (int)(jmbg[8])) + 4 * ((int)(jmbg[3]) + (int)(jmbg[9])) + 3 * ((int)(jmbg[4]) + (int)(jmbg[10])) + 2 * ((int)(jmbg[5]) + (int)(jmbg[11]))) % 11);

    if(m >= 10):
        return ((int)(jmbg[12])) == 0;
    return ((int)(jmbg[12])) == m;

def provjeri_Sifru(password):
    if(len(password)<8):
        return False;
    veliko=False;
    malo=False;
    cifra=False;
    for a in password:
        if( a.isupper()):
            veliko=True;
        elif(a.islower()):
            malo=True;
        elif(a.isdigit()):
            cifra=True;
    return malo and veliko and cifra;
def provjeri_Email(email):
    tacka=False;
    luda=False;
    for a in email:
        if(a=='@'):
            luda=True;
        if(a=='.'):
            tacka=True;



    return luda and tacka and (email[len(email)-1]!='.')and (email[len(email)-2]!='.')
def DHondt(ucesnik):
    izbor = Izbor.query.filter(Izbor.id == ucesnik.izborId).first();
    myId=-1;
    brojGlasova=[];
    brojMandata=[]
    i=0;
    ukupnoGlasova = Glas.query.filter(and_(Glas.izborId == izbor.id, Glas.validan == True)).count();
    ucesniciIzbora=IzborUcesnik.query.filter(IzborUcesnik.izborId==izbor.id);
    for ucesnikIzbora in ucesniciIzbora:
        brojGlasovaUcesnik=Glas.query.filter(and_(Glas.izborId==izbor.id,Glas.poolNum==ucesnikIzbora.poolNum,Glas.validan==True)).count()
        procenat=brojGlasovaUcesnik/ukupnoGlasova*100;
        print("Procenat "+str(procenat)+" : "+str(ucesnikIzbora.ucesnikId)+" : "+str(ucesnikIzbora.poolNum)+ " broj glasova je "+ str(Glas.query.filter(and_(Glas.izborId==izbor.id,Glas.poolNum==ucesnikIzbora.poolNum,Glas.validan==True)).count()))
        if(procenat>=5):
            if ucesnikIzbora.ucesnikId == ucesnik.ucesnikId:
                myId = i
            brojGlasova.append(brojGlasovaUcesnik)
            brojMandata.append(0)

            i+=1

    if(myId==-1):
        return 0;

    myMandats=0;

    for i in range(1,251):
        k=-1
        max=-1
        for j in range(0,len(brojGlasova)):
            if max<(brojGlasova[j]/(1+brojMandata[j])):
                max=(brojGlasova[j]/(1+brojMandata[j]))
                k=j
        brojMandata[k]+=1


    return brojMandata[myId]
def greska(duplikat):
    if(duplikat==True):
        return "Duplicate ballot."
    return "Invalid poll number."
def rezultat(ucesnik):
    izbor=Izbor.query.filter(Izbor.id==ucesnik.izborId).first();
    if(izbor.individual):
        rez=0
        try:
            rez= Glas.query.filter(and_(Glas.izborId==izbor.id,Glas.poolNum==ucesnik.poolNum,Glas.validan==True)).count()/Glas.query.filter(and_(Glas.izborId==izbor.id,Glas.validan==True)).count();
        except:
            rez=0;
        return round(rez,2);
    else:
        return DHondt(ucesnik);
@application.route ( "/register", methods = ["POST"] )
def register ( ):
    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );
    forename = request.json.get ( "forename", "" );
    surname = request.json.get ( "surname", "" );
    jmbg = request.json.get("jmbg", "");
    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;
    forenameEmpty = len ( forename ) == 0;
    surnameEmpty = len ( surname ) == 0;
    jmbgEmpty = len(jmbg) == 0;

    if (jmbgEmpty):
        return jsonify(message="Field jmbg is missing."), 400
    if (forenameEmpty):
        return jsonify(message="Field forename is missing."),400
    if (surnameEmpty):
        return jsonify(message="Field surname is missing."), 400
    if (emailEmpty):
        return jsonify(message="Field email is missing."), 400
    if (passwordEmpty):
        return jsonify(message="Field password is missing."), 400

    result = parseaddr ( email );

    if (not (provjera_JMBG(jmbg))):
        return jsonify(message="Invalid jmbg."),400


    if ( len ( result[1] ) == 0  or not(provjeri_Email(email))):
        return jsonify(message="Invalid email."),400

    if (not (provjeri_Sifru(password))):
        return jsonify(message="Invalid password."),400


    return "", 200

jwt = JWTManager ( application );

@application.route ( "/login", methods = ["POST"] )
def login ( ):
    email = request.json.get ( "email", "" );
    password = request.json.get ( "password", "" );

    emailEmpty = len ( email ) == 0;
    passwordEmpty = len ( password ) == 0;

    if ( emailEmpty ):
        return jsonify(message="Field email is missing."), 400

    if (passwordEmpty):
        return jsonify(message="Field password is missing."), 400


    #user = User.query.filter ( and_ ( User.email == email, User.password == password ) ).first ( );

    result = parseaddr(email);

    if (len(result[1]) == 0 or not (provjeri_Email(email))):
        return jsonify(message="Invalid email."), 400
    #if ( not user ):
        return jsonify(message="Invalid credentials."), 400 ;

    ##additionalClaims = {
     #       "jmbg": user.jmbg,
      #      "forename": user.forename,
       #     "surname": user.surname,
        #    "email": user.email,
         #   "password": user.password,
          #  "role": str(user.role)
    #}

    #accessToken = create_access_token ( identity = user.email, additional_claims = additionalClaims );
    #refreshToken = create_refresh_token ( identity = user.email, additional_claims = additionalClaims );

    # return Response ( accessToken, status = 200 );
    #return jsonify ( accessToken = accessToken, refreshToken = refreshToken ),200
    return "",200;

@application.route ( "/getParticipants", methods = ["GET"] )
@jwt_required ( )
def getP ( ):
    identity = get_jwt_identity();
    refreshClaims = get_jwt();

    ucesnici= UcesnikIzbora.query.all();



    if(refreshClaims["role"]!="administrator"):
      #  User.query.filter(User.email == email).delete();
       # database.session.commit();
        return "ne moze",200;
    #return "ne moze", 200;

    return jsonify(participants=[ {"id":obj.id,"name":obj.ime,"individual":obj.individual} for obj in ucesnici]),200;

@application.route ( "/createParticipant", methods = ["POST"] )
@jwt_required ()
def createP ( ):
    identity = get_jwt_identity ( );
    refreshClaims = get_jwt ( );
    individual = request.json.get("individual", "");
    name = request.json.get("name", "");

    nameEmpty = len(name) == 0;
    individualEmpty = len(str(individual)) == 0;

    if (nameEmpty):
        return jsonify(message="Field name is missing."), 400

    if (individualEmpty):
        return jsonify(message="Field individual is missing."), 400


    if(refreshClaims["role"]!="administrator"):
        return jsonify(message="You dont have privilige"),400;

    ucesnik=UcesnikIzbora(ime=name,individual=individual);
    database.session.add(ucesnik);
    database.session.commit();

    return jsonify(id= ucesnik.id), 200;


@application.route ( "/createElection", methods = ["POST"] )
@jwt_required ()
def createE ( ):
    identity = get_jwt_identity ( );
    refreshClaims = get_jwt ( );
    individual = request.json.get("individual", "");
    start = request.json.get("start", "");
    end = request.json.get("end", "");
    participants = request.json.get("participants", "");
    startEmpty = len(start) == 0;
    endEmpty=len(end)==0;
    participantsEmpty=str(participants)=="";
    individualEmpty = len(str(individual)) == 0;

    if (startEmpty):
        return jsonify(message="Field start is missing."), 400

    if (endEmpty):
        return jsonify(message="Field end is missing."), 400

    if (individualEmpty):
        return jsonify(message="Field individual is missing."), 400

    if (participantsEmpty):
        return jsonify(message="Field participants is missing."), 400




    try:
        startDate = parser.parse(start)
    except :
        return jsonify(message="Invalid date and time."), 400

    try:
        endDate = parser.parse(end)
    except:
        return jsonify(message="Invalid date and time."), 400
    if(not startDate):
        return jsonify(message="Invalid date and time."), 400
    if (not endDate):
        return jsonify(message="Invalid date and time."), 400
    if(endDate<startDate):
        return jsonify(message="Invalid date and time."), 400
    elections = Izbor.query.all();
    for el in elections:
        if (el.start >= startDate and el.start < endDate):
            return jsonify(message="Invalid date and time."), 400
        if (el.end > startDate and el.end < endDate):
            return jsonify(message="Invalid date and time."), 400
        if (el.start <= startDate and el.end >= endDate):
            return jsonify(message="Invalid date and time."), 400

    if(refreshClaims["role"]!="administrator"):
        return jsonify(message="You dont have privilige"),400;

    if (len(participants)<3):
        return jsonify(message="Invalid participants."), 400
    for a in participants:
        if(not(UcesnikIzbora.query.filter(and_(UcesnikIzbora.id==a,UcesnikIzbora.individual==individual)).first())):
            return jsonify(message="Invalid participants."), 400





    election= Izbor(start=startDate,end=endDate,individual=individual);

    database.session.add(election);
    database.session.commit();
    i=1;
    for a in participants:
        ucesnikizbora=IzborUcesnik(izborId=election.id,ucesnikId=a,poolNum=i);
        database.session.add(ucesnikizbora);
        database.session.commit();
        i+=1;

    return jsonify(pollNumbers=[a for a in range(1,len(participants)+1)]), 200;


@application.route ( "/getElections", methods = ["GET"] )
@jwt_required ()
def getE():
    identity = get_jwt_identity();
    refreshClaims = get_jwt();

    ucesnici = Izbor.query.all();

    if (refreshClaims["role"] != "administrator"):
        return "ne moze", 400;

    return jsonify(
        elections=[{"id": obj.id, "start": obj.start.isoformat(), "end": obj.end.isoformat(),"individual":obj.individual,"participants":[{"id":obj1.id,"name":obj1.ime} for obj1 in obj.ucesnici]} for obj in ucesnici]), 200;



@application.route ( "/getResults", methods = ["GET"] )
@jwt_required ()
def getRes():
    identity = get_jwt_identity();
    refreshClaims = get_jwt();
    try:
        (request.args["id"])
    except:
        return jsonify(message="Field id is missing."), 400;

    id=(int)(request.args["id"])


    if (request.args["id"] == ""):
        return jsonify(message="Field id is missing."), 400;
    izbor = Izbor.query.filter(Izbor.id==id).first();
    if(not(izbor)):
        return jsonify(message="Election does not exist."), 400;

    if (izbor.start <= datetime.now() and izbor.end >= datetime.now()):
        return jsonify(message="Election is ongoing."), 400;

    ucesnici=izbor.ucesnici;
    glasovi=izbor.glasovi
    if (refreshClaims["role"] != "administrator"):
        return "ne moze", 400;


    allInvalidVotes=Glas.query.filter(and_(Glas.izborId==izbor.id,Glas.validan==False ));

    participanti=[]

    ucesnici = []
    sviucesnici = IzborUcesnik.query.all();
    for ucesnik in sviucesnici:
        if (ucesnik.izborId==izbor.id):
            ucesnici.append(ucesnik);
    for ucesnik in ucesnici:
        print(ucesnik.id);

        obj={"pollNumber": ucesnik.poolNum,"name":UcesnikIzbora.query.filter(UcesnikIzbora.id==ucesnik.ucesnikId).first().ime,"result":rezultat(ucesnik)}
        participanti.append(obj)
    return jsonify(
        #participants=[{"pollNumber": obj.id, "name": obj.start.isoformat(), "result": obj.end.isoformat()}for obj in ucesnici],
        participants=[obj for obj in participanti],
        invalidVotes=[{"electionOfficialJmbg":objq.jmbg,"ballotGuid":objq.guid,"pollNumber":objq.poolNum,"reason":greska(objq.duplikat)} for objq in allInvalidVotes]), 200;





if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True,host="0.0.0.0", port = 5001 );