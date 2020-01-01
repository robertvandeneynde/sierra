from django.urls import path

from . import views

urlpatterns = [
    # first urls
    path('', views.homepage),
    path('hello/', views.hello),
    
    # cool uris don't change
    path('projects/', views.list_projects),
    
    # those urls do change, they are 100% related to python code
    path('raw/create_project/', views.create_project),
    path('raw/list_projects/', views.list_projects),
    path('raw/import_from_filesystem/', views.import_from_filesystem),
    
    path('raw/project/upload_source/', views.project_upload_source),
    path('raw/project/upload_scans/', views.project_upload_scans),
    path('raw/project/upload_scans_with_qr/', views.upload_scans_with_qr),
    
    path('project/<likeid>/', views.project_detail),
    path('project/<likeid>/papers', views.project_list_papers),
]
