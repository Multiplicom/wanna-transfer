from wanna import Transfer
from wanna.vendors.aws import _AWS


def test_aws():
    vendor = _AWS()
    assert vendor.name == 'aws'


def test_transfer():
    t = Transfer()
    assert hasattr(t, 'download_file')
