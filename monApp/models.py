from django.db import models
from django.utils import timezone
from os import listdir
from datetime import datetime
from monApp import util
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import json

# Create your models here.
class ArticleType(models.Model):
    nom = models.CharField(max_length=50, null=True)
    img = models.ImageField(upload_to="static/img/article_icon", null=True)



class ForumGroup(models.Model):

    def __str__(self):
        return self.nom

    nom = models.CharField(max_length=30)
    couleur = models.CharField(max_length=10)
    logo = models.ForeignKey("logo", on_delete=models.SET_NULL, null=True)
    mail = models.EmailField(null=True, max_length=50)

    list_template = "monApp/admin_group_list.html"
    form_template = "monApp/admin_group_form.html"
    form_fields = ("nom", "couleur", "logo")


    @staticmethod
    def objectList(arg):
        return ForumGroup.objects.all()


class LangueSection(models.Model):
    nom_complet = models.CharField(max_length=50)
    nom_apparent = models.CharField(max_length=50)
    groupes = models.ManyToManyField(ForumGroup)

    list_template = "monApp/admin_section_list.html"
    form_template = "monApp/admin_section_form.html"

    def __str__(self):
        return self.nom_complet

    def getArticles(self):
        return Article.objects.filter(langue=self, date__lte=timezone.localdate())

    @staticmethod
    def objectList(arg):
        return LangueSection.objects.all()


class ForumUser(models.Model):
    identifiant = models.CharField(max_length=30, unique=True, null=False)
    password = models.CharField(max_length=300, null=False)
    mail = models.EmailField(null = True)
    groupe = models.ManyToManyField(ForumGroup)
    admin = models.BooleanField(default=False)

    list_template = "monApp/admin_user_list.html"
    form_template = "monApp/admin_user_form.html"

    def __str__(self):
        return self.identifiant


    def getLangues(self):
        langues = []
        for groupe in self.groupe.all():
            langues_groupe = LangueSection.objects.filter(groupes=groupe)
            for langue in langues_groupe:
                if not langue in langues:
                    langues.append(langue)
        return langues

    @staticmethod
    def objectList(arg):
        if arg:
            return ForumUser.objects.filter(groupe=arg)
        else:
            return ForumUser.objects.all()

    def send_init_mail(self):
        if self.mail:
            template = get_template("monApp/mail_templates/addUser.txt")
            mail_content = template.render({"username": self.identifiant,
                                            "password": self.password})
            msg = EmailMultiAlternatives("Bienvenue", mail_content, "test@mail.com", [self.mail])
            msg.send()
        else:
            raise Exception("User has no E-mail")

class logo(models.Model):
    nom = models.CharField(max_length=50)
    img = models.ImageField(upload_to="static/img/logo")


class Article(models.Model):
    title = models.CharField(max_length=30, null=False)
    subTitle = models.CharField(max_length=100, null=True)
    date = models.DateField(default=timezone.now())
    type_id = models.ForeignKey("ArticleType", on_delete=models.PROTECT, default=1)
    langue = models.ManyToManyField(LangueSection)

    list_template = "monApp/admin_article_list.html"
    form_template = "monApp/admin_article_form.html"

    class Meta:
        verbose_name="article"
        ordering=["date"]

    def __str__(self):
        return self.title

    def get_images_path(self):
        path = "monApp/static/content/%s/"%(self.id)
        return ["content/%s/%s"%(self.id, name) for name in listdir(path)]

    @staticmethod
    def objectList(arg=None):
        if arg:
            return Article.objects.filter(langue=arg)
        else:
            return Article.objects.all()


class MailModel(models.Model):
    name = models.CharField(null=False, max_length=50)
    template_txt = models.FilePathField(null=False)
    template_html = models.FilePathField(null=True)

    def __str__(self):
        return self.name


class PlannedMail(models.Model):
    to = models.ForeignKey("ForumGroup", on_delete=models.CASCADE)
    subject = models.CharField(null=True, max_length=50)
    mailModel = models.ForeignKey("MailModel", on_delete=models.PROTECT)
    args = models.TextField(null=True)
    sent = models.BooleanField(default=False)
    time = models.DateTimeField(default=util.endHour(datetime.now()))

    list_template = "monApp/admin_mail_list.html"
    form_template = "monApp/admin_mail_form_test.html"

    @staticmethod
    def objectList(arg=None):
        return PlannedMail.objects.all().order_by("time")

    def __str__(self):
        return "%s - %s - %s/%s/%s" % (self.mailModel,
                                             self.to,
                                             self.time.day,
                                             self.time.month,
                                             self.time.year,
                                             )

    def send(self):
        txt_template = get_template(self.mailModel.template_txt)
        if self.mailModel.template_html:
            html_template = get_template(self.mailModel.template_html)
        else:
            html_template = None
        args = json.loads(self.args)
        if "user_dest" in args or not self.to.mail:
            if args["user_dest"] == "auto" or not self.to.mail:
                for user in self.to.forumuser_set:
                    temp_arg = args
                    temp_arg["user"] = user
                    txt_content = txt_template.render(temp_arg)
                    msg = EmailMultiAlternatives(self.mailModel.subject, txt_content, "test@mail.com", [user.mail])
                    if self.mailModel.template_html:
                        html_content = html_template.render(temp_arg)
                        msg.attach_alternative(html_content, "text/html")
                    ret = msg.send()
        else:
            txt_content = txt_template.render(args)
            msg = EmailMultiAlternatives(self.mailModel.subject, txt_content, "test@mail.com", [self.to.mail])
            ret = msg.send()
        if ret:
            self.delete()
        else:
            util.report("Erreur d'envoi d'un mail")
