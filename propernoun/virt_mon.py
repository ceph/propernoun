import json
import libvirt
import sys

from lxml import etree

from . import virt_ifaces


def _handle_event(conn, domain, event, detail, opaque):
    msg = dict(
        type='libvirt',
        name=domain.name(),
        uuid=domain.UUIDString(),
        uri=opaque['uri'],
        )
    if event == libvirt.VIR_DOMAIN_EVENT_DEFINED:
        xml_s = domain.XMLDesc(flags=0)
        tree = etree.fromstring(xml_s)
        ifaces = virt_ifaces.get_interfaces(tree)
        ifaces = list(ifaces)
        msg['interfaces'] = ifaces
    elif event == libvirt.VIR_DOMAIN_EVENT_UNDEFINED:
        pass
    else:
        print >>sys.stderr, \
            ('unknown event:'
             + ' Domain {name} event={event} detail={detail}'.format(
                    name=domain.name(),
                    event=event,
                    detail=detail,
                    )
             )
        return

    opaque['callback'](msg)


def monitor(uris, callback):
    libvirt.virEventRegisterDefaultImpl()

    conns = {}
    for uri in uris:
        conn = libvirt.openReadOnly(uri)
        conns[uri] = conn

        conn.setKeepAlive(5, 3)

        conn.domainEventRegisterAny(
            dom=None,
            eventID=libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
            cb=_handle_event,
            opaque=dict(uri=uri, callback=callback),
            )

    for uri, conn in conns.iteritems():
        for name in conn.listDefinedDomains():
            try:
                domain = conn.lookupByName(name)
            except libvirt.libvirtError as e:
                if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                    # lost a race, someone undefined the domain
                    # between listing names and fetching details
                    pass
                else:
                    raise
            else:
                # inject fake defined event for each domain that
                # exists at startup
                _handle_event(
                    conn=conn,
                    domain=domain,
                    event=libvirt.VIR_DOMAIN_EVENT_DEFINED,
                    detail=None,
                    opaque=dict(uri=uri, callback=callback),
                    )

    while True:
        libvirt.virEventRunDefaultImpl()

        for uri, conn in conns.iteritems():
            if not conn.isAlive() == 1:
                # conn.close() tends to fail at this point, so don't
                # even try
                raise RuntimeError(
                    'Lost connection to {uri}'.format(uri=uri),
                    )


def main():
    def cb(msg):
        sys.stdout.write(json.dumps(msg) + '\n')
        sys.stdout.flush()

    uris = sys.argv[1:]
    monitor(uris, callback=cb)


if __name__ == "__main__":
    main()
