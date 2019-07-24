from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from monApp import forms, models, util
from os import listdir


def home(request):
    # On s'assure de vider la session
    request.session.flush()
    auth_form = forms.LoginForm(request.POST or None)
    if auth_form.is_valid():
        req = models.ForumUser.objects.filter(
            identifiant=auth_form.cleaned_data["id"],
            password=util.hash(auth_form.cleaned_data["mdp"])).count()
        if req:
            request.session["user"] = models.ForumUser.objects.get(identifiant=auth_form.cleaned_data["id"]).id
            return redirect("forum")
        else:
            return render(request, 'monApp/home.html', {"erreur": "Mauvais identifiant ou mot de passe, veuillez réessayer"})
    else:
        return render(request, 'monApp/home.html')


def forum(request):
    if not request.session.get("user"):
        return HttpResponseForbidden()

    user = models.ForumUser.objects.get(id=request.session["user"])
    if request.session.get("langue_redirect"):
        langue = models.LangueSection.objects.get(id=request.session.get("langue_redirect"))
    else:
        try:
            langue = user.getLangues()[0]
        except IndexError:
            return HttpResponseForbidden()
    return render(request, 'monApp/forum.html', {"user":user, "langue": langue})


# TODO créer fonction redirect génerale
def redirect_langue(request, langue_id):
    user = models.ForumUser.objects.get(id=request.session["user"])
    for langue in user.getLangues():
        if langue.id == langue_id:
            request.session["langue_redirect"] = langue_id
            return redirect("forum")
    return HttpResponseForbidden()


def redirect_article(request, article_id):
    user = models.ForumUser.objects.get(id=request.session["user"])
    article = models.Article.objects.get(id=article_id)
    for langue in user.getLangues():
        if langue in article.langue.all():
            request.session["article_redirect"] = article_id
            return redirect("article")
    return HttpResponseForbidden()


def article(request):
    if not request.session.get("user"):
        return HttpResponseForbidden()
    if not request.session.get("article_redirect"):
        redirect("forum")
    user = models.ForumUser.objects.get(id=request.session["user"])
    article = models.Article.objects.get(id=request.session["article_redirect"])
    return render(request, 'monApp/article.html', {"user": user, "article": article})
