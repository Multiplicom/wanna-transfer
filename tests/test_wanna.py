from wanna import Transfer
from wanna.vendors.aws import _AWS
from mock import patch
import configparser


def test_aws():
    vendor = _AWS()
    assert vendor.name == "aws"


def test_transfer():
    trf = Transfer()
    assert hasattr(trf, "download_file")

