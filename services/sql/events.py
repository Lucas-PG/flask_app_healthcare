from flask import Flask;
from sqlalchemy import DDL
from services.db import db
from models.devices import Device

session = db.session

def create_historic_trigger(app: Flask):
    trigger = DDL(
        "DELIMITER $$"
        "CREATE TRIGGER populate_historic"
        "AFTER INSERT ON devices"
        "FOR EACH ROW"
        "BEGIN"
        "INSERT INTO historic(value, datetime, device_id) VALUES(NULL, NOW(), NEW.id);"
        "END$$"
        "DELIMITER ;"
    )
    
    session.execute(trigger)