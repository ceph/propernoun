import logging


log = logging.getLogger(__name__)


class Collector(object):
    def __init__(self, callback):
        self.callback = callback
        self.leases = {}
        self.seen_leases = False
        self.vms = {}
        self.seen_all_vms = False

    def event_libvirt(self, event):
        vm = event['vm']
        ifaces = vm.get('interfaces')
        if ifaces is not None:
            # add
            log.debug('New or updated vm %r with interfaces %r',
                      vm['name'], ifaces)
            uuid = vm['uuid']
            self.vms[uuid] = vm
        else:
            # delete
            log.debug('Removing vm %r', vm['name'])
            uuid = vm['uuid']
            del self.vms[uuid]

    def event_libvirt_complete(self, event):
        self.seen_all_vms = True

    def event_dhcp(self, event):
        leases = event['leases']
        log.debug('Updating leases, now at %d entries', len(leases))
        self.leases.clear()
        self.leases.update(leases)
        self.seen_leases = True

    def event_unknown(self, event):
        log.debug('Unknown event: %r', event)

    def event(self, event):
        fn = getattr(
            self,
            'event_{type}'.format(type=event['type']),
            self.event_unknown,
            )
        fn(event)
        self.callback(
            dict(
                vms=self.vms,
                leases=self.leases,
                complete=(self.seen_all_vms and self.seen_leases),
                ),
            )
