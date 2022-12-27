# Django Storages
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_SECURE_URLS = True
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 24*60*60
AWS_BUCKET_ACL = 'private'
AWS_DEFAULT_ACL = 'private'
