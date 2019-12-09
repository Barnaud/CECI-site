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
        if isNan(df["Identifiant"][k]):
            dict["identifiant"] = "%s.%s" % (df["Prénom"][k], df["Nom"][k])
            additional_id = 2
            while models.ForumUser.objects.filter(identifiant=dict["identifiant"]).count():
                dict["identifiant"] = "%s.%s%s" % (df["Prénom"][k], df["Nom"][k], additional_id)
                additional_id += 1
        else:
            dict["identifiant"] = df["Identifiant"][k]


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
        print(user)
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


def widafExtract(file):
    df = pd.read_excel(file)
    list = []
    for k in range(len(df["Vocabulaire"])):
        if not math.isnan(df["Vocabulaire"][k]):
            dict = {}
            NameLst = [df["Prénom"][k], df["Nom"][k]]
            name = "%s %s" % (NameLst[0].lower(), NameLst[1].lower())
            mail = "%s.%s@ecam-strasbourg.eu" % (NameLst[0], NameLst[1])
            dict["mail"] = mail
            dict["content"] = 'Bonjour, %s, Nous avons reçu les résultats du Widaf.\n' % (NameLst[0])
            if int(df['Total'][k]) > 125:
                dict[
                    "content"] += "Félicitations, vous avez obtenu un score de %s points. Votre Widaf est donc validé.\n" % (
                df["Total"][k])
            else:
                dict[
                    "content"] += "Malheureusement, vous avez obtenu le score de %s points, qui n'est pas suffisant pour valider votre Widaf.\n" % (
                df["Total"][k])
            dict[
                "content"] += "Vous avez obtenu %s points à la partie vocabulaire, %s points à la partie compréhension écrite, %s points à la partie compréhension orale.\nCordialement,\nBernard Jenaste" % (
            int(df['Vocabulaire'][k]), int(df["Compréhensionécrite"][k]), int(df['Compréhensionorale'][k]))
            list.append(dict)
    return list

def toeicExtract(file):
    df = pd.read_excel(file, skiprows=12, usecols=4)
    list = []
    for k in range(len(df["R"])):
        dict = {}
        NameLst = df["Candidate name"][k].split(" ")
        name = "%s %s" % (NameLst[-1], NameLst[-2])
        mail = "%s.%s@ecam-strasbourg.eu" % (NameLst[-1], NameLst[-2])
        dict["mail"] = mail
        dict["content"] = 'Bonjour, %s, Nous avons reçu les résultats du Toeic.\n' % (NameLst[-1])
        if int(df['TOTAL'][k]) > 800:
            dict[
                "content"] += "Félicitations, vous avez obtenu un score de %s points. Votre Toeic est donc validé.\n" % (
            int(df["TOTAL"][k]))
        else:
            dict[
                "content"] += "Malheureusement, vous avez obtenu le score de %s points, qui n'est pas suffisant pour valider votre Toeic.\n" % (
            int(df["TOTAL"][k]))
        dict[
            "content"] += "Vous avez obtenu %s points à la partie Listening et %s points à la partie Reading.\nCordialement,\nBernard Jenaste" % (
        int(df['L'][k]), int(df["R"][k]))
        list.append(dict)
    return list

