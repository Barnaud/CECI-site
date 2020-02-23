from random import randint
import pandas as pd
import os
import math
import numpy as np
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from monApp import models, util
from datetime import timedelta
import hashlib
from django.template.loader import get_template

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

def isNan(value):
    if isinstance(value, float):
        return math.isnan(value)
    return False


def widafExtract(file, exam_type):
    df = pd.read_excel(file)
    list = []
    errorList = []
    for k in range(len(df["Vocabulaire"])):
        if not isNan(df["Vocabulaire"][k]) and\
                not isNan(df["Nom"][k]) and \
                not isNan(df["Prénom"][k]) and \
                not isNan(df["Compréhensionécrite"][k]) and \
                not isNan(df["Compréhensionorale"][k]) and\
                not isNan(df["Total"][k]) :
            dict = {}
            NameLst = [df["Prénom"][k].split(" ")[0], df["Nom"][k].split("-")[0].replace(" ", "")]
            mail = "%s.%s@ecam-strasbourg.eu" % (NameLst[0], NameLst[1])
            dict["mail"] = mail
            template_params = {
                "nom": df["Nom"][k],
                "score": df["Total"][k],
                "voc": df["Vocabulaire"][k],
                "ce": df["Compréhensionécrite"][k],
                "co": df["Compréhensionorale"][k],
                "blanc": True if exam_type != "widaf" else False,
                "exam_type": exam_type
            }
            template = get_template("monApp/mail_templates/widaf_result.txt")
            dict["content"] = template.render(template_params)
            list.append(dict)
        else:
            errorList.append(k+2)
        if errorList:
            errorStr="Il manque des informations aux lignes suivantes: "
            for elt in errorList:
                errorStr += str(elt)+", "
            errorStr = errorStr[:-2]
            raise Exception(errorStr)
    return list

def toeicExtract(file, examType):
    df = pd.read_excel(file, skiprows=12, usecols=4)
    list = []
    errorLst = []
    errorStr = "Il manque des éléments à la ligne suivante: "
    for k in range(len(df["R"])):
        dict = {}
        if not isNan(df["TOTAL"][k]) and \
            not isNan(df["R"][k]) and \
            not isNan(df["L"][k]) and \
            not isNan(df["Candidate name"][k]):

            NameLst = df["Candidate name"][k].split(",")[0].split(" ")
            if len(NameLst) != 2:
                raise Exception("Veuillez verifier le nom à la ligne: " + str(k))
            template_param = {"nom": NameLst[-2],
                              "score": int(df['TOTAL'][k]),
                              "reading": int(df["R"][k]),
                              "listening": int(df["L"][k]),
                              "grade": util.getToeicGrade(int(df['TOTAL'][k])),
                              "success": True if int(df['TOTAL'][k])>=800 else False}
            mail = "%s.%s@ecam-strasbourg.eu" % (NameLst[-1], NameLst[-2])
            dict["mail"] = mail
            if examType == "toeic_s5":
                template_param["s"] = 5
                template_param["blanc"] = "blanc"
            elif examType == "toeic_s6":
                template_param["s"] = 6
                template_param["blanc"] = "blanc"
            else:
                template_param["s"] = 7
                template_param["blanc"] = ""

            template = get_template("monApp/mail_templates/toeic_result.txt")
            dict["content"] = template.render(template_param)
            list.append(dict)
        else:
            errorLst.append(k+14)

        if  errorLst:
            for elt in errorLst:
                errorStr += str(elt)+", "
            errorStr = errorStr[:-2]

            raise Exception(errorStr)
    return list

def getToeicGrade(mark):
    if mark < 120:
        return "Less than A1"
    elif mark < 225:
        return "A1"
    elif mark < 550:
        return "A2"
    elif mark < 800:
        return "B1"
    elif mark < 945:
        return "B2"
    else:
        return "C1"
