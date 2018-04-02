from django.urls import path

from . import views

urlpatterns = [
    path('', views.world),
    path('hello/', views.hello),
]
