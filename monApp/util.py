from random import randint
import pandas as pd
import os
import math
import numpy as np
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from monApp import models
from datetime import timedelta
import hashlib

def isNan(value):
    if isinstance(value, float):
        if math.isnan(value):
            return True
    return False


def excel_read(file):

    df=pd.read_excel(file)
    list = []

    for k in range(len(df["Nom"])):
        dict = {}
        if isNan(df["Nom"][k]) or isNan(df["Prénom"][k]):
            dict["identifiant"] = df["Identifiant"][k]
        else:
            dict["identifiant"] = "%s.%s" % (df["Prénom"][k], df["Nom"][k])
            additional_id=2
            while models.ForumUser.objects.filter(identifiant=dict["identifiant"]).count():
                dict["identifiant"] = "%s.%s%s" % (df["Prénom"][k], df["Nom"][k], additional_id)
                additional_id +=1

        dict["mail"] = df["Addresse e-mail"][k]
        dict["groupe"] = df["Groupe"][k]
        list.append(dict)

    return list

def check_excel_dict(dict):
    for user in dict:
        for elt in user:
            if not type(elt) is str:
                raise Exception("Wrong data type")
        if len(user["identifiant"])<3:
            raise Exception("Username %s too short" % (user["identifiant"]))
        validate_email(user["mail"])
        models.ForumGroup.objects.get(nom=user['groupe'])
        if models.ForumUser.objects.filter(identifiant=user["identifiant"]).count():
            raise Exception("Username %s already taken" % (user["identifiant"]))


def hash(str):
    m = hashlib.sha256()
    m.update(str.encode())
    return(m.digest())


def gen_passwd(size):
    chars = "azertyuiopqsdfghjklmwxcvbn1234567890"
    passwd = ""
    for k in range(size):
        passwd += chars[randint(0, len(chars)-1)]
    return passwd


def endHour(dateTime):
    dateTime = dateTime+timedelta(hours=1)
    return dateTime.replace(minute=0, second=0, microsecond=0)


def report(str):
    print(str)
