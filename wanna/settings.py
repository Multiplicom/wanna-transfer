"""Configuration module

Settings and defaults
"""
import os
import configparser


class Config(object):
    """Shared settings"""

    PARTNER_NAME = "partner"
    ENCRYPTION_ALGORITHM = "AES256"
    UPLOAD_PREFIX = "in"
    BUCKET = "mtp-cloudstorage"
    IGNORE_PREFIX = False

    def __init__(self, vendor, profile=None):
        config = configparser.ConfigParser()

        config.read(os.path.expanduser("~/.wanna/credentials"))

        self.PARTNER_NAME = config.get("default", "partner", fallback=self.PARTNER_NAME)
        self.ENCRYPTION_KEY = bytes(
            bytearray.fromhex(config.get("default", "encryption_key", fallback="0000"))
        )
        self.UPLOAD_PREFIX = config.get("default", "upload_prefix", fallback="not-set")
        self.BUCKET = config.get("default", "bucket", fallback=self.BUCKET)
        print "<Config: " + repr(DATACENTERS[vendor.name.lower()]) + ">"
        self.VENDOR = DATACENTERS[vendor.name.lower()](config, profile)

        ignore_prefix = config.get("default", "ignore_prefix", fallback=False)

        self.IGNORE_PREFIX = True if ignore_prefix == "true" else False

class AWS(object):
    """Aws specific settings"""

    def __init__(self, cfg, profile=None):
        self.API_KEY = cfg.get(
            profile if profile else "aws", "aws_access_key_id", fallback="missing"
        )
        self.API_SECRET = cfg.get(
            profile if profile else "aws", "aws_secret_access_key", fallback="missing"
        )

class MINIO(object):
    def __init__(self, config, *args, **kwargs):
        self.ENDPOINT_URL = config.get("minio", "endpoint_url")
        self.API_KEY = config.get("minio", "minio_access_key")
        self.API_SECRET = config.get("minio", "minio_secret_key")



DATACENTERS = {
    "minio": MINIO,
    "aws": AWS,
    "softlayer": NotImplementedError,
    "azure": NotImplementedError,
    "googlecloud": NotImplementedError,
}
