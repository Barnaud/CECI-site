from django.urls import path
from monApp import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home),
    path('accueil', views.forum, name='forum'),
    path('accueil/langue/<int:langue_id>', views.redirect_langue),
    path('accueil/article/<int:article_id>', views.redirect_article),
    path('accueil/article', views.article, name="article")
]

