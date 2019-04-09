"""Configuration module

Settings and defaults
"""
import os
import configparser

from functools import partial

DEFAULT_SECTION = 'default'

class Config(object):
    """Shared settings"""

    ENCRYPTION_ALGORITHM = "AES256"

    def __init__(self, profile=None, vendor=None, path="~/.wanna/credentials"):
        config = configparser.ConfigParser()
        config.default_section = DEFAULT_SECTION
        config.read([os.path.expanduser(path)])
        self.validate(config)

        self.PROVIDER = (vendor if vendor else config.get("default", "provider", fallback="aws")).lower()
        
        section = "{}:{}".format(self.PROVIDER, profile) if profile else self.PROVIDER
        get = partial(config.get, section)
        get_boolean = partial(config.getboolean, section)
        
        self.ENCRYPTION_KEY = bytes(bytearray.fromhex(get("encryption_key", fallback="0000")))
        self.PARTNER_NAME = get("partner", fallback="")
        self.BUCKET = get("bucket", fallback="mtp-cloudstorage")
        self.UPLOAD_PREFIX = get("upload_prefix", fallback="in")
        self.IGNORE_PREFIX = get_boolean("ignore_prefix", fallback=False)
        self.VENDOR = DATACENTERS[self.PROVIDER](get)

    def validate(self, config):
        if len(config.sections()) < 1:
            raise ValueError("Invalid configuration file: Missing vendor settings.")

        vendors_with_settings = set(vendor.split(":")[0] for vendor in config.sections())
        
        for vendor in vendors_with_settings:
            if vendor not in DATACENTERS.keys():
                raise ValueError("Invalid configuration file: Unsupported vendor '{}'".format(vendor))

class AWS(object):
    """Aws specific settings"""

    def __init__(self, get):
        self.API_KEY = get("aws_access_key_id")
        self.API_SECRET = get("aws_secret_access_key")


class MINIO(object):
    """Minio
    
    endpoint_url -- the endpoint on which Minio is hosted
    root_ca_bundle -- a pem file bundle with root CA cert and self-signed cert (optional)
    minio_access_key -- access key (comparable with aws_access_key_id)
    minio_secret_key -- secret key (comparable with aws_secret_access_id)
    """
    def __init__(self, get):
        # ignore profile for now
        self.ENDPOINT_URL = get("endpoint_url")
        self.ROOT_CA_BUNDLE = get("root_ca_bundle", fallback=None)
        self.API_KEY = get("minio_access_key")
        self.API_SECRET = get("minio_secret_key")

DATACENTERS = {
    "aws": AWS,
    "minio": MINIO,
    # "softlayer": NotImplementedError,
    # "azure": NotImplementedError,
    # "googlecloud": NotImplementedError,
}
