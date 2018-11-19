from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound
from django.conf import settings
from django.db import transaction
from django.utils import timezone

# aliases
Http200, Http301, Http400, Http404 = \
HttpOk, HttpRedirect, HttpBadRequest, HttpNotFound = \
    HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound

import shutil
from re import compile as Re

from pathlib import Path

from .models import AmcProject

from functools import partial

def A(path):
    return Path('sierra', path)

def app_local_file(*filenames):
    return Path(settings.BASE_DIR, 'sierra', *filenames)

# test views

def hello(request):
    return HttpResponse('Tadaa')

# first views

def homepage(request):
    return render(request, A('index.html'))

# utils
class QuickHtml:
    BASE_LINKS = [
        '/',
    ]
    
    LINKS_NAMES = {
        '/': '&#x2302;&nbsp;Home',
    }
    
    @staticmethod
    def enclose(x,y):
        """
        >>> enclose('<li>', 'hello')
        <li>hello</li>
        >>> enclose('li', 'hello')
        <li>hello</li>
        """
        if Re("<(.*)>").fullmatch(x):
            x = Re("<(.*)>").fullmatch(x).group(1)
            return '<' + x + '>' + y + '</' + x + '>'
    
    @classmethod
    def base_links(cls, x, *, position='after'):
        y = '<br/>'.join('<a href="{}">{}</a>'.format(z, cls.LINKS_NAMES.get(z,z)) for z in cls.BASE_LINKS)
        l = [x, cls.enclose('<footer>', y)]
        return '\n'.join(l if position == 'after' else reversed(l))
    
    # Helpers
    @classmethod
    def base_links_before(cls, x):
        return cls.base_links(x, position='before')
    
    @classmethod
    def base_links_after(cls, x):
        return cls.base_links(x, position='after')
    
# real views

def create_project(request):
    R = request.POST
    name = R['name'].strip()
    mnemo = R.get('mnemo', '')
    academic_year_append = R.get('academic_year_append', False)
    
    if academic_year_append:
        N = timezone.now()
        x = N.year if (N.month, N.day) >= (9, 1) else N.year - 1
        name = name + '_' + f'{x}-{x+1}'
    
    if mnemo:
        name = mnemo + '_' + name
        
    assert AmcProject.re.STANDARD.fullmatch(name)
    assert not name.startswith('/')
    
    with transaction.atomic():
        project = AmcProject(rel_path=name)
        
        if project.abs_path.exists():
            return Http400(f"Project {name!r} already exists (on filepath)") 
        
        try:
            project.save()
        except: # Pokemon
            return Http400(f"Project {name!r} already exists (in db)")
        
        # creating the project
        project.abs_path.mkdir()
        
        # selecting template
        # TODO: select multiple templates from the documentation (like in the gui)
        # TODO: add custom templates for unif (like, 'from a pdf')
        for f in ['bareme.tex', 'options.xml']:
            shutil.copy(app_local_file('amc_templates', f), project.abs_path)
        
        # project.local_file('bareme.tex')
        # project.local_file('options.xml')
        
        return HttpResponse(f'Project <b>{name}</b> created !')  # redirect('/projects')

def import_from_filesystem(request):
    assert request.method == 'POST'
    R = request.POST
    
    name = R['name'].strip()
    if not AmcProject.re.STANDARD.fullmatch(name):
        return Http400(f"Can't import name {name!r}, contains weird characters")
    
    project = AmcProject(rel_path=name)
    
    with transaction.atomic():
        assert not AmcProject.objects.filter(rel_path=project.rel_path).exists()
        project.save()
    
    return HttpResponse(QuickHtml.base_links_after('Ok'))

def list_projects(request):
    assert request.method == 'GET'
    R = request.GET
    
    mysorted = partial(sorted, key=lambda t:(not t[0], t[1]))
    
    data = mysorted(
        (AmcProject.objects.filter(rel_path=rel_path).exists(),
         rel_path)
        for path in filter(Path.is_dir, AmcProject.root_path.iterdir())
        for rel_path in [ str(path.relative_to(AmcProject.root_path)) ])
    
    return render(request, A('project-list.html'), {'data':data})
    
    return HttpResponse(QuickHtml.base_links(QuickHtml.enclose('<ul>', '<br/>'.join(
        QuickHtml.enclose('<li>', '{0}<a href="/amc/project/{1}">{1}</a>'.format('&#x2204;&nbsp;' * (not exists), name))
        for exists, name in data
    ))))

def project_detail(request, likeid):
    assert request.method == 'GET'
    
    project = AmcProject.objects.get(rel_path=likeid)
    # [n.parts[-1] for n in (project.abs_path / 'data').iterdir()]
    
    # raise ''
    
    return render(request, A('project.html'), {
        'project': project
    })

def compile_project(project):
    import subprocess
    from subprocess import PIPE, STDOUT
    r = subprocess.check_output([
        'auto-multiple-choice',
        'prepare', 
        '--mode', 's',
        '--out-sujet', 'subject.pdf',
        'source.tex',
    ], cwd=project.abs_path, stderr=STDOUT)
    
    # here no exception
    # project.does_compile = True
    # project.save()
    return HttpResponse(QuickHtml.enclose('<pre>',  r.decode('utf-8', 'replace')))

def project_upload_scans(request):
    assert request.method == 'POST'
    
    R = request.POST
    
    if "project_likeid" in R:
        project = AmcProject.get_by_likeid(R["project_likeid"])
    else:
        project = AmcProject.objects.get(id=R["project_id"])
    
    scans = project.abs_path / 'scans'
    scans.mkdir(exist_ok=True)
    
    import itertools
    it = itertools.count(1)
    
    from os.path import splitext
    
    now = timezone.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    uploaded = []
    for f in request.FILES.getlist('scans'):
        ext = splitext(f.name)[-1].lower()
        new_file = scans / '{}_{}{}'.format(now, next(it), ext) 
        assert not new_file.exists()
        with open(new_file, 'wb') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        uploaded.append(new_file)
    
    import subprocess
    from subprocess import PIPE, STDOUT
    r = subprocess.check_output([
        'auto-multiple-choice',
        'analyse', 
        # '--seuil-coche', '0.6',  # read from options.xml for compability with GUI
        '--projet', str(project.abs_path),
        *(str(u.absolute()) for u in uploaded)
    ], cwd=project.abs_path, stderr=STDOUT)
    
    # each line is in +///+ notation
    # if the scan is not good, it will be in the sqlite (capture_failed table, containing capture_failed.filename with %PROJET)
    # else, it will be in capture_page table, with src startswith '%PROJET/' (student, page, copy)
    
    return HttpResponse(QuickHtml.enclose('<pre>',  r.decode('utf-8', 'replace')))

def project_upload_source(request):
    assert request.method == 'POST'
    
    R = request.POST
    
    if "project_likeid" in R:
        project = AmcProject.get_by_likeid(R["project_likeid"])
    else:
        project = AmcProject.objects.get(id=R["project_id"])
    
    if 'source' not in request.FILES:
        return Http400("400")
    
    if project.has_source():
        pass  # chill
    
    with open(project.abs_path / 'source.tex', 'wb') as f:
        f.write(request.FILES['source'].read())
        
    return compile_project(project)
    
    return HttpResponse('Ok')
