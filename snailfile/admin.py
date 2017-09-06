from django.contrib import admin
from .models import Tag
from .models import FilePackage
from .models import FileAttachment

# Register your models here.
admin.site.register(Tag)
admin.site.register(FilePackage)
admin.site.register(FileAttachment)