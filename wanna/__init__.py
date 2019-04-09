from wanna.vendors.aws import _AWS

__version__ = '0.2.2'

ALIASES = {
    "s3": _AWS,
    "aws": _AWS,
    "softlayer": NotImplementedError,
    "azure": NotImplementedError,
    "googlecloud": NotImplementedError,
}


def setup_vendor(
    vendor_str,
    bucket=None,
    use_encryption=True,
    ignore_prefix=False,
    profile=None,
    **other
):
    """Setup vendor from the given string and params"""
    vendor = vendor_str.lower()
    try:
        vendor = ALIASES[vendor]
    except KeyError:
        raise ValueError("datacenter: {}, is not supported".format(vendor))
    return vendor(
        bucket=bucket,
        use_encryption=use_encryption,
        ignore_prefix=ignore_prefix,
        profile=profile,
        **other
    )


def Transfer(
    vendor="aws", bucket=None, use_encrpytion=True, ignore_prefix=False, profile=None, config=None
):
    """A proxy to vendor"""
    return setup_vendor(
        vendor,
        bucket=bucket,
        use_encryption=use_encrpytion,
        ignore_prefix=ignore_prefix,
        profile=profile,
        config=config
    )
