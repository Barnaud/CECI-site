from django.db import models
from django.utils import timezone
from os import listdir


# Create your models here.
class ArticleType(models.Model):
    nom = models.CharField(max_length=50, null=True)
    img = models.ImageField(upload_to="monApp/static/img/article_icon", null=True)



class ForumGroup(models.Model):
    nom = models.CharField(max_length=30)
    couleur = models.CharField(max_length=10)
    logo = models.ForeignKey("logo", on_delete=models.SET_NULL, null="true")

    list_template = "monApp/admin_group_list.html"
    form_template = "monApp/admin_group_form.html"

    @staticmethod
    def objectList(arg):
        return ForumGroup.objects.all()


class LangueSection(models.Model):
    nom_complet = models.CharField(max_length=50)
    nom_apparent = models.CharField(max_length=50)
    groupes = models.ManyToManyField(ForumGroup)

    list_template = "monApp/admin_section_list.html"

    def getArticles(self):
        return Article.objects.filter(langue=self)

    @staticmethod
    def objectList(arg):
        return LangueSection.objects.all()

class ForumUser(models.Model):
    identifiant = models.CharField(max_length=30)
    password = models.CharField(max_length=300)
    mail = models.EmailField(null = True)
    groupe = models.ManyToManyField(ForumGroup)
    admin = models.BooleanField(default=False)

    list_template = "monApp/admin_user_list.html"

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

class logo(models.Model):
    nom = models.CharField(max_length=50)
    img = models.ImageField(upload_to="monApp/static/img/logo")


class Article(models.Model):
    title = models.CharField(max_length=30, default="untitled_article")
    subTitle = models.CharField(max_length=100, null=True)
    date = models.DateTimeField(default=timezone.now())
    type_id = models.ForeignKey("ArticleType", on_delete=models.PROTECT)
    langue = models.ManyToManyField(LangueSection)

    list_template = "monApp/admin_article_list.html"

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