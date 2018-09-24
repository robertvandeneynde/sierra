from django.db import models
from django.db.models import Model, CharField, ForeignKey, IntegerField

from django.conf import settings

from pathlib import Path

from re import compile as Re

def FK(*args, **kwargs):
    return models.ForeignKey(*args, **kwargs, on_delete=models.PROTECT)

class AmcProject(Model):
    # Fields
    rel_path = CharField(max_length=100, unique=True)  # relative to some dir settings.AMC_BASE_PATH
    
    # Class attributes
    root_path = Path(settings.AMC_BASE_PATH)
    
    # Class attributes (namespaced)
    class re:
        STANDARD = Re('[a-zA-Z0-9_-]+')
    
    # Object attributes (depend on Fields ²only)
    @property
    def abs_path(self) -> Path:
        return self.root_path / self.rel_path
    
    # Object attributes (depend on external sources)
    def local_file(self, *rels, existing=None) -> Path:
        out = Path(self.abs_path, *rels)
        if existing == True and not out.exists():
            raise ValueError
        if existing == False and out.exists():
            raise ValueError
        return out
