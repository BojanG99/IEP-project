from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy();


class IzborUcesnik(database.Model):
    __tablename__ = "izborucesnik";

    id = database.Column(database.Integer, primary_key=True);
    poolNum=database.Column(database.Integer);
    izborId = database.Column(database.Integer, database.ForeignKey("izbori.id"), nullable=False);
    ucesnikId = database.Column(database.Integer, database.ForeignKey("ucesnici.id"), nullable=False);


class Izbor(database.Model):
    __tablename__ = "izbori";
    id = database.Column(database.Integer, primary_key=True, autoincrement=True);
    start = database.Column(database.DATETIME, nullable=False, );
    end = database.Column(database.DATETIME, nullable=False, );
    individual = database.Column(database.Boolean, nullable=False);
    glasovi=database.relationship("Glas",back_populates="izbor");
    ucesnici = database.relationship("UcesnikIzbora", secondary=IzborUcesnik.__table__, back_populates="izbori");

class Glas(database.Model):
    __tablename__ = "glasovi";

    id = database.Column(database.Integer, primary_key=True);
    guid=database.Column(database.String(256),nullable=False);
    validan=database.Column(database.Boolean,nullable=False);
    duplikat=database.Column(database.Boolean)
    jmbg = database.Column(database.String(256), nullable=False);
    izborId=database.Column(database.Integer,database.ForeignKey("izbori.id"),nullable=False);
    poolNum=database.Column(database.Integer,nullable=False);
    izbor=database.relationship("Izbor",back_populates="glasovi");
    #ucesnikId=database.Column(database.Integer,database.ForeignKey("ucesnici.id"),nullable=False);
    #ucesnik = database.relationship("UcesnikIzbora", back_populates="glasovi");
    def __repr__(self):
        return self.name;


class UcesnikIzbora(database.Model):
    __tablename__ ="ucesnici"
    id = database.Column(database.Integer, primary_key=True);
    ime=database.Column(database.String(256),nullable=False, );
    individual=database.Column(database.Boolean,nullable=False);
    izbori=database.relationship("Izbor",secondary= IzborUcesnik.__table__,back_populates="ucesnici");

    def __repr__(self):
        return self.ime;
