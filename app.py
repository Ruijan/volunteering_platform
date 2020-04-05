import json
import os
import pandas as pd
from bson import ObjectId
from flask import Flask, session, render_template, redirect, url_for
from flask_pymongo import PyMongo, request
from cryptography.fernet import Fernet
from datetime import datetime
from flask_simple_geoip import SimpleGeoIP
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random

from reccomendation_system import recommend_task

app = Flask("Company Explorer")
app.secret_key = os.environ["MONGO_KEY_VOLUNTEER"]
global pymongo_connected
global mongo

pymongo_connected = False
if 'MONGO_URI_VOLUNTEER' in os.environ and not pymongo_connected:
    app.config['MONGO_DBNAME'] = 'volunteering'
    app.config['MONGO_URI'] = os.environ['MONGO_URI_VOLUNTEER'].strip("'").replace('test', app.config['MONGO_DBNAME'])
    app.config["GEOIPIFY_API_KEY"] = os.environ['WHOIS_KEY']
    mongo = PyMongo(app)
    pymongo_connected = True
    simple_geoip = SimpleGeoIP(app)


def is_user_connected():
    if session.get("USER") and mongo.db.users.find_one({"email": session["USER"]}) is not None:
        return True
    elif session.get("USER"):
        session.clear()
    return False


@app.route('/')
def homepage():
    if is_user_connected():
        return render_template("index.html", first_name=session["FIRST_NAME"])
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    global mongo
    if is_user_connected():
        return redirect(url_for("dashboard"))
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        data = request.form
        # f = Fernet(bytes(app.secret_key, 'utf-8'))
        users = list(mongo.db.users.find())
        user = None
        for tmp_user in users:
            if tmp_user["email"] == data["email"]:
                user = tmp_user
        if user is not None:
            # db_pass = f.decrypt(user["pass"]).decode("utf-8")
            db_pass = user["password"]
            if db_pass == data["pass"]:
                session["USER"] = user["email"]
                session["FIRST_NAME"] = user["first_name"]
                session["LOCALIZATION"] = " ".join([user["address"], str(user["zip_code"]), user["city"]])
                session["ZIP_CODE"] = user["zip_code"]
                session["CITY"] = user["city"]
                session.new = True
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error_login="Wrong password")
        else:
            return render_template("login.html", error_login="No user found with username")


