from wanna.upload import upload_file
from wanna.download import download_file
from wanna.misc import list_files
from wanna.misc import delete_file
from wanna.vendors.aws import _AWS


__version__ = '0.1.0'

ALIASES = {
    's3': _AWS,
    'aws': _AWS,
    'softlayer': NotImplementedError,
    'azure': NotImplementedError,
    'googlecloud': NotImplementedError
}


def setup_vendor(vendor_str, use_encryption=True, ignore_prefix=False):
    """return vendor obj from given string"""
    vendor = vendor_str.lower()
    try:
        vendor = ALIASES[vendor]
    except KeyError:
        raise ValueError('datacenter: {}, is not supported'.format(vendor))
    return vendor(use_encryption, ignore_prefix)


class Transfer(object):

    def __init__(self):
        pass


Transfer.upload_file = staticmethod(upload_file)
Transfer.download_file = staticmethod(download_file)
Transfer.delete_file = staticmethod(delete_file)
Transfer.list_files = staticmethod(list_files)
