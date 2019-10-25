from django import forms
from monApp import models, util
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import json
from datetime import datetime, timedelta
from pdf2image import convert_from_bytes
from os import path, mkdir
from Django import settings
import shutil


class LoginForm(forms.Form):
    id = forms.CharField(max_length=50)
    mdp = forms.CharField(max_length=50)


class GroupForm(forms.ModelForm):
    class Meta:
        model = models.ForumGroup
        fields = ("nom", "couleur")

    fichier = forms.ImageField(required=False)

    def save(self, commit=True):
        m = super().save(commit=False)

        if self.cleaned_data["fichier"]:
            new_logo = models.logo.objects.create(nom="logo_%s"%(self.cleaned_data["nom"]))
            new_logo.img = self.cleaned_data["fichier"]
            new_logo.save()
            m.logo = new_logo
        m.save()

class UserForm(forms.ModelForm):
    class Meta:
        model = models.ForumUser
        fields = ("identifiant", "mail", "groupe")
        widgets= {
            'groupe': forms.CheckboxSelectMultiple(),
            'mail': forms.TextInput()
        }

    def save(self, commit=True):
        m = super().save(commit=True)
        if not m.password:
            m.password = util.gen_passwd(10)
            template = get_template("monApp/mail_templates/addUser.txt")
            mail_content = template.render({"username": m.identifiant,
                                            "password": m.password})
            msg=EmailMultiAlternatives("Bienvenue", mail_content, "noreply@docs-ceci-formation.fr", [m.mail])
            msg.send()
            m.password = util.hash(m.password)
        m.save()


class SectionForm(forms.ModelForm):
    class Meta:
        model = models.LangueSection
        fields = ("nom_complet", "nom_apparent", "groupes")
        widgets={
            "groupes": forms.CheckboxSelectMultiple()
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model=models.Article
        fields=("title", "subTitle", "date", "langue")
        widgets={
            "langue":forms.CheckboxSelectMultiple()
        }
    subTitle = forms.CharField(required=False)
    fichier = forms.FileField(required=False)
    audio = forms.FileField(required=False)

    def save(self, commit=True):
        m = super().save(commit=True)
        if "fichier" in self.files:
            try:
                image_set = convert_from_bytes(self.files["fichier"].file.read())
            except Exception as e:
                self.add_error("fichier", e)
                return 0
            print(path.join(settings.MEDIA_ROOT, "static/content/%s" % (m.id)))
            try:
                shutil.rmtree(path.join(settings.MEDIA_ROOT, "static/content/%s" % (m.id) ))
            except Exception:
                pass
            finally:
                mkdir(path.join(settings.MEDIA_ROOT, "static/content/%s" % (m.id)))

            img_id=0
            for img in image_set:
                img_id += 1
                img.save(path.join(settings.MEDIA_ROOT, "static/content/%s/image_%s.jpg" % (m.id, img_id)))
        if "audio" in self.files:
            if self.files["audio"].name[-4:] != ".mp3":
                self.add_error("audio", "The provided file is not an MP3 file")
                return 0

            try:
                shutil.rmtree(path.join(settings.MEDIA_ROOT, "static/content_audio/%s" % (m.id) ))
            except Exception:
                pass
            finally:
                mkdir(path.join(settings.MEDIA_ROOT, "static/content_audio/%s" % (m.id)))
            with open(path.join(settings.MEDIA_ROOT, "static/content_audio/%s/%s" % (m.id, self.files["audio"].name)), 'wb+') as destination:
                for chunk in self.files["audio"].chunks():
                    destination.write(chunk)



class MailFormTest(forms.Form):

    to = forms.ModelChoiceField(queryset=models.ForumGroup.objects.all(), required=True)
    date = forms.DateField(initial=datetime.now().date() + timedelta(weeks=2), required=True)
    langue = forms.CharField(required=True)
    instance = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def save(self):
        subject = "Préparation du DS du %s - %s" % (self.cleaned_data["date"], self.cleaned_data["langue"])
        args = json.dumps({"langue":self.cleaned_data["langue"], "date": datetime.strftime(self.cleaned_data["date"], "%d/%m/%Y")})
        model = models.MailModel.objects.get(id=1)
        if self.cleaned_data["instance"]:
            mail = models.PlannedMail.objects.get(id=self.cleaned_data["instance"])
            mail.to = self.cleaned_data["to"]
            mail.subject = subject
            mail.args = args
            mail.time = self.cleaned_data["date"]-timedelta(weeks=2)

        else:
            mail = models.PlannedMail.objects.create(to=self.cleaned_data["to"], subject=subject, mailModel=model, args=args,
                                                 time=self.cleaned_data["date"]-timedelta(weeks=2))

        mail.save()

    def __init__(self,data=None, files=None, instance=None):
        if instance:
            ret = super().__init__(data=data, files=files, initial={
                "to": instance.to,
                "date": str(datetime.strptime(json.loads(instance.args)["date"], "%d/%m/%Y").date()),
                "langue": json.loads(instance.args)["langue"],
                "instance": instance.id,
            })
        else:
            ret=super().__init__(data=data, files=files)
        return ret

class ExcelImportForm(forms.Form):
    file = forms.FileField()


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    new_password_confirm = forms.CharField(widget=forms.PasswordInput())

