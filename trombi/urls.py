"""
URL configuration for trombinoscoope project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.trombi, name= "trombi"),
    path ('connexion/', views.connexion,name="connexion"),
    path('dashboard/', views.dashboard, name= "dashboard"),
    path('inscription/', views.inscription, name= "inscription"),
    path('deconnexion/', views.deconnexion, name= "deconnexion"),
    path('profile/<int:id>/', views.profile, name='profile'),
    path('cv/', views.cv, name='cv'),
    path('cv/<int:cv_id>/<str:action>/', views.manage_cv, name='manage_cv'),
    path('info/', views.info, name='info'),
    path('add_info/', views.add_info, name='add_info'),
    path('send/<int:cv_id>/envoyer/', views.send_cv_by_email, name='send_cv_by_email'),
    path('generer_cv/', views.generer_cv, name='generer_cv'),  # Route avec cv_id
    path('creation_cv/<int:id>/', views.creation_cv, name='creation_cv'),  # Route avec cv_id
    path("cv1/", views.creer_cv, name="cv1"),
    path("cv/update/<int:cv_id>/", views.update_cv, name="update_cv"),
    path("new_cv/<int:id>/", views.new_cv, name="new_cv"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
