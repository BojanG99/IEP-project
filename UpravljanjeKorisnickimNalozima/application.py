from flask import Flask, request, Response, jsonify;
from configuration import Configuration;
from models import database, User;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;


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


@application.route ( "/", methods = ["GET"] )
def index ( ):
    return "Cao"

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

    user = User.query.filter(User.email == email).first();

    if (user):
        return jsonify(message="Email already exists."), 400


    user = User ( email = email, password = password, forename = forename, surname = surname ,jmbg=jmbg, roleId=2);
    database.session.add ( user );
    database.session.commit ( );

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


    user = User.query.filter ( and_ ( User.email == email, User.password == password ) ).first ( );

    result = parseaddr(email);

    if (len(result[1]) == 0 or not (provjeri_Email(email))):
        return jsonify(message="Invalid email."), 400
    if ( not user ):
        return jsonify(message="Invalid credentials."), 400 ;

    additionalClaims = {
            "jmbg": user.jmbg,
            "forename": user.forename,
            "surname": user.surname,
            "email": user.email,
            "password": user.password,
            "role": str(user.role)
    }

    accessToken = create_access_token ( identity = user.email, additional_claims = additionalClaims );
    refreshToken = create_refresh_token ( identity = user.email, additional_claims = additionalClaims );

    # return Response ( accessToken, status = 200 );
    return jsonify ( accessToken = accessToken, refreshToken = refreshToken ),200

@application.route ( "/delete", methods = ["POST"] )
@jwt_required ( )
def delete ( ):
    identity = get_jwt_identity();
    refreshClaims = get_jwt();

    email = request.json.get("email", "");

    emailEmpty = len(email) == 0;


    if (emailEmpty):
        return jsonify(message="Field email is missing."), 400

    result = parseaddr(email);

    if (len(result[1]) == 0 or not (provjeri_Email(email))):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first();

    if (not user):
        return jsonify(message="Unknown user."), 400

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "role": refreshClaims["role"]
    };
    if(refreshClaims["role"]=="administrator"):
        User.query.filter(User.email == email).delete();
        database.session.commit();
        return "",200;

    return "Nemate pravo da brisete korisnike.",400;

@application.route ( "/refresh", methods = ["POST"] )
@jwt_required ( refresh = True )
def refresh ( ):
    identity = get_jwt_identity ( );
    refreshClaims = get_jwt ( );

    additionalClaims = {

        "jmbg": refreshClaims["jmbg"],
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "email": refreshClaims["email"],
        "password": refreshClaims["password"],
        "role":refreshClaims["role"]

    };

    return jsonify(accessToken= create_access_token ( identity = identity, additional_claims = additionalClaims )), 200

if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True,host="0.0.0.0", port = 5002 );