from lxml import etree


def get_interfaces(xml_s):
    tree = etree.fromstring(xml_s)
    print tree.xpath.__doc__
    networks = tree.xpath(
        "/domain/devices/interface[@type='network']",
        )
    for net in networks:
        (name,) = net.xpath('./source/@network')
        (mac,) = net.xpath('./mac/@address')
        yield (name, mac)
