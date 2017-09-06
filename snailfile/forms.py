from django import forms
from snailfile.models import FileAttachment
from snailfile.models import FilePackage
from snailfile.models import Tag



class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('tagtext',)

class FilePackageForm(forms.ModelForm):
    class Meta:
        model= FilePackage
        fields = ('pprovnum', 'pfye', 'ptitle', 'pdescription',)


class FileAttachmentForm(forms.ModelForm):
    class Meta:
        model = FileAttachment
#        fields = ('filepackage', 'originalfilename', 'adescription', 'afile',)
        fields = ('afile',)
        file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

        