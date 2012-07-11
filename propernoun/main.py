import Queue

from . import leases
from . import safethread
from . import virt_mon


def main(
    uris,
    dhcp_leases_path,
    ):
    events = Queue.Queue()

    callables = []

    def submit_libvirt_event(msg):
        events.put(msg)

    def monitor_libvirt():
        """monitor libvirt"""
        virt_mon.monitor(
            uris=uris,
            callback=submit_libvirt_event,
            )
    callables.append(monitor_libvirt)

    def monitor_dhcp():
        """monitor dhcp"""
        for by_ip in leases.gen_leases(path=dhcp_leases_path):
            msg = dict(
                type='dhcp',
                leases=by_ip,
                )
            events.put(msg)
    callables.append(monitor_dhcp)

    def collector():
        """collector"""
        while True:
            msg = events.get()
            print msg
    callables.append(collector)

    safethread.run_safe_threads(*callables)
