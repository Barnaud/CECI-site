from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from monApp import forms, models, util
from django.forms import modelform_factory
from django.core.mail import EmailMultiAlternatives
from os import listdir


def home(request):

    auth_form = forms.LoginForm(request.POST or None)
    if auth_form.is_valid():
        req = models.ForumUser.objects.filter(
            identifiant=auth_form.cleaned_data["id"],
            password=util.hash(auth_form.cleaned_data["mdp"])).count()
        if req == 1:
            request.session["user"] = models.ForumUser.objects.get(identifiant=auth_form.cleaned_data["id"]).id
            if models.ForumUser.objects.get(identifiant=auth_form.cleaned_data["id"]).admin:
                return  redirect("admin")
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
        return redirect("forum")
    user = models.ForumUser.objects.get(id=request.session["user"])
    article = models.Article.objects.get(id=request.session["article_redirect"])
    return render(request, 'monApp/article.html', {"user": user, "article": article})


def deco(request):
    # On s'assure de vider la session
    for key in request.session.keys():
        request.session[key] = None
    return redirect(home)


def admin(request, model = "group", action="list", arg=None):
    if not request.session.get("user"):
        return HttpResponseForbidden()
    if not models.ForumUser.objects.get(id=request.session.get("user")).admin:
        return HttpResponseForbidden()

    modelDict = {
        "group": models.ForumGroup,
        "user": models.ForumUser,
        "section": models.LangueSection,
        "article": models.Article,
        "mail": models.PlannedMail,
    }
    formDict = {
        "group": forms.GroupForm,
        "user": forms.UserForm,
        "section": forms.SectionForm,
        "article": forms.ArticleForm,
        "mail": forms.MailFormTest,
    }

    success = None

    if not model in modelDict:
        return Http404()
    if action == "list":
        return render(request, modelDict[model].list_template, {"objectList": modelDict[model].objectList(arg)})
    elif action == "add":
        form = formDict[model](request.POST or None, request.FILES or None)
        if request.method == "POST":
            if form.is_valid():
                form.save()
                success = True
        return render (request, modelDict[model].form_template, {"form": form,"success":success})
    elif action == "edit" and arg:
        try:
            obj = modelDict[model].objects.get(id=arg)
        except modelDict[model].DoesNotExist:
            raise Http404()

        form = formDict[model](request.POST or None, request.FILES or None, instance=obj)
        if request.method == "POST":
            if form.is_valid():
                form.save()
                success = True
        return render(request, modelDict[model].form_template, {"form": form, "success": success})
    elif action == "delete" and arg:
        try :
            obj = modelDict[model].objects.get(id=arg)
        except modelDict[model].DoesNotExist:
            raise Http404()
        obj.delete()
        return redirect("admin")



def user_import(request):
    if not request.session.get("user"):
        return HttpResponseForbidden()
    if not models.ForumUser.objects.get(id=request.session.get("user")).admin:
        return HttpResponseForbidden()

    form = forms.ExcelImportForm(request.POST or None, request.FILES or None)
    if request.FILES and form.is_valid():
        excel_dict = util.excel_read(form.files["file"].open())
        try:
            util.check_excel_dict(excel_dict)
        except Exception as e:
            form.add_error("file",e)
        else:
            for user in excel_dict:
                password = util.gen_passwd(10)
                group = models.ForumGroup.objects.get(nom=user["groupe"])
                new_user = models.ForumUser.objects.create(
                    identifiant=user["identifiant"],
                    password=password,
                    mail=user["mail"],
                )
                new_user.groupe.add(group)
                new_user.save()
                new_user.send_init_mail()
    return render(request, "monApp/admin_excel_import.html", {"form": form})

def test(request):
    mail = models.PlannedMail.objects.get(id=1)
    mail.send()
    return HttpResponse("oui.")

def change_password(request):
    if not request.session.get("user"):
        return HttpResponseForbidden()

    form = forms.ChangePasswordForm(request.POST or None)
    user = models.ForumUser.objects.get(id=request.session.get("user"))
    print("yes")

    if form.is_valid():
        if str(util.hash(form.cleaned_data["old_password"])) == user.password:
            if form.cleaned_data["new_password"] == form.cleaned_data["new_password_confirm"]:
                user.password = util.hash(form.cleaned_data["new_password"])
                user.save()
                return redirect("forum")
            else:
                form.add_error("new_password_confirm", "La confirmation de mot de passe ne correspond pas au premier mot de passe entré")
        else:
            form.add_error("old_password", "Mauvais mot de passe")

    return render(request, "monApp/change_password.html", {"form": form, "user": user})

def newPassword(request, arg):
    if not request.session.get("user"):
        return HttpResponseForbidden()
    if not models.ForumUser.objects.get(id=request.session.get("user")).admin:
        return HttpResponseForbidden()

    try:
        user = models.ForumUser.objects.get(id=arg)
    except Exception:
        return HttpResponseForbidden

    try:
        user.send_newpassword()
    except Exception:
        return HttpResponseForbidden

    return redirect("admin")


def examExtract(request):
    form = forms.ExamResults(request.POST or None, request.FILES or None)
    if form.is_valid() and request.FILES:
        if(form.cleaned_data["exam_type"] == "toeic"):
            try:
                mails = util.toeicExtract(form.files["file"])
            except Exception:
                form.add_error("file", "Erreur avec le fichier, veuillez vérifier")
                return render(request, "monApp/admin_send_results.html", {"form": form})
        elif(form.cleaned_data["exam_type"] == "widaf"):
            try:
                mails = util.widafExtract(form.files["file"])
            except Exception:
                form.add_error("file", "Erreur avec le fichier, veuillez vérifier")
                return render(request, "monApp/admin_send_results.html", {"form": form})
        else:
            raise HttpResponseForbidden
        for mail in mails:
            msg = EmailMultiAlternatives("Resultats %s"%(form.cleaned_data["exam_type"]), mail["content"], "noreply@docs-ceci-formation.fr", [mail["mail"]])
            msg.send()
    return render(request, "monApp/admin_send_results.html", {"form":form})