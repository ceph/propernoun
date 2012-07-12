import mock

import sqlalchemy as sq

from .. import dns


def pytest_funcarg__meta(request):
    tmpdir = request.getfuncargvalue('tmpdir')
    engine = sq.create_engine(
        'sqlite:///' + str(tmpdir.join('mock.sqlite3')),
        )
    meta = sq.MetaData()
    meta.bind = engine
    sq.Table(
        'domains',
        meta,
        sq.Column('id', sq.Integer, primary_key=True),
        sq.Column('name', sq.String, nullable=False),
        )
    sq.Table(
        'records',
        meta,
        sq.Column('id', sq.Integer, primary_key=True),
        sq.Column('domain_id', sq.Integer),
        sq.Column('name', sq.String),
        sq.Column('type', sq.String),
        sq.Column('content', sq.String),
        sq.Column('ttl', sq.Integer),
        sq.Column('prio', sq.Integer),
        sq.Column('change_date', sq.Integer),
        sq.Column('ordername', sq.String),
        sq.Column('auth', sq.Boolean),
        )
    meta.create_all()

    meta.tables['domains'].insert().execute(
        name='test.example.com',
        )
    return meta


def test_simple(meta):
    clock = mock.Mock()
    clock.side_effect = [1000001]
    d = dns.update(
        meta=meta,
        config=dict(
            dhcp=dict(
                networks=dict(
                    fakenet='10.1.0.0/16',
                    ),
                ),
            pdns=dict(
                domain='test.example.com',
                ),
            ),
        _clock=clock,
        )
    # start the coroutine
    d.next()

    vm = {
        'name': 'foo',
        'uuid': '20398bc3-c328-4586-95fe-fd2295798cfe',
        'interfaces': [('fakenet', '52:54:00:f3:b7:13')],
        'uri': 'qemu:///system',
        }
    vms = {
        vm['uuid']: vm,
        }
    lease = {
        'ip': '10.1.2.3',
        'mac': '52:54:00:f3:b7:13',
        }
    leases = {
        lease['ip']: lease,
        }

    d.send(dict(
        vms=vms,
        leases=leases,
        complete=False,
        ))

    q = meta.tables['records'].select()
    rows = q.execute().fetchall()
    rows = [dict(r) for r in rows]
    assert rows == [
        dict(
            id=1,
            domain_id=1,
            name='foo.test.example.com',
            type='A',
            content='10.1.2.3',
            ttl=1800,
            prio=None,
            change_date=None,
            ordername='',
            auth=True,
            propernoun_epoch=1000001,
            ),
        ]


def test_prune(meta):
    clock = mock.Mock()
    clock.side_effect = [1000001]
    d = dns.update(
        meta=meta,
        config=dict(
            dhcp=dict(
                networks=dict(
                    fakenet='10.1.0.0/16',
                    ),
                ),
            pdns=dict(
                domain='test.example.com',
                ),
            ),
        _clock=clock,
        )
    # start the coroutine
    d.next()

    meta.tables['records'].insert().execute(
        domain_id=1,
        name='foo.test.example.com',
        type='A',
        content='10.1.2.3',
        ttl=1800,
        prio=None,
        change_date=None,
        ordername='',
        auth=True,
        propernoun_epoch=42,
        )
    meta.tables['records'].insert().execute(
        domain_id=1,
        name='innocent.test.example.com',
        type='A',
        content='10.1.2.3',
        ttl=1800,
        prio=None,
        change_date=None,
        ordername='',
        auth=True,
        )

    d.send(dict(
        vms={},
        leases={},
        complete=True,
        ))

    q = meta.tables['records'].select()
    rows = q.execute().fetchall()
    rows = [r['name'] for r in rows]
    assert rows == ['innocent.test.example.com']
