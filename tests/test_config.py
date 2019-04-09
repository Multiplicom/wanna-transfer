from wanna.settings import Config
from unittest import TestCase
from pytest import fixture, raises
import six

SAMPLE_CONFIG = """
[default]
encryption_key = 656767 
partner = spam
bucket = sausage
upload_prefix = bacon

[aws]
aws_access_key_id = egg bacon sausage and spam
aws_secret_access_key = spam bacon sausage and spam

[minio]
endpoint_url = default-minio-url
minio_access_key = default-minio-key
minio_secret_key = default-minio-secret
bucket = lobster thermidor

[minio:dev]
endpoint_url = dev-minio-url
minio_access_key = dev-minio-key
minio_secret_key = dev-minio-secret
bucket = lobster thermidor aux crevettes
"""

@fixture
def config_file(tmpdir, scope='function'):
    def with_content(contents, profile=None, vendor=None):
        tmpdir.chdir()
        tmpdir.join("config").write(contents)
        return Config(path="./config", profile=profile, vendor=vendor)

    return with_content

def test_empty_config_file(config_file):
    with raises(ValueError):
        config = config_file("") 

def test_defaults_are_set(config_file):
    config = config_file(SAMPLE_CONFIG)

    assert config.ENCRYPTION_KEY == six.b("egg")
    assert config.PARTNER_NAME == "spam"
    assert config.BUCKET == "sausage"
    assert config.UPLOAD_PREFIX == "bacon"

def test_default_vendor_setings_are_set(config_file):
    config = config_file(SAMPLE_CONFIG)

    assert config.VENDOR.API_KEY == "egg bacon sausage and spam"
    assert config.VENDOR.API_SECRET == "spam bacon sausage and spam"


def test_vendor_setings_are_set(config_file):
    config = config_file(SAMPLE_CONFIG, vendor="minio")

    assert config.VENDOR.API_KEY == "default-minio-key"
    assert config.VENDOR.API_SECRET == "default-minio-secret"

def test_defaults_are_overwritten_by_vendor(config_file):
    config = config_file(SAMPLE_CONFIG, vendor='minio', profile="dev")
    assert config.BUCKET == 'lobster thermidor aux crevettes'

def test_default_provider_aws_precedence(config_file):
    config = config_file("""
    [default]
    bucket = egg

    [aws]
    bucket = spam
    aws_access_key_id = aaki
    aws_secret_access_key = asak
    """)
    assert config.BUCKET == "spam"

def test_provider_precedence(config_file):
    config = config_file("""
    [default]
    bucket = egg

    [aws]
    bucket = spam
    aws_access_key_id = aaki
    aws_secret_access_key = asak
    """, vendor='aws')
    assert config.BUCKET == "spam"

def test_default_provider_aws_without_vendor_override(config_file):
    config = config_file("""
    [default]
    bucket = egg

    [aws]
    aws_access_key_id = aaki
    aws_secret_access_key = asak

    [minio]
    bucket = bacon
    """)
    assert config.BUCKET == "egg"

def test_default_provider_aws_without_vendor_override(config_file):
    config = config_file("""
    [default]
    bucket = egg

    [minio]
    endpoint_url = spam
    bucket = bacon
    minio_access_key = mak
    minio_secret_key = msk
    """, vendor='minio')
    assert config.BUCKET == "bacon"

def test_default_provider_with_named_profile(config_file):
    config =config_file("""
    [default]
    bucket = egg

    [aws:dev]
    aws_access_key_id = aaki
    aws_secret_access_key = asak
    bucket = spam
    """, profile="dev")
    assert config.BUCKET == "spam"

def test_unsupported_vendor_configuration(config_file):
    with raises(ValueError):
        config_file("""
        [spam]
        """)

def test_non_default_vendor_with_named_profile(config_file):
    config = config_file("""
    [default]
    bucket = egg

    [minio]
    endpoint_url = spam
    bucket = bacon
    minio_access_key = mak
    minio_secret_key = msk

    [minio:foo]
    bucket = foo-bacon
    endpoint_url = foo-spam
    minio_access_key = foo-mak
    minio_secret_key = foo-msk
    """, vendor='minio', profile="foo")
    assert config.BUCKET == "foo-bacon"

def test_vendor_override_for_default_provider(config_file):
    config = config_file("""
    [default]
    provider = minio
    bucket = foo

    [aws]
    bucket = bar

    [minio]
    provider = "aws
    endpoint_url = foo-spam
    minio_access_key = foo-mak
    minio_secret_key = foo-msk
    """)
    assert config.PROVIDER == "minio"
    assert config.BUCKET == "foo"

