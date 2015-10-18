import boto
import time
import hashlib

from random import randint
from django.conf import settings
from tempfile import TemporaryFile

AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None


class AWSManagerSettingsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AWSManagerCloudException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AWSManager(object):
    def __init__(self, *args, **kwargs):
        self.bucket = kwargs.get('bucket')
        self.api_key = kwargs.get('api_key', '')
        self.secret_key = kwargs.get('secret_key', '')
        self.host = kwargs.get('host', None)

        self.accepted_extensions = ['jpg', 'gif', 'png']
        self.rejected_extensions = ['exe', 'py', 'sh']

        self.aws_key_obj = None
        self.aws_key_name = ''

    def set_credentials(self):
        if AWS_ACCESS_KEY_ID is None:
            AWS_SECRET_ACCESS_KEY = self.api_key if self.api_key is not None else settings.AWS_API_KEY

        if AWS_SECRET_ACCESS_KEY is None:
            AWS_SECRET_ACCESS_KEY = self.secret_key if self.secret_key is not None else settings.AWS_SECRET_KEY

    def connect(self):
        self.check_settings()
        self.set_credentials()
        return boto.connect_s3(aws_access_key_id=settings.AWS_API_KEY, aws_secret_access_key=settings.AWS_SECRET_KEY, host=self.host)

    def check_settings(self):
        if not hasattr(settings, 'AWS_API_KEY'):
            raise AWSManagerSettingsException("Api key not found, please set up your settings correctly")
        if not hasattr(settings, 'AWS_SECRET_KEY'):
            raise AWSManagerSettingsException("Secret key not found, please set up your settings correctly")
        if not hasattr(settings, 'AWS_BUCKET'):
            raise AWSManagerSettingsException("Bucket name not found, please set up your settings correctly")
        if not hasattr(settings, 'AWS_KEY_PREFIX'):
            raise AWSManagerSettingsException("Prefix key not found, please set up your settings correctly")

        self.bucket = settings.AWS_BUCKET

    def add_accepted_files(self, extension):
        if extension.lower() not in self.rejected_extensions and extension.lower() not in self.accepted_extensions:
            self.accepted_extensions.append(extension.lower())
            return True
        else:
            return False

    def add_rejected_files(self, extension):
        if extension.lower() in self.accepted_extensions and extension.lower() not in self.rejected_extensions:
            self.accepted_extensions.remove(extension.lower())

        if extension.lower() not in self.rejected_extensions:
            self.rejected_extensions.append(extension.lower())
            return True
        else:
            return False

    def file_is_correct(self, file_name):
        extension = file_name.split('.')[1].encode('utf-8')
        if extension.lower() in self.accepted_extensions and extension.lower() not in self.rejected_extensions:
            return True
        else:
            return False

    def get_name_file_aws(self, file_name, bucket):
        hash_mds = hashlib.md5('{0}{1}'.format(str(time.time()), file_name.split('.')[0].encode('utf-8'))).hexdigest()
        file_lookup = u'{0}{1}'.format(settings.AWS_KEY_PREFIX, hash_mds)

        if bucket.get_key(file_lookup) is None:
            return file_lookup
        else:
            hash_mds = hashlib.md5('{0}{1}'.format(str(time.time()), file_name.split('.')[0].encode('utf-8'))).hexdigest()
            return u'{0}{1}'.format(settings.AWS_KEY_PREFIX, hash_mds)

    def upload(self, file_name, file_obj):
        if not self.file_is_correct(file_name):
            return "The name of file is invalid"

        file_obj.seek(0)

        aws = self.connect()

        #test permissions
        aws_bucket = aws.lookup(self.bucket)

        if not aws_bucket:
            raise AWSManagerCloudException('Bucket not found, please ensure that such Bucket exists')

        aws_new_key = aws_bucket.new_key(self.get_name_file_aws(file_name, aws_bucket))

        try:
            aws_new_key.set_contents_from_file(file_obj, replace=False)
        except Exception, e:
            raise AWSManagerCloudException('Error during uploading file - {0}'.format(e))

        # size_file = file_obj.size
        # size_file_aws = aws_new_key.size

        # if size_file != size_file_aws:
        #     aws_new_key.delete()
        #     raise AWSManagerCloudException('Error during uploading file - {0} saved bytes of {1}'.format(str(size_file_aws), str(size_file)))

        self.aws_key_obj = aws_new_key
        self.aws_key_name = aws_new_key.key

        return True

    def open(self, key_name):
        if not key_name:
            return False

        aws = self.connect()

        #test permissions
        aws_bucket = aws.lookup(self.bucket)

        if not aws_bucket:
            raise AWSManagerCloudException('Bucket not found, please ensure that such Bucket exists')

        aws_key = aws_bucket.get_key(key_name)

        result = TemporaryFile()
        aws_key.get_file(result)

        return result

    def update_key(self, key_name=None, file_obj=None):
        if not key_name:
            return False

        aws = self.connect()

        #test permissions
        aws_bucket = aws.lookup(self.bucket)

        if not aws_bucket:
            raise AWSManagerCloudException('Bucket not found, please ensure that such Bucket exists')

        aws_key = aws_bucket.get_key(key_name)

        try:
            aws_key.set_contents_from_file(file_obj, replace=False)
        except Exception, e:
            raise AWSManagerCloudException('Error during uploading file - {0}'.format(e))

        size_file = file_obj.size
        size_file_aws = aws_key.size

        if size_file != size_file_aws:
            aws_key.delete()
            raise AWSManagerCloudException('Error during uploading file - {0} saved bytes of {1}'.format(str(size_file_aws), str(size_file)))

        self.aws_key_obj = aws_key
        self.aws_key_name = aws_key.key

        return True

    def delete_key(self, key_name=None):
        if not key_name:
            return False

        aws = self.connect()

        #test permissions
        aws_bucket = aws.lookup(self.bucket)

        if not aws_bucket:
            raise AWSManagerCloudException('Bucket not found, please ensure that such Bucket exists')

        aws_key = aws_bucket.get_key(key_name)

        if not aws_key:
            raise AWSManagerCloudException('Key not found, please ensure that such Key exists')

        aws_key.delete()

        return True

    def set_key_object(self, key_name=None):
        if not key_name:
            return False

        aws = self.connect()
        #test permissions
        aws_bucket = aws.lookup(self.bucket)

        if not aws_bucket:
            raise AWSManagerCloudException('Bucket not found, please ensure that such Bucket exists')

        aws_key = aws_bucket.get_key(key_name)
        if not aws_key:
            return False
        self.aws_key_obj = aws_key
        self.aws_key_name = aws_key.key
        return True

    def url(self, expires=30, force_http=True, method='GET', query_auth=True):
        if self.aws_key_obj is None:
            return None

        #Seconds to days
        real_expires = (60 * 60 * 24) * expires
        return self.aws_key_obj.generate_url(expires_in=0, method=method, force_http=force_http, query_auth=False)
