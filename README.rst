A efficient transfer to the cloud
---------------------------------

Wanna upload?
Wanna download?

The main goal of this tool is to provide efficient and reliable upload/download
for large (>5GB) files to and from the cloud.

Wanna provides high level abstractions to achieve it
It handles several things for the user:

* Handy command line tool: wanna
* Uploading/downloading a file in parallel
* Simple progress bar
* Retries, when possible
* Server side encryption in transfer and on rest
* Control checksum to verify data integrity

and tries to follow multi-cloud strategy.
Currently only `aws s3` is supported.
Pull requests with adding more data centers are welcome!

Installation
------------

>> python setup.py install

Create a configuration file under ~/.wanna/credentials
Example:

```config
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

>> wanna upload big_file.tar.gz --encrypt --progress --checksum
>> wanna download big_file.tar.gz --decrypt --progress
>> wanna delete big_file.tar.gz
>> wanna ls

or

```python
from wanna import Transfer

Transfer.upload_file(...)
```
