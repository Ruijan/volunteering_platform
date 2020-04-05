from geopy.distance import geodesic
import pymongo
import os
import random
import string
import names
import numpy as np
from cryptography.fernet import Fernet
from datetime import datetime
import time
import random
from geopy.geocoders import Nominatim

def generate_location(geolocator):
    flag=False
    while not flag:
        address = geolocator.reverse(str(46.41006 + random.random()) + ", " + str(7.51362 + random.random()))[0]
        address_splitted = address.split(',')
        generated_country = address_splitted[-1:][0].strip()
        generated_zip = address_splitted[-2:-1][0].strip()
        if (generated_country == 'Switzerland') & generated_zip.isdigit():
            address_other_info = ', '.join(address_splitted[:-3])
            generated_city = address_splitted[-3].strip()
            generated_zip = int(generated_zip)
            flag=True
    return generated_country, generated_zip, generated_city, address_other_info

def compute_distance(zip_code_1, city_1, zip_code_2, city_2, geolocator):
    location = geolocator.geocode(str(zip_code_1) + ' ' + city_1)
    location2 = geolocator.geocode(str(zip_code_2) + ' ' + city_2)
    return geodesic((location.latitude, location.longitude), (location2.latitude, location2.longitude)).kilometers


# Find match for the volunteer
def recommend_task(volunteer, tasks):
    available_tasks = []
    for task in tasks:
        if task['task'] in volunteer['skills'] and task['city'] == volunteer['city'] and task['status'] == 0:
            task["distance"] = compute_distance(task['zip_code'], task['city'], volunteer['zip_code'], volunteer['city'], geolocator)
            available_tasks.append(task)
    return sorted(available_tasks, key = lambda i: i["distance"])


# Find match for the grandpa/ma
def recommend_volunteer(task, volunteers):
    available_volunteers=[]
    for volunteer in volunteers:
        status_active = (task['status'] == 2 and volunteer['status'] == 1) or volunteer['status'] == 2
        if task['task'] in volunteer['skills'] and task['city'] == volunteer['city'] and status_active:
            volunteer["distance"] = compute_distance(task['zip_code'], task['city'], volunteer['zip_code'], volunteer['city'], geolocator)
            available_volunteers.append(volunteer)
    return sorted(available_volunteers, key = lambda i: i["distance"])

#test
client = pymongo.MongoClient(os.environ["MONGO_URI_VOLUNTEER"])
db = client.volunteering
tasks = list(db.tasks.find())
users = list(db.users.find())
geolocator = Nominatim(timeout=3)
volunteers=[user for user in users if user["member_type"] == "Volunteer"]
volunteer = volunteers[0]
tasks_sorted_by_distance = =recommend_task(volunteer, tasks)
task = tasks[0]
volunteers_sorted_by_distance =recommend_volunteer(task, volunteers)
