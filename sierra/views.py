from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.db import transaction

import shutil
from re import compile as Re

from pathlib import Path

from .models import AmcProject

def A(path):
    return Path('sierra', path)

def app_local_file(*filenames):
    return Path(settings.BASE_DIR, 'sierra', *filenames)

# test views

def hello(request):
    return HttpResponse('Tadaa')

def world(request):
    return render(request, A('index.html'))

# real views

def create_project(request):
    R = request.POST
    name = R['name'].strip()
    assert Re('[a-zA-Z0-9_-]+').fullmatch(name)
    assert not name.startswith('/')
    
    with transaction.atomic():
        project = AmcProject(path=name)
        assert not project.abs_path.exists()
        project.save()
        
        # creating the project
        project.abs_path.mkdir()
        
        # selecting template
        # TODO: select multiple templates from the documentation (like in the gui)
        # TODO: add custom templates for unif (like, 'from a pdf')
        for name in ['bareme.tex', 'options.xml']:
            shutil.copy(app_local_file('amc_templates', name), project.abs_path)
        
        # project.local_file('bareme.tex')
        # project.local_file('options.xml')

def amc_prepare(request):
    
    return HttpResponse('Ok')
