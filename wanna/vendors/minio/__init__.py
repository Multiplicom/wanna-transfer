from wanna.vendors.aws import _AWS
from botocore.client import Config as BotoConfig


class MINIO(_AWS):
    def __init__(self, **kwargs):
        super(MINIO, self).__init__(**kwargs)

    @property
    def name(self):
        return "minio"

    def _get_config(self, config):
        return {
            "aws_access_key_id": config.VENDOR.API_KEY,
            "aws_secret_access_key": config.VENDOR.API_SECRET,
            "endpoint_url": config.VENDOR.ENDPOINT_URL,
            "config": BotoConfig(
                signature_version=self.signature_version, region_name=self.region_name
            ),
        }