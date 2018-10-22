An efficient transfer to the cloud
----------------------------------
[![Build Status](https://travis-ci.org/Multiplicom/wanna-transfer.svg?branch=master)](https://travis-ci.org/Multiplicom/wanna-transfer)
[![PyPI version](https://badge.fury.io/py/wanna-transfer.svg)](https://badge.fury.io/py/wanna-transfer)
[![Maintainability](https://api.codeclimate.com/v1/badges/04b6db49155397d49c5d/maintainability)](https://codeclimate.com/github/piotrpawlaczek/wanna-transfer/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/04b6db49155397d49c5d/test_coverage)](https://codeclimate.com/github/piotrpawlaczek/wanna-transfer/test_coverage)

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

> ⚠️ wanna-transfer will use the profile **aws** if no profile is selected either from the CLI or in the API.

Example:

```ini
[default]
encryption_key = your_encryption_key
partner = partner-name
bucket = your-space
upload_prefix = in

# this is the default profile
[aws]
aws_access_key_id = your_key_id
aws_secret_access_key = your_secret_key

[dev]
aws_access_key_id = your_key_dev_id
aws_secret_access_key = your_dev_secret_key
```

Usage
-----
from the command line:
```
>> wanna -h
Wanna transfer.

Usage:
  wanna upload PATH [--no-encrypt] [--no-progress] [--ignore-prefix]
                    [--checksum] [--datacenter=<aws>] [--bucket=<credentials>] [-v | -vv] [-H | --human]
                    [--profile=<name>]
  wanna download PATH [DST] [--no-decrypt] [--no-progress] [--checksum]
                            [--datacenter=<aws>]  [--bucket=<credentials>] [--ignore-prefix] [-v | -vv] [-H | --human]
                            [--profile=<name>]
  wanna delete PATH [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv]
                    [--profile=<name>]
  wanna search TERM [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv]
                    [--profile=<name>]
  wanna rename OLD NEW [--ignore-prefix] [--datacenter=<aws>] [--no-encrypt]  [--bucket=<credentials>] [-v | -vv]
                       [--profile=<name>]
  wanna status PATH [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv] [--profile=<name>]
  wanna generate_secret [-v | -vv]
  wanna ls [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv] [-H | --human] [--profile=<name>]
  wanna (-h | --help)
  wanna --version
```
or from python:

```python
from wanna import Transfer

Transfer(vendor='aws').upload_files(path)
```
