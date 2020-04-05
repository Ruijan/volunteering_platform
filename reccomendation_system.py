from geopy.distance import geodesic
import pymongo
import os
import random
from geopy.geocoders import Nominatim


def generate_location(geolocator):
    flag = False
    while not flag:
        address = geolocator.reverse(str(46.41006 + random.random()) + ", " + str(7.51362 + random.random()))[0]
        address_splitted = address.split(',')
        generated_country = address_splitted[-1:][0].strip()
        generated_zip = address_splitted[-2:-1][0].strip()
        if (generated_country == 'Switzerland') & generated_zip.isdigit():
            address_other_info = ', '.join(address_splitted[:-3])
            generated_city = address_splitted[-3].strip()
            generated_zip = int(generated_zip)
            flag = True
    return generated_country, generated_zip, generated_city, address_other_info


def compute_distance(coordinates1, coordinates2):
    return geodesic((coordinates1[0], coordinates1[1]), (coordinates2[0], coordinates2[1])).kilometers


# Find match for the volunteer
def recommend_task(volunteer, tasks):
    available_tasks = []
    for task in tasks:
        if task['task'] in volunteer['skills'] and task['city'] == volunteer['city'] and task['status'] == 0 and \
                "coordinates" in task and "coordinates" in volunteer:
            task["distance"] = compute_distance(task['coordinates'], volunteer['coordinates'])
            available_tasks.append(task)
    return sorted(available_tasks, key=lambda i: i["distance"])


# Find match for the grandpa/ma
def recommend_volunteer(task, volunteers):
    available_volunteers = []
    for volunteer in volunteers:
        status_active = (task['status'] == 2 and volunteer['status'] == 1) or volunteer['status'] == 2
        if task['task'] in volunteer['skills'] and task['city'] == volunteer['city'] and status_active:
            volunteer["distance"] = compute_distance(task['coordinates'], volunteer['coordinates'])
            available_volunteers.append(volunteer)
    return sorted(available_volunteers, key=lambda i: i["distance"])