@app.route('/logout')
def logout():
    if is_user_connected():
        data = mongo.db.users.find_one({"email": session["USER"]})
        if data is not None:
            data["connected"] = False
            data["last_connection"] = datetime.now()
        session.clear()
    return redirect(url_for("homepage"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    global mongo
    if is_user_connected():
        return redirect(url_for("dashboard"))
    if request.method == 'GET':
        skills = ["Housework", "House cleaning", "Grocery shopping", "Dog walking", "Call check", "Medication",
                  "Cooking", "Administrative"]
        return render_template("register.html", skills=skills)
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        geolocator = Nominatim(timeout=3)
        # f = Fernet(bytes(app.secret_key, 'utf-8'))
        # data["pass"] = f.encrypt(data["pass"].encode())
        # data["first_name"] = f.encrypt(data["first_name"].encode())
        # data["last_name"] = f.encrypt(data["last_name"].encode())
        # data["email"] = f.encrypt(data["email"].encode())
        # data["phone"] = f.encrypt(data["phone"].encode())
        data["creation_date"] = datetime.now()
        data["password"] = data["pass"]
        location = geolocator.geocode(" ".join([data["address"], str(data["zip_code"]), data["city"]]))
        data["coordinates"] = (location.latitude, location.longitude)
        data["status"] = 0
        data["geolocation"] = simple_geoip.get_geoip_data()
        data.pop("pass2")
        data.pop("pass")
        user = None
        try:
            user = mongo.db.users.find_one({"email": data["email"]})
        except:
            pass
        if user is None:
            data["connected"] = True
            data["last_connection"] = datetime.now()
            mongo.db.users.insert_one(data)
            session["USER"] = data["email"]
            session["FIRST_NAME"] = data["first_name"]
            session["LOCALIZATION"] = " ".join([data["address"], str(data["zip_code"]), data["city"]])
            session["ZIP_CODE"] = data["zip_code"]
            session["CITY"] = data["city"]
            session.new = True
            return redirect(url_for("homepage"))
        else:
            return render_template("register.html", error_signup="Email already in database. Try signing in")


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global mongo
    if is_user_connected():
        current_user = mongo.db.users.find_one({"email": session["USER"]})
        if current_user["member_type"] == "Volunteer":
            tasks = list(mongo.db.tasks.find({"city": session["CITY"]}))
            tasks_sorted_by_distance = recommend_task(current_user, tasks)
            if request.method == 'POST':
                data = request.form.to_dict(flat=True)
                id = ObjectId(data["_id"])
                task = mongo.db.tasks.find_one({"_id": id})
                task["volunteer_id"] = session["USER"]
                task["status"] = 1
                mongo.db.tasks.find_one_and_replace({"_id": id}, task)
                if "accepted_tasks" not in current_user:
                    current_user["accepted_tasks"] = []
                current_user["accepted_tasks"].append(task)
                mongo.db.users.find_one_and_replace({"email": session["USER"]}, current_user)
            for task in tasks_sorted_by_distance:
                task["distance"] = "{:0.2f}".format(task["distance"]) + "km"

            accepted_tasks = []
            if "accepted_tasks" in current_user and len(current_user["accepted_tasks"]) > 0:
                accepted_tasks = current_user["accepted_tasks"]
            for task in accepted_tasks:
                task["status"] = "On Going" if task["status"] == 1 else "Complete"
            feature_tasks = [
                {"type": "Feature",
                 "geometry": {"type": "Point", "coordinates": (task["coordinates"][1], task["coordinates"][0])},
                 "properties": {"description": "<div style='text-align: center; width: 100%;'><img src=" +
                                               ("'static/images/grandpa.png'" if task[
                                                                                     "gender"] == "Male" else "'static/images/grandma.png'") + "width='50%'></div>" +
                                               "<div style='text-align: center; width: 100%; margin-bottom: 15px;'>" +
                                               task["user_first_name"] +
                                               "</div><strong>Task: " + task["task"] +
                                               "</strong><br/><strong>Urgency:</strong> " + str(
                     task["emergency_level"]) +
                                               "<br><strong>Duration:</strong> " + str(
                     task["task_duration-in-minutes"]) +
                                               "min<br><strong>Start:</strong> " + task["date_time_start"] +
                                               "<form class='login100-form validate-form' target='_self' "
                                               "method='post' style='width: 100%; text-align: center;'>"
                                               "<input value='" + str(task['_id']) + "' name='_id' hidden>"
                                                                                     "<button class='be_a_hero_button' style='width:100%;' type='submit'>Be a hero!</button></form>"}}
                for task in tasks_sorted_by_distance]
            return render_template("dashboard.html", tasks=tasks_sorted_by_distance, first_name=session["FIRST_NAME"],
                                   accepted_tasks=accepted_tasks, feature_tasks=feature_tasks)
        elif current_user["member_type"] == "Need":

            accepted_tasks = list(mongo.db.tasks.find({"user_id": current_user["_id"]}))
            for task in accepted_tasks:
                task["status"] = "On Going" if task["status"] == 1 else "Complete"
            return render_template("dashboard-need.html", first_name=session["FIRST_NAME"],
                                   accepted_tasks=accepted_tasks, gender=current_user["gender"])
    else:
        return redirect(url_for("login"))


@app.route('/map', methods=['GET'])
def map():
    global mongo
    tasks = list(mongo.db.tasks.find())

    return render_template("map.html")


@app.route('/choose_volunteer', methods=['GET'])
def choose_volunteer():
    global mongo
    users = list(mongo.db.users.find({"member_type": "Volunteer"}).limit(10))
    return render_template("choose_volunteer.html", users=users)


@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    global mongo
    if request.method == 'POST':
        current_user = mongo.db.users.find_one({"email": session["USER"]})
        data = request.form.to_dict(flat=True)
        task = {"task": data["selected_skill"],  "date_time_start": data["helpday"], "task_duration-in-minutes":  data["duration"],
            "user_id": current_user["_id"],  "address": current_user["address"], "emergency_level": data["selected_emergency"],
            "zip_code": current_user["zip_code"], "city": current_user["city"],
            "phone": current_user["phone"], "user_first_name": current_user["first_name"],
            "gender": current_user["gender"],
            'status': 0, "volunteer_id": -1}
        mongo.db.tasks.insert_one(task)
        return redirect(url_for("choose_volunteer"))
    elif request.method == 'GET':
        skills = ["Housework", "House cleaning", "Grocery shopping", "Dog walking", "Call check", "Medication",
                  "Cooking", "Administrative"]
        return render_template("add_task.html", skills=skills)


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
