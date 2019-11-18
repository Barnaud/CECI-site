from Django import wsgi
from monApp import models
from monApp.util import endHour
import datetime

mails_to_send = models.PlannedMail.objects.filter(time__lte=endHour(datetime.datetime.now()))
print(mails_to_send)

for mail in mails_to_send:
	mail.send()


