from wanna.vendors.aws import _AWS


__version__ = '0.1.4'

ALIASES = {
    's3': _AWS,
    'aws': _AWS,
    'softlayer': NotImplementedError,
    'azure': NotImplementedError,
    'googlecloud': NotImplementedError
}


def setup_vendor(vendor_str, use_encryption=True, ignore_prefix=False):
    """Setup vendor from the given string and params"""
    vendor = vendor_str.lower()
    try:
        vendor = ALIASES[vendor]
    except KeyError:
        raise ValueError('datacenter: {}, is not supported'.format(vendor))
    return vendor(use_encryption=use_encryption, ignore_prefix=ignore_prefix)


def Transfer(vendor='aws', use_encrpytion=True, ignore_prefix=True):
    """A proxy to vendor"""
    return setup_vendor(vendor, use_encrpytion, ignore_prefix)
