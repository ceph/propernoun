import inotifyx
import os


def watch_dhcp_leases(path):
    """
    This is a generator for events that happen to the file at the
    given path. It assumes ISC DHCPD -like behavior; that is, ISC
    dhcpd man page dhcpd.leases(5) promises that the leases file is
    only updated in exactly two ways:

    1. new entries are appended

    2. a new (pruned) lease file is renamed to the monitored filename
       (the old file is first moved out of the way, but that's not
       relevant here)

    So we trigger events on appends and lease file replacement, and
    start monitoring the new file on the latter.

    Example::

        for _ in watch('/var/lib/dhcp/dhcpd.leases'):
            print "Stuff happened!"

    """
    fd = inotifyx.init()
    parent = os.path.dirname(path)
    if parent == '':
        # this happens if path had no slashes in it; mostly when
        # testing manually
        parent = '.'

    try:
        wd_new = inotifyx.add_watch(
            fd,
            parent,
            inotifyx.IN_MOVED_TO | inotifyx.IN_ONLYDIR,
            )

        while True:
            # the only real reason for `path` not to exist here is on
            # first loop (assuming dhcpd behavior); `replaced` only
            # becomes True after a file is renamed to this name, so
            # there's no race there (barring un-dhcpd like behavior
            # like deleting the file)
            wd_journal = inotifyx.add_watch(
                fd,
                path,
                inotifyx.IN_MODIFY,
                )

            # yield once in order to 1) make caller read the existing
            # content of the file and 2) make writing unit tests
            # easier; now we already have an open inotify fd with the
            # right watches
            yield None

            replaced = False
            while not replaced:
                for e in inotifyx.get_events(fd):
                    if e.mask & inotifyx.IN_Q_OVERFLOW:
                        yield e
                        # we could have lost an IN_MOVED_TO event,
                        # do this just in case
                        replaced = True
                    elif e.wd == wd_journal:
                        yield e
                    elif (e.wd == wd_new
                          and e.mask & inotifyx.IN_MOVED_TO
                          and e.name == os.path.basename(path)):
                        # the old watch is implicitly removed as the
                        # file is deleted, no need to clean that up;
                        # not 100% sure if this will leak wds or not
                        replaced = True
    finally:
        os.close(fd)
