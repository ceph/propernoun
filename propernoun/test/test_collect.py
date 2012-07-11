import mock

from .. import collect


def poison(*a, **kw):
    raise AssertionError('Poison called, args=%r kwargs=%r', a, kw)


def test_simple_vm_then_lease():
    cb = mock.Mock()
    s = collect.Collector(callback=cb)

    vm = {
        'name': 'foo',
        'uuid': '20398bc3-c328-4586-95fe-fd2295798cfe',
        'interfaces': [('front', '52:54:00:f3:b7:13')],
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

    s.event(dict(type='libvirt', vm=vm))
    cb.assert_called_once_with(
        vms=vms,
        leases={},
        complete=False,
        )
    cb.reset_mock()

    s.event(dict(type='dhcp', leases=leases))
    cb.assert_called_once_with(
        vms=vms,
        leases=leases,
        complete=False,
        )


def test_simple_lease_then_vm():
    cb = mock.Mock()
    s = collect.Collector(callback=cb)

    vm = {
        'name': 'foo',
        'uuid': '20398bc3-c328-4586-95fe-fd2295798cfe',
        'interfaces': [('front', '52:54:00:f3:b7:13')],
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

    s.event(dict(type='dhcp', leases=leases))
    cb.assert_called_once_with(
        vms={},
        leases=leases,
        complete=False,
        )
    cb.reset_mock()

    s.event(dict(type='libvirt', vm=vm))
    cb.assert_called_once_with(
        vms=vms,
        leases=leases,
        complete=False,
        )


def test_simple_vm_then_lease_complete():
    cb = mock.Mock()
    s = collect.Collector(callback=cb)

    vm = {
        'name': 'foo',
        'uuid': '20398bc3-c328-4586-95fe-fd2295798cfe',
        'interfaces': [('front', '52:54:00:f3:b7:13')],
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

    s.event(dict(type='libvirt', vm=vm))
    cb.assert_called_once_with(
        vms=vms,
        leases={},
        complete=False,
        )
    cb.reset_mock()

    s.event(dict(type='dhcp', leases=leases))
    cb.assert_called_once_with(
        vms=vms,
        leases=leases,
        complete=False,
        )
    cb.reset_mock()

    s.event(dict(type='libvirt_complete'))
    cb.assert_called_once_with(
        vms=vms,
        leases=leases,
        complete=True,
        )


def test_simple_lease_then_complete_vm():
    cb = mock.Mock()
    s = collect.Collector(callback=cb)

    vm = {
        'name': 'foo',
        'uuid': '20398bc3-c328-4586-95fe-fd2295798cfe',
        'interfaces': [('front', '52:54:00:f3:b7:13')],
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

    s.event(dict(type='dhcp', leases=leases))
    cb.assert_called_once_with(
        vms={},
        leases=leases,
        complete=False,
        )
    cb.reset_mock()

    s.event(dict(type='libvirt_complete'))
    cb.assert_called_once_with(
        vms={},
        leases=leases,
        complete=True,
        )
    cb.reset_mock()

    s.event(dict(type='libvirt', vm=vm))
    cb.assert_called_once_with(
        vms=vms,
        leases=leases,
        complete=True,
        )
