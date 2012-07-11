import argparse
import logging
import sys

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
        '-c', '--connect',
        metavar='URI',
        action='append',
        help='libvirt URI to connect to',
        )
    parser.add_argument(
        '--dhcp-leases',
        metavar='PATH',
        help='path to dhcpd leases file',
        )
    parser.set_defaults(
        # we want to hold on to this, for later
        prog=parser.prog,
        connect=[],
        dhcp_leases='/var/lib/dhcp/dhcpd.leases',
        )
    args = parser.parse_args()
    if not args.connect:
        parser.error('Need at least one libvirt URI to connect to.')
    return args


def main():
    args = parse_args()

    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG

    logging.basicConfig(
        level=loglevel,
        )

    try:
        return main_.main(
            uris=args.connect,
            dhcp_leases_path=args.dhcp_leases,
            )
    except exc.PropernounError as e:
        print >>sys.stderr, '{prog}: {msg}'.format(
            prog=args.prog,
            msg=e,
            )
        sys.exit(1)
