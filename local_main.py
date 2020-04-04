import pymongo
import os
import random
import string
import names
import numpy as np
from cryptography.fernet import Fernet
from datetime import datetime


def makeEmail():
    extensions = ['com', 'net', 'org', 'gov']
    domains = ['gmail', 'yahoo', 'comcast', 'verizon', 'charter', 'hotmail', 'outlook', 'frontier']
    winext = extensions[random.randint(0, len(extensions) - 1)]
    windom = domains[random.randint(0, len(domains) - 1)]
    acclen = random.randint(1, 20)
    winacc = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(acclen))
    finale = winacc + "@" + windom + "." + winext
    return finale


def phn():
    n = '0000000000'
    while '9' in n[3:6] or n[3:6] == '000' or n[6] == n[7] == n[8] == n[9]:
        n = str(random.randint(10 ** 9, 10 ** 10 - 1))
    return '07.' + n[2:4] + '.' + n[4:6] + '.' + n[6:8] + '.' + n[8:10]


if __name__ == '__main__':
    client = pymongo.MongoClient(os.environ["MONGO_URI_VOLUNTEER"])
    db = client.volunteering
    users = list(db.users.find())
    # x = client.volunteering.users.delete_many({})
    skills = ["House cleaning", "Grocery shopping", "Dog walking", "Call check", "Medication", "Cooking", "Housework"]
    nb_users = 50
    if len(users) < nb_users:
        nb_users = nb_users - len(users)
        f = Fernet(bytes(os.environ["MONGO_KEY_VOLUNTEER"], 'utf-8'))
        member_types = ["Volunteer", "Need"]
        for index in range(nb_users):
            nb_skills = random.randint(1, len(skills))
            selected_skills = list(np.unique([random.choice(skills) for i in range(nb_skills)]))
            user = {"email": makeEmail(), "first_name": names.get_first_name(), "last_name": names.get_last_name(),
                    "localization": random.randint(1000, 9999), "phone": phn(), "password": "pwd",
                    "skills": selected_skills, "age": random.randint(18, 60),
                    "member_type": member_types[random.randint(0, 1)], "last_connection": datetime.now()}
            client.volunteering.users.insert_one(user)
