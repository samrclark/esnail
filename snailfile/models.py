from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import Group

class Tag(models.Model): 
    tagtext = models.CharField(max_length=64)
    def __str__(self):
        return self.tagtext

class FileAttachment(models.Model):
    filepackage = models.ForeignKey('FilePackage', on_delete=models.CASCADE)
    originalfilename = models.CharField(verbose_name='Original Filename', max_length=256)
#    #django storages ID thing here instead of base file class
    afile = models.FileField(verbose_name='File', upload_to='attachments/')
    def __str__(self):
        return self.originalfilename

class FilePackage(models.Model):
    pprovnum = models.CharField(verbose_name='Provider Number', max_length=6)
    pfye = models.DateField(verbose_name='Fiscal Year End')
    ptitle = models.TextField(verbose_name='Package Title')
    pdescription = models.TextField(verbose_name='Package Description')
    accessiblebyusers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='accessiblefp')
    accessiblebygroups = models.ManyToManyField(Group)
    tags = models.ManyToManyField(Tag)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='createdfp')
    created_date = models.DateField(auto_now_add=True)
    #fileattachments = models.ForeignKey('FileAttachment', blank=True, null=True, on_delete=models.CASCADE) 
    def __str__(self):
        return self.ptitle

