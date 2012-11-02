import Queue
import logging

import sqlalchemy as sq

from . import collect
from . import dns
from . import leases
from . import safethread
from . import virt_mon


log = logging.getLogger(__name__)


def main(
    config,
    ):
    events = Queue.Queue()

    engine = sq.create_engine(
        config['pdns']['database'],
        )
    meta = sq.MetaData()
    meta.bind = engine
    meta.reflect()

    dns_updater = dns.update(
        meta=meta,
        config=config,
        db=config['pdns']['database'],
        )
    # start the coroutine
    dns_updater.next()

    collector = collect.Collector(
        callback=dns_updater.send,
        )

    callables = []

    def submit_libvirt_event(msg):
        events.put(msg)

    def monitor_libvirt():
        """monitor libvirt"""
        virt_mon.monitor(
            uris=config['libvirt']['uris'],
            callback=submit_libvirt_event,
            )
    callables.append(monitor_libvirt)

    def monitor_dhcp():
        """monitor dhcp"""
        for by_ip in leases.gen_leases(path=config['dhcp']['leases']):
            msg = dict(
                type='dhcp',
                leases=by_ip,
                )
            events.put(msg)
    callables.append(monitor_dhcp)

    def send_to_collector():
        """collector"""
        while True:
            msg = events.get()
            log.debug('Event: %r', msg)
            collector.event(msg)
    callables.append(send_to_collector)

    safethread.run_safe_threads(*callables)
