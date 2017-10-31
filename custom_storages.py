from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

#class StaticStorage(S3Boto3Storage):
#    bucket_name ='esnailstatic'
#    location = settings.AWS_STATIC_LOCATION

class PrivateMediaStorage(S3Boto3Storage):
    bucket_name ='esnailmedia'
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    
