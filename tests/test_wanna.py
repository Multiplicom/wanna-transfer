from wanna import Transfer
from pytest import fixture
from wanna.vendors.aws import _AWS

from tests.test_config import config_file

def test_aws(config_file):
    config = config_file("""
    [aws]
    aws_access_key_id = foo
    aws_secret_access_key = bar
    """)
    vendor = _AWS(config=config)
    assert vendor.name == "aws"


def test_transfer(config_file):
    config = config_file("""
    [aws]
    aws_access_key_id = foo
    aws_secret_access_key = bar
    """)
    trf = Transfer(config=config)
    assert hasattr(trf, "download_file")

