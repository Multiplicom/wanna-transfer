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
from wanna.utils import finder

from wanna.settings import Config

from boto3.s3.transfer import S3Transfer
from botocore.client import Config as BotoConfig

import glob
import boto3
import os.path
import logging

LOG = logging.getLogger("wanna:aws")

class ServerSideEncryption:
    # More information: https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingEncryption.html

    CUSTOMER_PROVIDED_KEY = 'SSEC'
    S3_MANAGED_KEY = 'SSES3'
    KMS_MANAGED_KEY = 'SSEKMS'

    TYPES = [CUSTOMER_PROVIDED_KEY, S3_MANAGED_KEY, KMS_MANAGED_KEY]


class _AWS(object):
    """AWS s3 service"""

    hash_checksum = ".md5"
    signature_version = "s3v4"
    region_name = "eu-central-1"

    @property
    def service(self):
        return "s3"

    @property
    def name(self):
        return "aws"

    def _get_config(self, config):
        return {
            "aws_access_key_id": config.VENDOR.API_KEY,
            "aws_secret_access_key": config.VENDOR.API_SECRET,
            "config": BotoConfig(
                signature_version=self.signature_version, region_name=self.region_name
            ),
        }

    def __init__(
        self,
        bucket=None,
        use_encryption=True,
        ignore_prefix=False,
        humanized=False,
        profile=None,
        config=None
    ):
        LOG.info("Profile '{}'".format(profile) if profile else "No profile selected")
        config = config if config else Config(profile=profile)
        self._bucket = config.BUCKET if not bucket else bucket
        self._default_prefix = os.path.join(config.UPLOAD_PREFIX, config.PARTNER_NAME)
        self._encrypt = use_encryption
        self._encryption_type = ServerSideEncryption.CUSTOMER_PROVIDED_KEY
        self.client = boto3.client(self.service, **self._get_config(config))
        self.resource = boto3.resource("s3", **self._get_config(config))
        self._transfer = S3Transfer
        self._checksum = None
        self.ignore_prefix = ignore_prefix or config.IGNORE_PREFIX
        self.config = config
        self._humanized = humanized

        if self.ignore_prefix:
            self._ignore_prefix()

    def get_encryption_key(self, key=None):
        if key:
            try:
                return bytes(bytearray.fromhex(key))
            except ValueError as error:
                LOG.warning("{}, enc key: {}".format(error, key))
                return key
        return self.config.ENCRYPTION_KEY

    def _ignore_prefix(self):
        LOG.debug("ignore prefix mode")
        self._prefix = ""

    def _get_extra_args(self, encryption_key=None):
        """Extra parameters"""
        args = {}
        if self._encrypt and self._encryption_type != ServerSideEncryption.S3_MANAGED_KEY:
            LOG.info("using encryption: {}".format(self.config.ENCRYPTION_ALGORITHM))
            args.update(
                {
                    "SSECustomerAlgorithm": self.config.ENCRYPTION_ALGORITHM,
                    "SSECustomerKey": self.get_encryption_key(encryption_key),
                }
            )
        return args

    def get_obj_key(self, path, md5=False, ignore_prefix=False, prefix=None):
        """Get file object key"""
        if ignore_prefix is True or self.ignore_prefix:
            key = path
        else:
            prefix = prefix or self._default_prefix or ""
            
            if os.path.dirname(path).startswith(prefix):
                key = path
            else:
                key = os.path.join(prefix, os.path.basename(path))

            LOG.info("Prefix={} & Path={} => Key={}".format(prefix, path, key))
        if md5 is True:
            key = key + self.hash_checksum
        return key

    @staticmethod
    def get_checksum(path):
        """Calculate control sum"""
        return md5sum(path)

    def upload_checksum(self, path, ignore_prefix=False, prefix=None):
        """Upload control sum for the given file"""
        LOG.debug('uploading checksum for: %s', path)
        key = self.get_obj_key(path, md5=True, ignore_prefix=ignore_prefix, prefix=prefix)
        checksum = self.get_checksum(path)
        response = self.client.put_object(Bucket=self._bucket, Key=key, Body=checksum)
        LOG.info("checksum ({}): {}".format(self.hash_checksum, checksum))
        return response

    def upload_files(
        self, path, add_checksum=False, progress=False, encryption_key=None, ignore_prefix=False, prefix=None
    ):
        """Upload files"""

        def get_files():
            if os.path.isdir(path):
                return glob.glob(os.path.join(path, "*"))
            return [path]

        for item in get_files():
            itemname = os.path.basename(item)
            key = self.get_obj_key(itemname, ignore_prefix=ignore_prefix, prefix=prefix)
            progress_callback = (
                ProgressPercentage(item, humanized=self._humanized)
                if progress
                else lambda x: None
            )
            extra_args = (
                {}
                if self._encrypt is False or (self._encrypt and self._encryption_type == ServerSideEncryption.S3_MANAGED_KEY)
                else self._get_extra_args(encryption_key=encryption_key)
            )

            with ignore_ctrl_c():
                with self._transfer(self.client) as transfer:
                    LOG.debug("uploading %s", item)
                    transfer.upload_file(
                        item,
                        self._bucket,
                        key,
                        extra_args=extra_args,
                        callback=progress_callback,
                    )
            print("")
            if add_checksum:
                self.upload_checksum(item, ignore_prefix=ignore_prefix, prefix=prefix)

    def search(self, term, fuzzy=False):
        """Identical or Fuzzy search for the object(s) using given term"""
        bucket = self.resource.Bucket(self._bucket)
        for obj in finder(term, (obj.key for obj in bucket.objects.all()), fuzzy=fuzzy):
            yield obj

    def rename_object(self, old_prefix, new_prefix, encryption_key=None):
        """Rename object"""
        if old_prefix == new_prefix:
            LOG.info(":renaming skipped, old and new name are the same")
            return

        LOG.warning(":ignoring all prefixes")
        copy_source = {"Bucket": self._bucket, "Key": old_prefix}
        extra = self._get_extra_args(encryption_key)
        if self._encrypt and self._encryption_type != ServerSideEncryption.S3_MANAGED_KEY:
            extra.update(
                dict(
                    CopySourceSSECustomerAlgorithm=self.config.ENCRYPTION_ALGORITHM,
                    CopySourceSSECustomerKey=self.get_encryption_key(encryption_key),
                )
            )

        with ignore_ctrl_c():
            LOG.info(":renaming")
            self.client.copy(copy_source, self._bucket, new_prefix, ExtraArgs=extra)
            self.delete_file(old_prefix, ignore_prefix=True)

    def get_object_size(self, path, encryption_key=None, ignore_prefix=False, prefix=None):
        """Get object size of SSE-S3 or CSE-encrypted object
        """
        if self._encryption_type == ServerSideEncryption.S3_MANAGED_KEY:
            response = self.client.head_object(
                Bucket=self._bucket,
                Key=self.get_obj_key(path, ignore_prefix=ignore_prefix, prefix=prefix)
            )
        else:
            response = self.client.head_object(
                Bucket=self._bucket,
                Key=self.get_obj_key(path, ignore_prefix=ignore_prefix, prefix=prefix),
                **self._get_extra_args(encryption_key)
            )
        return response["ContentLength"]

    def check_if_key_exists(self, key, ignore_prefix=False, prefix=None):
        """See if file/key exists"""
        LOG.info('checking {}'.format(key))
        key = self.get_obj_key(key, ignore_prefix=ignore_prefix, prefix=prefix)
        resp = self.client.list_objects_v2(Bucket=self._bucket, Prefix=key)
        return "Contents" in resp

    def download_file(
        self, path, dst=".", progress=False, use_encryption=None, encryption_key=None, ignore_prefix=False, prefix=None
    ):
        """Download a file"""
        dst = dst or "."
        if os.path.isdir(dst):
            local = os.path.join(dst, os.path.basename(path))
        else:
            local = dst
        touch(local)
        key = self.get_obj_key(path, ignore_prefix=ignore_prefix, prefix=prefix)
        LOG.warn("Downloading object with key **{}**".format(key))

        progress_callback = (
            ProgressPercentage(
                local,
                size=self.get_object_size(key, encryption_key=encryption_key, ignore_prefix=ignore_prefix),
                humanized=self._humanized,
            )
            if progress
            else lambda x: None
        )
        extra_args = (
            {}
            if use_encryption is False
            else self._get_extra_args(encryption_key=encryption_key)
        )

        if self.check_if_key_exists(key, ignore_prefix=ignore_prefix, prefix=prefix):
            with ignore_ctrl_c():
                with self._transfer(self.client) as transfer:
                    response = transfer.download_file(
                        self._bucket,
                        key,
                        local,
                        extra_args=extra_args,
                        callback=progress_callback,
                    )
            print("")
        else:
            raise KeyError("{} does not exist!".format(path))
        return response

    def list_files(self, prefix=None):
        """List files"""
        if self.ignore_prefix:
            resp = self.client.list_objects_v2(Bucket=self._bucket)
        else:
            resp = self.client.list_objects_v2(Bucket=self._bucket, Prefix=prefix or self._default_prefix)
        if "Contents" in resp:
            for el in resp["Contents"]:
                yield {
                    "date": el["LastModified"],
                    "size": el["Size"],
                    "name": el["Key"],
                }

    def delete_file(self, path, ignore_prefix=False, prefix=None):
        """Delete file object"""
        path = self.get_obj_key(path, ignore_prefix=ignore_prefix, prefix=prefix)
        if self.check_if_key_exists(path, ignore_prefix=ignore_prefix, prefix=prefix):
            with ignore_ctrl_c():
                return self.client.delete_object(Bucket=self._bucket, Key=path)
        raise KeyError("{} does not exist!".format(path))

    def get_status(self, path):
        """Get status from tag data"""
        return self.client.get_object_tagging(Bucket=self._bucket, Key=path)

    def encryption_type(self, encryption_type):
        """
        Set encryption type
        :param encryption_type:
        :return:
        """
        if not encryption_type in ServerSideEncryption.TYPES:
            raise NotImplementedError("Encryption type {0} not supported".format(encryption_type))
        self._encryption_type = encryption_type
