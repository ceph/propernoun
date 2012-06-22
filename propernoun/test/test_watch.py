import os

from .. import watch


def test_simple(tmpdir):
    path = os.path.join(str(tmpdir), 'dhcpd.leases')
    with file(path, mode='w', buffering=0) as f:
        g = watch.watch_dhcp_leases(path)

        # we see the initial artificial trigger
        got = next(g)
        assert got is None

        f.write('foo')
        got = next(g)
        assert got is not None


def test_rotate(tmpdir):
    path = os.path.join(str(tmpdir), 'dhcpd.leases')
    path_old = os.path.join(str(tmpdir), 'dhcpd.leases~')
    path_new = os.path.join(str(tmpdir), 'dhcpd.leases.new')
    with file(path, mode='w', buffering=0) as f_old:
        f_old.write('blahblah')
        g = watch.watch_dhcp_leases(path)

        # we see the initial artificial trigger
        got = next(g)
        assert got is None

        with file(path_new, mode='w', buffering=0) as f_new:

            os.rename(path, path_old)
            os.rename(path_new, path)

            got = next(g)
            assert got is None

            f_new.write('foo')
            got = next(g)
            assert got is not None
