#!/usr/bin/env python
"""Wanna transfer.

Usage:
  wanna upload PATH [--no-encrypt] [--no-progress] [--ignore-prefix]
                    [--checksum] [--datacenter=<aws>] [--bucket=<credentials>] [-v | -vv] [-H | --human]
  wanna download PATH [DST] [--no-decrypt] [--no-progress] [--checksum]
                            [--datacenter=<aws>]  [--bucket=<credentials>] [--ignore-prefix] [-v | -vv] [-H | --human]
  wanna delete PATH [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv]
  wanna search TERM [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv]
  wanna rename OLD NEW [--ignore-prefix] [--datacenter=<aws>] [--no-encrypt]  [--bucket=<credentials>] [-v | -vv]
  wanna status PATH [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv]
  wanna generate_secret [-v | -vv]
  wanna ls [--ignore-prefix] [--datacenter=<aws>]  [--bucket=<credentials>] [-v | -vv] [-H | --human]
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
  --bucket=<name>  Bucket name [default: credentials]
"""
from docopt import docopt

from wanna.upload import upload_files
from wanna.download import download_file
from wanna.misc import delete_file
from wanna.misc import list_files
from wanna.misc import get_status
from wanna.misc import rename_file
from wanna.misc import search_files
from wanna import __version__ as version

from wanna.utils import humanize

import os
import sys
import random
import logging
import binascii

LOG = logging.getLogger('wanna:cli')


def _handle(args):
    if args['PATH'] is not None:
        path = args['PATH']
        if args['upload'] or args['download']:
            add_checksum = args['--checksum']
            use_encryption = not (args['--no-encrypt'] or args['--no-decrypt'])
            progress = not (args['--no-progress'])
            if args['download']:
                dst = args['DST']
    if args['rename']:
        use_encryption = not (args['--no-encrypt'] or args['--no-decrypt'])
        old = args['OLD']
        new = args['NEW']
    if args['search']:
        term = args['TERM']
    vendor = args['--datacenter']
    ignore_prefix = args['--ignore-prefix']
    bucket = None if args['--bucket'] == 'credentials' else args['--bucket']
    humanized = any((args['-H'], args['--human']))
    args = locals()
    args.pop('args')
    LOG.debug(args)
    return args


def handle_upload(args):
    kwargs = _handle(args)
    LOG.info('Uploading {path}...to {vendor}'.format(**kwargs))
    upload_files(**kwargs)
    print('Upload finished!')


def handle_ls(args):
    kwargs = _handle(args)
    for el in list_files(**kwargs):
        reported_size = humanize(
            el['size']) if kwargs['humanized'] else el['size']
        print('{}\t {}\t\t {}'.format(
            el['date'].isoformat(), reported_size, el['name']))


def handle_rename(args):
    kwargs = _handle(args)
    rename_file(**kwargs)
    print('Done!')


def handle_search(args):
    kwargs = _handle(args)
    for el in search_files(**kwargs):
        print(el)


def handle_secret(args):
    print(binascii.b2a_hex(os.urandom(32)))


def handle_download(args):
    kwargs = _handle(args)
    LOG.info('Getting {path}...'.format(**kwargs))
    download_file(**kwargs)
    print('Download finished!')


def handle_delete(args):
    kwargs = _handle(args)
    LOG.info('Deleting {path}...'.format(**kwargs))
    delete_file(**kwargs)
    print('Done!')


def handle_status(args):
    kwargs = _handle(args)
    resp = get_status(**kwargs)
    if 'TagSet' in resp:
        for item in resp['TagSet']:
            for key, value in item.items():
                if item[key] == 'state':
                    print('import_status: {}'.format(item['Value']))
                    return
        else:
            print('import_status: init')


def handle_cry():
    from pygments.console import codes
    code = 'Hahahah, you wanna cry...'
    print(''.join(random.choice(codes.values()) + x + codes['reset'] for x in code))
    sys.exit()


def main():
    if 'cry' in sys.argv:
        handle_cry()

    args = docopt(__doc__, version=version)

    if args['--verbose'] > 1:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    elif args['--verbose'] == 1:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

    if args['upload'] is True:
        handle_upload(args)

    if args['download'] is True:
        handle_download(args)

    if args['delete'] is True:
        handle_delete(args)

    if args['ls'] is True:
        handle_ls(args)

    if args['search'] is True:
        handle_search(args)

    if args['rename'] is True:
        handle_rename(args)

    if args['status'] is True:
        handle_status(args)

    if args['generate_secret'] is True:
        handle_secret(args)


if __name__ == '__main__':
    main()
