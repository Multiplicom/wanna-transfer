"""S3 service from aws

Features:
   * upload object
   * download object
   * list objects
   * delete object
   * rename object
   * get object size
   * check the integrity via control sum
   * simple fuzzy search
"""
from wanna.utils import md5sum
from wanna.utils import ProgressPercentage
from wanna.utils import ignore_ctrl_c
from wanna.utils import touch
from wanna.utils import fuzzyfinder

from wanna.settings import Config

from boto3.s3.transfer import S3Transfer
from botocore.client import Config as BotoConfig

import boto3
import os.path
import logging


LOG = logging.getLogger(__name__)


class _AWS(object):
    """AWS s3 service"""
    hash_checksum = '.md5'
    signature_version = 's3v4'
    region_name = 'eu-central-1'

    @property
    def service(self):
        return 's3'

    @property
    def name(self):
        return 'aws'

    def _get_config(self, config):
        return {
            'aws_access_key_id': config.VENDOR.API_KEY,
            'aws_secret_access_key': config.VENDOR.API_SECRET,
            'config': BotoConfig(signature_version=self.signature_version,
                                 region_name=self.region_name)
        }

    def __init__(self, use_encryption=True, ignore_prefix=False):
        config = Config(self)
        self._bucket = config.BUCKET
        self._prefix = os.path.join(config.UPLOAD_PREFIX, config.PARTNER_NAME)
        self._encrypt = use_encryption
        self.client = boto3.client(self.service, **self._get_config(config))
        self.resource = boto3.resource('s3', **self._get_config(config))
        self._transfer = S3Transfer
        self._checksum = None
        self.ignore_prefix = ignore_prefix
        self.config = config

        if self.ignore_prefix:
            self._prefix = ''

    def _get_extra_args(self):
        """Extra parameters"""
        args = {}
        if self._encrypt:
            LOG.info('using encryption: {}'.format(self.config.ENCRYPTION_ALGORITHM))
            args.update({
                'SSECustomerAlgorithm': self.config.ENCRYPTION_ALGORITHM,
                'SSECustomerKey': self.config.ENCRYPTION_KEY,
            })
        return args

    def get_obj_key(self, path, md5=False):
        """Get file object key"""
        key = os.path.join(self._prefix, os.path.basename(path))
        if md5 is True:
            key = key + self.hash_checksum
        return key

    def get_checksum(self, path):
        """Calculate control sum"""
        if self._checksum is None:
            self._checksum = md5sum(path)
        return self._checksum

    def upload_checksum(self, path):
        """Upload control sum for the given file"""
        LOG.info('uploading checksum')
        key = self.get_obj_key(path, md5=True) if not self.ignore_prefix else path
        checksum = self.get_checksum(path)
        response = self.client.put_object(Bucket=self._bucket, Key=key, Body=checksum)
        LOG.info('checksum ({}): {}'.format(self.hash_checksum, checksum))
        return response

    def upload_file(self, path, progress=False):
        """Upload a file"""
        key = self.get_obj_key(path)
        progress_callback = ProgressPercentage(path) if progress else lambda x: None
        extra_args = self._get_extra_args()

        with ignore_ctrl_c():
            with self._transfer(self.client) as transfer:
                response = transfer.upload_file(
                    path, self._bucket, key, extra_args=extra_args, callback=progress_callback)
        return response

    def search(self, term):
        bucket = self.resource.Bucket(self._bucket)
        for obj in fuzzyfinder(term, (obj.key for obj in bucket.objects.all())):
            yield obj

    def rename_object(self, old_prefix, new_prefix):
        """Rename object"""
        LOG.warning('ignoring all prefixes')
        copy_source = {
            'Bucket': self._bucket,
            'Key': old_prefix
        }
        extra = self._get_extra_args()
        extra.update(dict(
            CopySourceSSECustomerAlgorithm=self.config.ENCRYPTION_ALGORITHM,
            CopySourceSSECustomerKey=self.config.ENCRYPTION_KEY))

        self.client.copy(
            copy_source, self._bucket, new_prefix, ExtraArgs=extra
        )

    def get_object_size(self, path):
        """Get object size"""
        response = self.client.head_object(Bucket=self._bucket, Key=self.get_obj_key(path), **self._get_extra_args())
        return response['ContentLength']

    def check_if_key_exists(self, key):
        """See if file/key exists"""
        key = self.get_obj_key(key)
        resp = self.client.list_objects_v2(Bucket=self._bucket, Prefix=key)
        return 'Contents' in resp

    def download_file(self, path, progress=False, use_encryption=None):
        """Download a file"""
        touch(path)
        key = self.get_obj_key(path)
        progress_callback = ProgressPercentage(path, size=self.get_object_size(path)) if progress else lambda x: None
        extra_args = {} if use_encryption is False else self._get_extra_args()

        with ignore_ctrl_c():
            with self._transfer(self.client) as transfer:
                response = transfer.download_file(
                    self._bucket, key, path, extra_args=extra_args, callback=progress_callback)
        return response

    def list_files(self):
        """List files"""
        resp = self.client.list_objects_v2(Bucket=self._bucket, Prefix=self._prefix)
        if 'Contents' in resp:
            for el in resp['Contents']:
                yield {
                    'date': el['LastModified'], 'size': el['Size'], 'name': el['Key']
                }

    def delete_file(self, path):
        """Delete file object"""
        key = self.get_obj_key(path)
        with ignore_ctrl_c():
            return self.client.delete_object(Bucket=self._bucket, Key=key)
