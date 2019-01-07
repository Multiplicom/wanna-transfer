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

Configuration
-------------

Create a configuration file under `~/.wanna/credentials`.

Unless specified otherwise, wanna will use the **S3** provider using the access credentials in the nameless profile for that provider—i.e. under `[aws]`. The default provider can be toggled by setting the provider under `[default]` to any of the supported providers.

Wanna supports using _any_ of the multiple named profiles that are stored in the credentials file. You can configure additional profiles by adding sections to the credentials file like shown in the example below.

Settings can be shared between profiles using the `[default]` section. These values can be overwritten in the profile settings (either named or nameless).


```ini
[default]
encryption_key = default-encryption_key
partner = partner-name
bucket = your-space
upload_prefix = in

# Default access credentials for the default provider. 
[aws]
aws_access_key_id = your_key_id
aws_secret_access_key = your_secret_key

# Named profile 'dev' for S3.
# Use with --profile=dev 
[aws:dev] 
aws_access_key_id = your-dev-key-id
aws_secret_access_key = your-dev-secret-key
# These settings override the defaults:
bucket = your-dev-space 
encryption_key = dev-encryption-key
```
_Example credentials file_

Supported Providers
---
| | Settings |
|----|-----|
| **aws** | `aws_access_key_id` (mandatory)<br>`aws_secret_access_key` (mandatory) | 
| **minio** | `minio_access_key` (mandatory)<br>`minio_secret_key` (mandatory)<br>`root_ca_bundle` (optional)<br>`endpoint_url` (mandatory)



Usage
-----
from the command line:
```
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

Options:
  -h --help      Show this message and exit.
  -v --verbose   Show more text.
  --version      Show version and exit.
  --no-progress  Do not show progress bar.
  --no-encrypt   Do not encrypt at rest.
  --no-decrypt   Do not decrypt in transit.
  --ignore-prefix  Ignore all prefixes
  --profile=<name>  Use a named profile
  --datacenter=<name>  Cloud provider [default: aws]
  --bucket=<name>  Bucket name [default: credentials]
```

Or from Python:

```python
from wanna import Transfer

Transfer().upload_files(path)
```
