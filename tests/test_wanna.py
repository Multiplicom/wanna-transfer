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


def test_default_profile():
    with patch.object(
        configparser.ConfigParser, "get", return_value="0000"
    ) as cfg_get_mocked:
        trf = Transfer()

        cfg_get_mocked.assert_any_call("aws", "aws_access_key_id", fallback="missing")
        cfg_get_mocked.assert_any_call(
            "aws", "aws_secret_access_key", fallback="missing"
        )


def test_named_profile():
    with patch.object(
        configparser.ConfigParser, "get", return_value="0000"
    ) as cfg_get_mocked:
        trf = Transfer(profile="partner")

        cfg_get_mocked.assert_any_call(
            "partner", "aws_access_key_id", fallback="missing"
        )
        cfg_get_mocked.assert_any_call(
            "partner", "aws_secret_access_key", fallback="missing"
        )
