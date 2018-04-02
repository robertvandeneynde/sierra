from django.db import models
from django.db.models import Model, CharField, ForeignKey, IntegerField

from django.conf import settings

from pathlib import Path

def FK(*args, **kwargs):
    return models.ForeignKey(*args, **kwargs, on_delete=models.PROTECT)

class AmcProject(Model):
    path = CharField(max_length=100, unique=True) # relative to some dir settings.AMC_BASE_PATH
    
    @property
    def abs_path(self):
        return Path(settings.AMC_BASE_PATH, self.path)
    
    def local_file(self, *rels, existing=None):
        out = Path(self.abs_path, *rels)
        if existing == True and not out.exists():
            raise ValueError
        if existing == False and out.exists():
            raise ValueError
        return out
