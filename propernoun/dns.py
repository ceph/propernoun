import ipaddr
import logging
import time

import sqlalchemy as sq


log = logging.getLogger(__name__)


def update(meta, config, _clock=None):
    if _clock is None:
        _clock = lambda: time.time() * 1e6

    try:
        sq.schema.DDL(
            'ALTER TABLE records ADD COLUMN propernoun_epoch INTEGER',
            ).execute(bind=meta.bind)
    except sq.exc.OperationalError as e:
        # ugly hack because SQL a standard isn't
        if 'duplicate column name' in e.message:
            pass
        else:
            raise
    meta.tables['records'].append_column(
        sq.Column('propernoun_epoch', sq.Integer),
        )
    while True:
        state = (yield)
        # if this doesn't tick fast enough, we'll create duplicate
        # entries.. silly but not a real issue
        epoch = int(_clock())

        vms_by_net_mac = {}
        for vm in state['vms'].itervalues():
            for (net, mac) in vm['interfaces']:
                assert (net, mac) not in vms_by_net_mac
                vms_by_net_mac[(net, mac)] = vm

        net_addresses = {}
        for net_name, ip_s in config['dhcp']['networks'].iteritems():
            net_addresses[net_name] = ipaddr.IPv4Network(ip_s)

        for lease in state['leases'].itervalues():
            ip = ipaddr.IPv4Address(lease['ip'])
            for net_name, net_ip in net_addresses.iteritems():
                if ip in net_ip:

                    # TODO do all the networks always go in one
                    # domain?
                    domain_q = sq.select(
                        [meta.tables['domains'].c.id],
                        (meta.tables['domains'].c.name
                         == config['pdns']['domain']),
                        ).limit(1)
                    domain_row = domain_q.execute().fetchone()
                    if domain_row is None:
                        # DNS does not know of this domain
                        log.warning(
                            'Domain missing from DNS database: %r',
                            config['pdns']['domain'],
                            )
                        continue
                    domain_id = domain_row['id']

                    # found the right network, now look for a vm
                    vm = vms_by_net_mac.get((net_name, lease['mac']))
                    if vm is not None:
                        log.debug('Create DNS: %r %s at %d',
                                  vm['name'],
                                  ip,
                                  epoch,
                                  )
                        name = '{prefix}{name}{suffix}.{domain}'.format(
                            prefix=config['pdns'].get('prefix') or '',
                            name=vm['name'],
                            suffix=config['pdns'].get('suffix') or '',
                            domain=config['pdns']['domain'],
                            )
                        meta.tables['records'].insert().execute(
                            domain_id=domain_id,
                            name=name,
                            type='A',
                            content=lease['ip'],
                            # set dynamic vm dns ttl to just
                            # 30seconds, they tend to come and go
                            ttl=30,
                            ordername='',
                            auth=True,
                            propernoun_epoch=epoch,
                            )

        if state['complete']:
            log.debug('Pruning everything older than %d', epoch)
            t = meta.tables['records']
            q = t.delete(
                sq.sql.expression.and_(
                    t.c.propernoun_epoch != None,
                    t.c.propernoun_epoch < epoch,
                    ),
                )
            status = q.execute()
            log.debug('Pruned %d DNS entries', status.rowcount)
