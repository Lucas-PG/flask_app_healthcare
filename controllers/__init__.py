# app_controller.py
import json

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, login_required, logout_user
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

from db.connection import db, instance
from models import Actuator, Device, Kit, Sensor, User

topic_recive = "cz/enviar"
topic_send = "cz/receba"
temperature = 0
max_capacity = 100
people = 0


def create_app():
    app = Flask(
        __name__,
        template_folder="./templates/",
        static_folder="./static/",
        root_path="./",
    )
    app.secret_key = "lucaspucas"

    app.config["MQTT_BROKER_URL"] = "mqtt-dashboard.com"
    app.config["MQTT_BROKER_PORT"] = 1883
    app.config["MQTT_USERNAME"] = ""
    app.config["MQTT_PASSWORD"] = ""
    app.config["MQTT_KEEPALIVE"] = 5000
    app.config["MQTT_TLS_ENABLED"] = False

    mqtt_client = Mqtt()
    mqtt_client.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login.login_func"

    @app.route("/")
    def index():
        return render_template("landing.html", user=session.get("user"))

    @mqtt_client.on_message()
    def handle_mqtt_message(client, userdata, message):
        js = json.loads(message.payload.decode())
        global people, temperature
        with app.app_context():
            dht = Sensor.select_device_by_sensor_id(1)
            Sensor.update_sensor_value(dht.id, js["temperature"])
            temperature = dht.value
            print(dht.value)

        if js["exitPeople"] == 0:
            with app.app_context():
                actuator = Actuator.select_actuators_by_id(2)
                Actuator.update_actuator_button_value(actuator.device_id, 1)
        elif js["enterPeople"] == 0:
            with app.app_context():
                actuator = Actuator.select_actuators_by_id(1)
                Actuator.update_actuator_button_value(actuator.device_id, 1)
        with app.app_context():
            people = (
                Actuator.select_device_by_actuator_id(1).value
                - Actuator.select_device_by_actuator_id(2).value
            )

    @app.route("/publish_message", methods=["GET", "POST"])
    def publish_message():
        request_data = request.get_json()
        publish_result = mqtt_client.publish(
            request_data["topic"], request_data["message"]
        )
        return jsonify(publish_result)

    @app.route("/real_time", methods=["GET", "POST"])
    def real_time():
        global temperature, people
        people = people if people <= max_capacity else max_capacity
        people = people if people >= 0 else 0
        values = {"Temperatura": temperature, "Pessoas": people}
        print(temperature)
        return render_template(
            "real_time.html",
            values=values,
            max_capacity=max_capacity,
            people=people,
            temperature=temperature,
        )

    @app.route("/kits")
    @login_required
    def kits():

        kits = Kit.select_all_from_kits()
        return render_template("kits/kits.html", kits=kits)

    @app.route("/edit_kit")
    @login_required
    def edit_kit():
        kit_id = request.args.get("kit_id", None)
        kit = Kit.select_kit_by_id(kit_id)
        attributes = dir(kit)
        user_name = User.select_user_by_id(kit.user_id).name
        error_message = request.args.get("error_message", None)
        if kit == None:
            return redirect("/kits")
        else:
            return render_template(
                "kits/edit_kits.html",
                kit=kit,
                user_name=user_name,
                error_message=error_message,
            )

    @app.route("/edit_given_kit")
    @login_required
    def edit_given_kit():
        kit_id = request.args.get("kit_id", None)
        kit_name = request.args.get("kit_name", None)
        user_name = request.args.get("user_name", None)
        existing_kit = Kit.select_kit_by_name(kit_name)
        kit = Kit.select_kit_by_id(kit_id).name
        existing_user = User.select_user_by_name(user_name)
        if existing_kit and kit_name != kit:
            return redirect(
                url_for(
                    ".edit_kit",
                    error_message="Esse nome de kit já existe!",
                    kit_id=kit_id,
                )
            )
        elif not existing_user:
            return redirect(
                url_for(
                    ".edit_kit",
                    error_message="Esse nome de usuário não existe!",
                    kit_id=kit_id,
                )
            )
        else:
            user_id = User.select_user_by_name(user_name).id
            Kit.update_given_kit(kit_id, kit_name, user_id)
            return redirect("/kits")

    @app.route("/delete_kit")
    @login_required
    def remove_kit():
        kit_id = request.args.get("kit_id", None)
        Kit.delete_kit_by_id(kit_id)
        return redirect("/kits")

    @mqtt_client.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Broker Connected successfully")
            mqtt_client.subscribe(topic_recive)
            mqtt_client.subscribe(topic_send)
            print("Broker Connected successfully")
        else:
            print("Bad connection. Code:", rc)

    @mqtt_client.on_disconnect()
    def handle_disconnect(client, userdata, rc):
        print("Disconnected from broker")

    @app.errorhandler(404)
    def page_not_found(error):
        logged = False
        if session.get("user"):
            logged = True
        return (
            render_template(
                "errors/error.html",
                error_message="Parece que a página não existe! Tente novamente!",
                logged=logged,
            ),
            404,
        )

    @app.errorhandler(405)
    def page_not_found(error):
        return (
            render_template("errors/error.html", error_message="Você não fez login!"),
            405,
        )

    @login_manager.request_loader
    def load_user_from_request(request):

        # first, try to login using the api_key url arg
        api_key = request.args.get("api_key")
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # next, try to login using Basic Auth
        api_key = request.headers.get("Authorization")
        if api_key:
            api_key = api_key.replace("Basic ", "", 1)
            try:
                api_key = base64.b64decode(api_key)
            except TypeError:
                pass
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # finally, return None if both methods did not login the user
        return None

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
