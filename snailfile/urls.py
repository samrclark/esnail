from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^upload$', views.PackageCreation, name='file_upload'),
    url(r'^packagedetail/$', views.PackageDetail, name='packagedetail'),
    url(r'^packagedetail/([0-9]+)/$', views.PackageDetail, name='packagedetail'),
    url(r'^packagecreated$', views.PackageCreated, name='packagecreated'),
    url(r'^vocredentialpage$', views.VOCredentialPage, name='vocredentialpage'),
    url(r'^vocregen/([0-9]+)/$', views.VOCRegen, name='vocregen'),
    url(r'^packagedelete/([0-9]+)/$', views.PackageDelete, name='packagedelete'),
    url(r'^edit/([0-9]+)/$', views.PackageEdit, name='edit'),
]