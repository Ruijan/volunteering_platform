import os
import pandas as pd
from flask import Flask, session, render_template, redirect, url_for
from flask_pymongo import PyMongo, request
from cryptography.fernet import Fernet
from datetime import datetime
from flask_simple_geoip import SimpleGeoIP

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
        return ""
    else:
        return redirect(url_for("login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global mongo
    if is_user_connected():
        return redirect(url_for("homepage"))
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        data = request.form
        f = Fernet(bytes(app.secret_key, 'utf-8'))
        users = list(mongo.db.users.find())
        user = None
        for tmp_user in users:
            if isinstance(tmp_user["email"], bytes):
                email = f.decrypt(tmp_user["email"]).decode("utf-8")
                if email == data["email"]:
                    user = tmp_user
        if user is not None:
            db_pass = f.decrypt(user["pass"]).decode("utf-8")
            if db_pass == data["pass"]:
                session["USER"] = user["email"]
                session.new = True
                return redirect(url_for("homepage"))
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
    return redirect(url_for("login"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    global mongo
    session.clear()
    if is_user_connected():
        return redirect(url_for("homepage"))
    if request.method == 'GET':
        skills = ["Housework", "House cleaning", "Grocery shopping", "Dog walking", "Call check", "Medication",
                  "Cooking", "Administrative"]
        return render_template("register.html", skills=skills)
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        # f = Fernet(bytes(app.secret_key, 'utf-8'))
        # data["pass"] = f.encrypt(data["pass"].encode())
        # data["first_name"] = f.encrypt(data["first_name"].encode())
        # data["last_name"] = f.encrypt(data["last_name"].encode())
        # data["email"] = f.encrypt(data["email"].encode())
        # data["phone"] = f.encrypt(data["phone"].encode())
        data["creation_date"] = datetime.now()
        data["geolocation"] = simple_geoip.get_geoip_data()
        data.pop("pass2")
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
            session.new = True
            return redirect(url_for("homepage"))
        else:
            return render_template("register.html", error_login="Email already in database. Try signing in")


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run()
