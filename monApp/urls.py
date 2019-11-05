from django.urls import path
from monApp import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home),
    path('change_password', views.change_password),
    path('deco', views.deco),
    path('accueil', views.forum, name='forum'),
    path('accueil/langue/<int:langue_id>', views.redirect_langue),
    path('accueil/article/<int:article_id>', views.redirect_article),
    path('accueil/article', views.article, name="article"),
    path('admin', views.admin, name="admin"),
    path('admin/<str:model>/<str:action>', views.admin, name="admin"),
    path('admin/<str:model>/<str:action>/<int:arg>', views.admin, name="admin"),
    path('admin/test', views.test),
    path('admin/excel_import', views.user_import, name="user_import"),
    path('admin/user/<int:arg>/newPassword', views.newPassword, name="newPassword"),
    path('admin/exam_extract', views.examExtract, name="examExtract")

]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
