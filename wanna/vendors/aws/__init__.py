from wanna.utils import md5sum
from wanna.utils import ProgressPercentage
from wanna.utils import ignore_ctrl_c
from wanna.utils import touch
from wanna.settings import Config

from boto3.s3.transfer import S3Transfer
from botocore.client import Config as BotoConfig

import boto3
import os.path


class _AWS(object):
    """AWS vendor"""

    @property
    def service(self):
        return 's3'

    @property
    def name(self):
        return 'aws'

    def __init__(self, use_encryption=True, ignore_prefix=False):
        config = Config(self)
        self._bucket = config.BUCKET
        self._prefix = os.path.join(config.UPLOAD_PREFIX, config.PARTNER_NAME)
        self._encrypt = use_encryption
        self.client = boto3.client(
            self.service,
            aws_access_key_id=config.VENDOR.API_KEY,
            aws_secret_access_key=config.VENDOR.API_SECRET,
            config=BotoConfig(signature_version='s3v4')
        )
        self._transfer = S3Transfer
        self._checksum = None
        self.ignore_prefix = ignore_prefix
        self.config = config

        if self.ignore_prefix:
            self._prefix = ''

    def get_extra_args(self):
        """Extra parameters"""
        args = {}
        if self._encrypt:
            args.update({
                'SSECustomerKey': self.config.ENCRYPTION_KEY,
                'SSECustomerAlgorithm': self.config.ENCRYPTION_ALGORITHM
            })
        return args

    def get_obj_key(self, path, md5=False):
        """Get file object key"""
        key = os.path.join(self._prefix, os.path.basename(path))
        if md5 is True:
            key = key + '.md5'
        return key

    def get_checksum(self, path):
        """Calculate control sum"""
        if self._checksum is None:
            self._checksum = md5sum(path)
        return self._checksum

    def upload_checksum(self, path):
        """Upload md5sum for the given file"""
        key = self.get_obj_key(path, md5=True) if not self.ignore_prefix else path
        response = self.client.put_object(Bucket=self._bucket, Key=key, Body=self.get_checksum(path))
        return response

    def upload_file(self, path, progress=False):
        """Upload a file"""
        key = self.get_obj_key(path)
        progress_callback = ProgressPercentage(path) if progress else lambda x: None
        extra_args = self.get_extra_args()

        with ignore_ctrl_c():
            with self._transfer(self.client) as transfer:
                response = transfer.upload_file(
                    path, self._bucket, key, extra_args=extra_args, callback=progress_callback)

        return response

    def check_if_key_exists(key):
        pass

    def download_file(self, path, progress=False):
        """Download a file"""
        touch('./{}'.format(path))
        key = self.get_obj_key(path)
        progress_callback = ProgressPercentage(path) if progress else lambda x: None
        extra_args = self.get_extra_args()

        with ignore_ctrl_c():
            with self._transfer(self.client) as transfer:
                response = transfer.download_file(
                    self._bucket, key, './{}'.format(path), extra_args=extra_args, callback=progress_callback)
        return response

    def list_files(self, progress=False):
        """List files"""
        with ignore_ctrl_c():
            resp = self.client.list_objects_v2(Bucket=self._bucket, Prefix=self._prefix)
            if 'Contents' in resp:
                for el in resp['Contents']:
                    print('{}\t {}\t {}'.format(el['LastModified'].isoformat(), el['Size'], el['Key']))
            else:
                print('no files')
