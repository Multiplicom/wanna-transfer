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

import glob
import boto3
import os.path
import logging

LOG = logging.getLogger('wanna:aws')


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
            'config': BotoConfig(signature_version=self.signature_version, region_name=self.region_name)
        }

    def __init__(self, bucket=None, use_encryption=True, ignore_prefix=False, humanized=False):
        config = Config(self)
        self._bucket = config.BUCKET if not bucket else bucket
        self._prefix = os.path.join(config.UPLOAD_PREFIX, config.PARTNER_NAME)
        self._encrypt = use_encryption
        self.client = boto3.client(self.service, **self._get_config(config))
        self.resource = boto3.resource('s3', **self._get_config(config))
        self._transfer = S3Transfer
        self._checksum = None
        self.ignore_prefix = ignore_prefix or config.IGNORE_PREFIX
        self.config = config
        self._humanized = humanized

        if ignore_prefix:
            self._ignore_prefix()

    def get_encryption_key(self, key=None):
        if key:
            try:
                return bytes(bytearray.fromhex(key))
            except ValueError as error:
                LOG.warning('{}, enc key: {}'.fomat(error, key))
                return key
        return self.config.ENCRYPTION_KEY

    def _ignore_prefix(self):
        LOG.debug('ignore prefix mode')
        self._prefix = ''

    def _get_extra_args(self, encryption_key=None):
        """Extra parameters"""
        args = {}
        if self._encrypt:
            LOG.info('using encryption: {}'.format(self.config.ENCRYPTION_ALGORITHM))
            args.update({
                'SSECustomerAlgorithm': self.config.ENCRYPTION_ALGORITHM,
                'SSECustomerKey': self.get_encryption_key(encryption_key),
            })
        return args

    def get_obj_key(self, path, md5=False, ignore_prefix=False):
        """Get file object key"""
        if ignore_prefix is True or self.ignore_prefix:
            key = path
        else:
            key = os.path.join(self._prefix, os.path.basename(path))
        if md5 is True:
            key = key + self.hash_checksum
        return key

    @staticmethod
    def get_checksum(path):
        """Calculate control sum"""
        return md5sum(path)

    def upload_checksum(self, path):
        """Upload control sum for the given file"""
        LOG.debug('uploading checksum for: %s', path)
        key = self.get_obj_key(path, md5=True) if not self.ignore_prefix else path
        checksum = self.get_checksum(path)
        response = self.client.put_object(Bucket=self._bucket, Key=key, Body=checksum)
        LOG.info('checksum ({}): {}'.format(self.hash_checksum, checksum))
        return response

    def upload_files(self, path, add_checksum=False, progress=False):
        """Upload files"""

        def get_files():
            if os.path.isdir(path):
                return glob.glob(os.path.join(path, '*'))
            return [path]

        for item in get_files():
            itemname = os.path.basename(item)
            key = self.get_obj_key(itemname)
            progress_callback = ProgressPercentage(item, humanized=self._humanized) if progress else lambda x: None
            extra_args = self._get_extra_args()

            with ignore_ctrl_c():
                with self._transfer(self.client) as transfer:
                    LOG.debug('uploading %s', item)
                    transfer.upload_file(item, self._bucket, key, extra_args=extra_args, callback=progress_callback)
            print('')
            if add_checksum:
                self.upload_checksum(item)

    def search(self, term):
        """Fuzzy search for the object(s) using given term"""
        bucket = self.resource.Bucket(self._bucket)
        for obj in fuzzyfinder(term, (obj.key for obj in bucket.objects.all())):
            yield obj

    def rename_object(self, old_prefix, new_prefix, encryption_key=None):
        """Rename object"""
        if old_prefix == new_prefix:
            LOG.info(':renaming skipped, old and new name are the same')
            return

        LOG.warning(':ignoring all prefixes')
        copy_source = {'Bucket': self._bucket, 'Key': old_prefix}
        extra = self._get_extra_args(encryption_key)
        if self._encrypt:
            extra.update(
                dict(
                    CopySourceSSECustomerAlgorithm=self.config.ENCRYPTION_ALGORITHM,
                    CopySourceSSECustomerKey=self.get_encryption_key(encryption_key)
                )
            )

        with ignore_ctrl_c():
            LOG.info(':renaming')
            self.client.copy(copy_source, self._bucket, new_prefix, ExtraArgs=extra)
            self.delete_file(old_prefix, ignore_prefix=True)

    def get_object_size(self, path, encryption_key=None):
        """Get object size"""
        response = self.client.head_object(
            Bucket=self._bucket,
            Key=self.get_obj_key(path),
            **self._get_extra_args(encryption_key)
        )
        return response['ContentLength']

    def check_if_key_exists(self, key):
        """See if file/key exists"""
        LOG.info('checking {}'.format(key))
        key = self.get_obj_key(key)
        resp = self.client.list_objects_v2(Bucket=self._bucket, Prefix=key)
        return 'Contents' in resp

    def download_file(self, path, dst='.', progress=False, use_encryption=None, encryption_key=None):
        """Download a file"""
        dst = dst or '.'
        if os.path.isdir(dst):
            local = os.path.join(dst, os.path.basename(path))
        else:
            local = dst
        touch(local)
        key = self.get_obj_key(path)
        progress_callback = ProgressPercentage(
            local, size=self.get_object_size(key, encryption_key=encryption_key), humanized=self._humanized
        ) if progress else lambda x: None
        extra_args = {} if use_encryption is False else self._get_extra_args(encryption_key=encryption_key)

        if self.check_if_key_exists(key):
            with ignore_ctrl_c():
                with self._transfer(self.client) as transfer:
                    response = transfer.download_file(
                        self._bucket, key, local, extra_args=extra_args, callback=progress_callback
                    )
            print('')
        else:
            raise KeyError('{} does not exist!'.format(path))
        return response

    def list_files(self):
        """List files"""
        resp = self.client.list_objects_v2(Bucket=self._bucket, Prefix=self._prefix)
        if 'Contents' in resp:
            for el in resp['Contents']:
                yield {'date': el['LastModified'], 'size': el['Size'], 'name': el['Key']}

    def delete_file(self, path, ignore_prefix=False):
        """Delete file object"""
        path = path if ignore_prefix is True else self.get_obj_key(path)
        if self.check_if_key_exists(path):
            with ignore_ctrl_c():
                return self.client.delete_object(Bucket=self._bucket, Key=path)
        raise KeyError('{} does not exist!'.format(path))

    def get_status(self, path, ingore_prefix=False):
        """Get status from tag data"""
        return self.client.get_object_tagging(Bucket=self._bucket, Key=path)
