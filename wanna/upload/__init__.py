"""This module provides high level abstractions for efficient
uploads to the cloud. It handles several things for the user:

* Automatically switching to multipart transfers when
  a file is over a specific size threshold
* Uploading a file in parallel
* Progress callbacks to monitor transfers
* Retries. When possible.
"""


def upload_files(
        path, vendor, bucket=None,
        use_encryption=True, add_checksum=False, progress=False, prefix=None, ignore_prefix=False, humanized=False):
    """Uploads file to the cloud.

    Args:
        path (str): path to the file or folder
        vendor (str): datacenter name: 'aws|softlayer|azure|googlecloud'
        use_encryption (bool): should the file be server side encrypted
        add_checksum (bool): should the md5 checksum be uploaded next to the original file
        progress (bool): should the transfer be monitored

    Returns:
        tuple - confirmation(s) from the vendor
    """
    from wanna import setup_vendor
    vendor = setup_vendor(vendor, bucket=bucket, use_encryption=use_encryption, ignore_prefix=ignore_prefix, humanized=humanized)
    vendor.upload_files(path, add_checksum=add_checksum, progress=progress)
