from wanna.settings import Config

from wanna.vendors.aws import _AWS
from wanna.vendors.minio import MINIO

__version__ = '0.2.0-alpha1'

ALIASES = {
    "s3": _AWS,
    "aws": _AWS,
    "minio": MINIO,
    "softlayer": NotImplementedError,
    "azure": NotImplementedError,
    "googlecloud": NotImplementedError,
}

config = Config()

def setup_vendor(
    vendor_str,
    bucket=None,
    use_encryption=True,
    ignore_prefix=False,
    profile=None,
    **other
):
    """Setup vendor from the given string and params"""
    vendor = vendor_str.lower() if vendor_str else config.PROVIDER 
    try:
        vendor = ALIASES[vendor]
    except KeyError:
        raise ValueError("datacenter: {}, is not supported".format(vendor_str.lower()))
    return vendor(
        bucket=bucket,
        use_encryption=use_encryption,
        ignore_prefix=ignore_prefix,
        profile=profile,
        **other
    )


def Transfer(
    vendor="aws", bucket=None, use_encrpytion=True, ignore_prefix=False, profile=None
):
    """A proxy to vendor"""
    return setup_vendor(
        vendor.lower() if vendor else config.PROVIDER,
        bucket=bucket,
        use_encryption=use_encrpytion,
        ignore_prefix=ignore_prefix,
        profile=profile,
    )
