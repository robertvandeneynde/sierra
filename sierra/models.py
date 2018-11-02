from django.db import models
from django.db.models import Model, CharField, ForeignKey, IntegerField

from django.conf import settings
from django.utils import timezone

from pathlib import Path

from re import compile as Re

def FK(*args, **kwargs):
    return models.ForeignKey(*args, **kwargs, on_delete=models.PROTECT)

class AmcProject(Model):
    # Fields
    rel_path = CharField(max_length=100, unique=True)  # if not startswith('/'): relative to settings.AMC_BASE_PATH
    
    # Class attributes
    root_path = Path(settings.AMC_BASE_PATH)
    
    # Class attributes (namespaced)
    class re:
        STANDARD = Re('[a-zA-Z0-9_-]+')
    
    # Object attributes (depend on Fields only)
    @property
    def abs_path(self) -> Path:
        return (self.root_path / self.rel_path if not self.rel_path.startswith('/') else
                Path(self.rel_path))
    
    @classmethod
    def get_by_likeid(cls, likeid):
        ''' Currently the likeid is the rel_path, but it may get smarter later '''
        return cls.objects.get(rel_path=likeid)
    
    # Object attributes (depend on external sources)
    def local_file(self, *rels, existing=None) -> Path:
        out = Path(self.abs_path, *rels)
        if existing == True and not out.exists():
            raise ValueError
        if existing == False and out.exists():
            raise ValueError
        return out
    
    def has_source(self) -> bool:
        return (self.abs_path / 'source.tex').is_file()
    
    def source_stat(self):
        import os
        stat = os.stat(self.abs_path / 'source.tex')
        return "{} bytes, modified {:%Y-%m-%d %H:%S}".format(
            stat.st_size,
            timezone.datetime.fromtimestamp(stat.st_mtime))
