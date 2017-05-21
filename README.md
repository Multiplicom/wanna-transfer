An efficient transfer to the cloud
----------------------------------

The main goal of this tool is to provide efficient and reliable upload/download
for large ( >5GB) files to and from the cloud.

Wanna handles several things for the user:

  * Uploading/downloading a file in parallel
  * Retries, when possible
  * Encryption in transit and at rest
  * Control checksum to verify data integrity

has a reasonable set of defaults:

  * Multipart threshold size (small/large file switch)
  * Max parallel downloads
  * Socket timeouts

and includes handy command line tool: `wanna` with simple progress bar.

Wanna tries to follow multi-cloud strategy.
Currently only `aws s3` is supported but pull requests with adding more data centers are welcome.
Nice to have: Azure, Google Cloud, IBM Softlayer

Installation
------------
```cmd
>> python setup.py install
```
Create a configuration file under ~/.wanna/credentials

Example:

```ini
[default]
encryption_key = your_encryption_key
partner = partner-name
bucket = your-space
upload_prefix = in

[aws]
aws_access_key_id = your_key_id
aws_secret_access_key = your_secret_key
```

Usage
-----
from command line:
```cmd
>> wanna upload big_file.tar.gz --encrypt --progress --checksum
>> wanna download big_file.tar.gz --decrypt --progress
>> wanna delete big_file.tar.gz
>> wanna ls
```
or from python:

```python
from wanna import Transfer

Transfer.upload_file(...)
```
