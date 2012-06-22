from . import parser
from . import watch

def gen_leases(path):
    """
    Keep track of currently valid leases for ISC dhcpd.

    Yields dictionaries that map ``ip`` to information about the
    lease. Will block until new information is available.
    """
    g = watch.watch_dhcp_leases(path)
    for _ in g:
        with file(path) as f:
            s = f.read()
        leases = {}
        for l in parser.parse(s):
            assert 'ip' in l
            leases[l['ip']] = l
        yield leases
