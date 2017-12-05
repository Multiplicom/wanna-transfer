An efficient transfer to the cloud
----------------------------------
[![Build Status](https://travis-ci.org/Multiplicom/wanna-transfer.svg?branch=master)](https://travis-ci.org/Multiplicom/wanna-transfer)
[![PyPI version](https://badge.fury.io/py/wanna-transfer.svg)](https://badge.fury.io/py/wanna-transfer)

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
>> pip install wanna-transfer
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
from the command line:
```
>> wanna -h
Wanna transfer.

Usage:
  wanna upload PATH [--no-encrypt] [--no-progress] [--ignore--prefix]
                    [--checksum] [--datacenter=<aws>] [-v | -vv]
  wanna download PATH [--no-decrypt] [--no-progress] [--checksum]
                      [--datacenter=<aws>] [-v | -vv]
  wanna delete PATH [--ignore-prefix] [--datacenter=<aws>] [-v | -vv]
  wanna search TERM [--ignore-prefix] [--datacenter=<aws>] [-v | -vv]
  wanna rename OLD NEW [--ignore-prefix] [--datacenter=<aws>] [-v | -vv]
  wanna ls [--ignore-prefix] [--datacenter=<aws>] [-v | -vv]
  wanna (-h | --help)
  wanna --version

Options:
  -h --help      Show this message and exit.
  -v --verbose   Show more text.
  --version      Show version and exit.
  --no-progress  Do not show progress bar.
  --no-encrypt   Do not encrypt at rest.
  --no-decrypt   Do not decrypt in transit.
  --ignore-prefix  Ignore all prefixes
  --datacenter=<name>  Cloud provider [default: aws]
```
or from python:

```python
from wanna import Transfer

Transfer(vendor='aws').upload_files(path)
```
