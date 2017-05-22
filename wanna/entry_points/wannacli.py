#!/usr/bin/env python
"""Wanna transfer.

Usage:
  wanna upload [--no-encrypt] [--no-progress] [-v | -vv]
               [--checksum] [--datacenter=<aws>] [--ignore--prefix] PATH
  wanna download [--no-decrypt] [--no-progress] [-v | -vv]
                 [--checksum] [--datacenter=<aws>] PATH
  wanna delete [--datacenter=<aws>] [--ignore-prefix] [-v | -vv] PATH
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
"""
from docopt import docopt
from wanna import __version__ as version

import sys
import logging


LOG = logging.getLogger('wanna')


def _handle(args):
    if args['PATH'] is not None:
        path = args['PATH']
        if args['upload'] or args['download']:
            add_checksum = args['--checksum']
            use_encryption =  not(args['--no-encrypt'] or args['--no-decrypt'])
            progress = not(args['--no-progress'])
    vendor = args['--datacenter']
    ignore_prefix = args['--ignore-prefix']
    args = locals()
    args.pop('args')
    LOG.debug(args)
    return args


def handle_upload(args):
    from wanna import upload_file
    kwargs = _handle(args)
    LOG.info('Uploading {path}...'.format(**kwargs))
    upload_file(**kwargs)


def handle_ls(args):
    from wanna import list_files
    kwargs = _handle(args)
    list_files(**kwargs)


def handle_download(args):
    from wanna import download_file

    kwargs = _handle(args)
    LOG.info('Getting {path}...'.format(**kwargs))
    download_file(**kwargs)


def handle_delete(args):
    from wanna import delete_file

    kwargs = _handle(args)
    LOG.info('Deleting {path}...'.format(**kwargs))
    delete_file(**kwargs)


def handle_cry():
    import random
    from pygments.console import codes
    code = 'Hahahah you wanna cry...'
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

    if args['upload'] is True:
        handle_upload(args)

    if args['download'] is True:
        handle_download(args)

    if args['delete'] is True:
        handle_delete(args)

    if args['ls'] is True:
        handle_ls(args)

if __name__ == '__main__':
    main()
