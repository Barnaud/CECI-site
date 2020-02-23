from django import forms
from monApp import models, util
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import json
from datetime import datetime, date
from pdf2image import convert_from_bytes
from os import path, mkdir
from Django import settings
import shutil
from hashlib import md5


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



class MailFormTest(forms.ModelForm):

    class Meta:
        model=models.PlannedMail
        fields=("to", "time", "subject", "content")
        widgets={
            "content": forms.Textarea,
        }
        labels={
            "time": "Send date"
        }

class ExcelImportForm(forms.Form):
    file = forms.FileField()


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    new_password_confirm = forms.CharField(widget=forms.PasswordInput())


class ExamResults(forms.Form):
    exam_type = forms.ChoiceField(choices=(("toeic", "Toeic officiel"),
                                           ("widaf","Widaf officiel"),
                                           ('toeic_s5', "Toeic blanc S5"),
                                           ("toeic_s6", "Toeic blanc S6"),
                                           ("widaf_s5", "Widaf blanc S5"),
                                           ("widaf_s6", "Widaf blanc S6")))
    file = forms.FileField()


class ExamInvite(forms.ModelForm):

    class Meta:
        model = models.ExamInvite
        fields=("to", "date", "examType")
        widgets={
            "examType": forms.Select(choices=(("Toeic", "Toeic"), ("Widaf", "Widaf"))),
        }
        labels={"examType":"Exam type"}

    def save(self):
        m = super().save(commit=True)
        for user in m.to.forumuser_set.all():
            hasher = md5()
            string = "%s%s"%(str(m), user.identifiant)
            hasher.update(string.encode("utf-8"))
            hash = hasher.hexdigest()
            item = models.ExamInviteItem.objects.create(user=user, parent=m, link=hash)
            item.save()
            item.send()
