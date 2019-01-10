from wanna.vendors.aws import _AWS
from botocore.client import Config as BotoConfig
from wanna.settings import Config
from os import environ

class MINIO(_AWS):
    def __init__(self, *args, **kwargs):
        super(MINIO, self).__init__(*args, **kwargs)

    @property
    def service(self):
        return "s3"

    @property
    def name(self):
        return "minio"

    def _get_boto_config(self):
        config = {
            "aws_access_key_id": self.program_config.VENDOR.API_KEY,
            "aws_secret_access_key": self.program_config.VENDOR.API_SECRET,
            "endpoint_url": self.program_config.VENDOR.ENDPOINT_URL,
            "config": BotoConfig(
                signature_version=self.signature_version, region_name=self.region_name
            ),
        }
        if self.program_config.VENDOR.ROOT_CA_BUNDLE:
            config.update({ 'verify': self.program_config.VENDOR.ROOT_CA_BUNDLE })
        
        return config
        