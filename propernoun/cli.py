import argparse
import logging
import sys
import yaml

from . import exc
from . import main as main_


log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create an Ubuntu Cloud image vm',
        )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true', default=None,
        help='be more verbose',
        )
    parser.add_argument(
        'configfile',
        metavar='CONFIGFILE',
        help='path to YAML config file',
        )
    parser.set_defaults(
        # we want to hold on to this, for later
        prog=parser.prog,
        )
    args = parser.parse_args()
    return args


def read_config(path):
    with file(path) as f:
        obj = yaml.safe_load(f)
    assert 'propernoun' in obj
    return obj['propernoun']


def main():
    args = parse_args()

    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG

    logging.basicConfig(
        level=loglevel,
        )

    config = read_config(args.configfile)

    try:
        return main_.main(
            config=config,
            )
    except exc.PropernounError as e:
        print >>sys.stderr, '{prog}: {msg}'.format(
            prog=args.prog,
            msg=e,
            )
        sys.exit(1)
