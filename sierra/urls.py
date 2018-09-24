from django.urls import path

from . import views

urlpatterns = [
    path('', views.world),
    path('hello/', views.hello),
    path('raw/create_project/', views.create_project),
    path('raw/list_projects/', views.list_projects),
    path('raw/import_from_filesystem/', views.import_from_filesystem),
    
    path('amc/project/<likeid>', views.project_detail),
]
