from wanna import Transfer
from wanna.vendors.aws import _AWS
from wanna.settings import Config

from pytest import fixture


def test_aws():
    vendor = _AWS()
    assert vendor.name == "aws"


def test_transfer():
    trf = Transfer()
    assert hasattr(trf, "download_file")

@fixture
def config_file(tmpdir, scope='function'):
    def with_content(contents, profile=None, vendor=None):
        tmpdir.chdir()
        tmpdir.join("config").write(contents)
        return Config(path="./config", profile=profile, vendor=vendor)

    return with_content

def test_fallback_settings_absent_configuration(config_file):
    config = config_file("""""")

    assert config.ENCRYPTION_KEY == bytearray.fromhex('0000')
    assert config.PARTNER_NAME == 'partner' 
    assert config.BUCKET == 'mtp-cloudstorage'
    assert config.UPLOAD_PREFIX == 'in'
    assert config.IGNORE_PREFIX == False
    assert config.ENCRYPTION_ALGORITHM == 'AES256'

def test_default_provider_nameless_profile_fallback_settings(config_file):
    config = config_file("""
    [aws]
    """)

    assert config.PROVIDER == 'aws'
    assert config.VENDOR.API_KEY == 'missing'
    assert config.VENDOR.API_SECRET == 'missing'

def test_named_profile(config_file):
    config = config_file("""
    [aws]
    aws_access_key_id = egg
    aws_secret_access_key = spam 
    
    [aws:partner]
    """, profile='partner')

    assert config.PROVIDER == 'aws'
    assert config.VENDOR.API_KEY == 'missing'
    assert config.VENDOR.API_SECRET == 'missing'

