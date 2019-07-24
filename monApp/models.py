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


class LangueSection(models.Model):
    nom_complet = models.CharField(max_length=50)
    nom_apparent = models.CharField(max_length=50)
    groupes = models.ManyToManyField(ForumGroup)

    def getArticles(self):
        return Article.objects.filter(langue=self)


class ForumUser(models.Model):
    identifiant = models.CharField(max_length=30)
    password = models.CharField(max_length=300)
    mail = models.EmailField(null = True)
    groupe = models.ManyToManyField(ForumGroup)

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


class logo(models.Model):
    nom = models.CharField(max_length=50)
    img = models.ImageField(upload_to="monApp/static/img/logo")


class Article(models.Model):
    title = models.CharField(max_length=30, default="untitled_article")
    subTitle = models.CharField(max_length=100, null=True)
    date = models.DateTimeField(auto_now_add=True)
    type_id = models.ForeignKey("ArticleType", on_delete=models.PROTECT)
    langue = models.ManyToManyField(LangueSection)

    class Meta:
        verbose_name="article"
        ordering=["date"]

    def __str__(self):
        return self.title

    def get_images_path(self):
        path = "monApp/static/content/%s/"%(self.id)
        return ["content/%s/%s"%(self.id, name) for name in listdir(path)]
