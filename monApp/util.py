from random import randint


def hash(str):
    return(str)


def gen_passwd(size):
    chars = "azertyuiopqsdfghjklmwxcvbn1234567890"
    passwd = ""
    for k in range(size):
        passwd += chars[randint(0, len(chars)-1)]
    return passwd


def endHour(dateTime):
    return dateTime.replace(hour=dateTime.hour + 1, minute=0, second=0, microsecond=0)


def report(str):
    print(str)