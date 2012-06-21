import pytest

from .. import parser


def test_deleted():
    s = """\
lease 1.2.3.4 {
  deleted;
}
"""
    g = parser.parse(s)
    lease = next(g)
    assert lease == dict(ip='1.2.3.4', deleted=True)
    with pytest.raises(StopIteration):
        next(g)


def test_partial():
    s = """\
lease 1.2.3.4 {
  deleted;
}
lease 1.2
"""
    g = parser.parse(s)
    lease = next(g)
    assert lease == dict(ip='1.2.3.4', deleted=True)
    with pytest.raises(StopIteration):
        next(g)


def test_two():
    s = """\
lease 1.2.3.4 {
  deleted;
}
lease 2.3.4.5 {
  deleted;
}
"""
    g = parser.parse(s)
    lease = next(g)
    assert lease == dict(ip='1.2.3.4', deleted=True)
    lease = next(g)
    assert lease == dict(ip='2.3.4.5', deleted=True)
    with pytest.raises(StopIteration):
        next(g)


def test_comment():
    s = """\
# foo
"""
    g = parser.parse(s)
    with pytest.raises(StopIteration):
        next(g)


def test_junk():
    s = """\
lease 10.13.42.20 {
  foo bar;
}
"""
    g = parser.parse(s)
    lease = next(g)
    assert lease == dict(
        ip='10.13.42.20',
        )
    with pytest.raises(StopIteration):
        next(g)


def test_mac():
    s = """\
lease 10.13.42.20 {
  hardware ethernet 52:54:00:de:ad:11;
}
"""
    g = parser.parse(s)
    lease = next(g)
    assert lease == dict(
        ip='10.13.42.20',
        mac='52:54:00:de:ad:11',
        )
    with pytest.raises(StopIteration):
        next(g)


def test_single():
    s = """\
lease 10.13.42.20 {
  starts 4 2012/06/21 18:42:57;
  ends 4 2012/06/21 18:52:57;
  cltt 4 2012/06/21 18:42:57;
  binding state active;
  next binding state free;
  hardware ethernet 52:54:00:de:ad:11;
  client-hostname "dhcptest01";
}
"""
    g = parser.parse(s)
    lease = next(g)
    assert lease == dict(
        ip='10.13.42.20',
        mac='52:54:00:de:ad:11',
        )
    with pytest.raises(StopIteration):
        next(g)


def test_realistic():
    s = """\
# The format of this file is documented in the dhcpd.leases(5) manual page.
# This lease file was written by isc-dhcp-4.1-ESV-R4

lease 10.13.42.20 {
  starts 4 2012/06/21 18:34:10;
  ends 4 2012/06/21 18:44:10;
  cltt 4 2012/06/21 18:34:10;
  binding state active;
  next binding state free;
  hardware ethernet 52:54:00:de:ad:11;
  client-hostname "dhcptest01";
}
server-duid "\000\001\000\001\027u\016\024RT\000H\227W";

lease 10.13.42.20 {
  starts 4 2012/06/21 18:42:57;
  ends 4 2012/06/21 18:52:57;
  cltt 4 2012/06/21 18:42:57;
  binding state active;
  next binding state free;
  hardware ethernet 52:54:00:de:ad:11;
  client-hostname "dhcptest01";
}
lease 10.13.42.20 {
  starts 4 2012/06/21 18:52:01;
  ends 4 2012/06/21 19:02:01;
  cltt 4 2012/06/21 18:52:01;
  binding state active;
  next binding state free;
  hardware ethernet 52:54:00:de:ad:11;
  client-hostname "dhcptest01";
}
lease 10.1.2.3 {
  starts 4 2012/06/21 18:53:35;
  ends 4 2012/06/21 19:03:35;
  cltt 4 2012/06/21 18:53:35;
  binding state active;
  next binding state free;
  hardware ethernet 52:54:00:f0:0b:a5;
  client-hostname "dhcptest02";
}
lease 10.13.42.20 {
  starts 4 2012/06/21 19:00:47;
  ends 4 2012/06/21 19:10:47;
  cltt 4 2012/06/21 19:00:47;
  binding state active;
  next binding state free;
  hardware ethernet 52:54:00:de:ad:11;
  client-hostname "dhcptest01";
}
"""
    g = parser.parse(s)
    lease = next(g)
    assert lease == dict(ip='10.13.42.20', mac='52:54:00:de:ad:11')
    lease = next(g)
    assert lease == dict(ip='10.13.42.20', mac='52:54:00:de:ad:11')
    lease = next(g)
    assert lease == dict(ip='10.13.42.20', mac='52:54:00:de:ad:11')
    lease = next(g)
    assert lease == dict(ip='10.1.2.3', mac='52:54:00:f0:0b:a5')
    lease = next(g)
    assert lease == dict(ip='10.13.42.20', mac='52:54:00:de:ad:11')
    with pytest.raises(StopIteration):
        next(g)
