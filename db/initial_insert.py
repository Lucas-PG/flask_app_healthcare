from flask import Flask
from db.connection import db
from sqlalchemy import event
from models.users import User
from models.kits import Kit
from models.devices import Device
from models.actuators import Actuator
from models.sensors import Sensor

session = db.session

def _populate_users(app:Flask):
    with app.app_context():
        users = [
            User('lucas', 'pucas', 'admin'),
            User('tiago', 'gaspe' , 'operador'),
            User('Yuji Itadori', 'jujutsu_sorcerer', 'estatistico'),
            User('Megumi Fushiguro', 'divine_dogs', 'estatistico'),
            User('Toji Fushiguro', 'homeless', 'operador'),
            User('Satoru Gojo', 'limitless', 'admin'),
            User('Sukuna', 'king_of_curses', 'operador'),
            User('Monkey D. Luffy', 'gomu_gomu', 'estatistico'),
            User('Roronoa Zoro', 'three_swords', 'operador'),
            User('Nami', 'navigation_expert', 'operador'),
            User('Usopp', 'sogeking', 'estatistico'),
            User('Sanji', 'black_leg', 'operador'),
            User('Tony Tony Chopper', 'doctorine', 'estatistico')
        ]
        
        session.add_all(users)
        session.commit()

def _populate_kits(app: Flask):
    with app.app_context():
        kits = [
            Kit('kit_1', 1),
            Kit('kit_2', 2),
            Kit('kit_3', 3),
        ]
        
        session.add_all(kits)
        session.commit()
        
def _populate_devices(app: Flask):
    with app.app_context():
        devices = [
            Device('DHT22', 22, 1),
            Device('Sensor de Proximidade', 10, 2),
            Device('Botão', 1, 3),
            Device('Servo', 0, 3)
        ]
        
        session.add_all(devices)
        session.commit()
        
def _populate_actuators(app: Flask):
    with app.app_context():
        actuators = [
            Actuator('lucas/enviar', 1),
            Actuator('lucas/enviar', 2),
            Actuator('lucas/enviar', 3),
            Actuator('lucas/enviar', 1),
        ]
    
        session.add_all(actuators)
        session.commit()
    
def _populate_sensors(app: Flask):
    with app.app_context():
        sensors = [
            Sensor('lucas/enviar', 1),
            Sensor('lucas/enviar', 2),
            Sensor('lucas/enviar', 3),
            Sensor('lucas/enviar', 3),
        ]
        
        session.add_all(sensors)
        session.commit()

def initial_populate_db(app: Flask):
    _populate_users(app)
    _populate_kits(app)
    _populate_devices(app)
    _populate_actuators(app)
    _populate_sensors(app)