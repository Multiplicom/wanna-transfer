An efficient transfer to the cloud
----------------------------------
[![Build Status](https://travis-ci.org/piotrpawlaczek/wanna-transfer.svg?branch=master)](https://travis-ci.org/piotrpawlaczek/wanna-transfer)

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
from the command line:
```
>> wanna -h   
                                                                                                                            
Wanna transfer.

Usage:
  wanna upload [--no-encrypt] [--no-progress] [-v | -vv]
               [--checksum] [--datacenter=<aws>] [--ignore--prefix] PATH
  wanna download [--no-decrypt] [--no-progress] [-v | -vv]
                 [--checksum] [--datacenter=<aws>] PATH
  wanna delete [--datacenter=<aws>] [--ignore-prefix] [-v | -vv] PATH
  wanna search [--datacenter=<aws>] [--ignore-prefix] [-v | -vv] TERM
  wanna rename [--datacenter=<aws>] [--ignore-prefix] [-v | -vv] OLD NEW
  wanna ls [--datacenter=<aws>] [--ignore-prefix] [-v | -vv]
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
from wanna import upload_file

upload_file(vendor='aws', path)
```
