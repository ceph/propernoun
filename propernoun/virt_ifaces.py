def get_interfaces(tree):
    networks = tree.xpath(
        "/domain/devices/interface[@type='network']",
        )
    for net in networks:
        (name,) = net.xpath('./source/@network')
        (mac,) = net.xpath('./mac/@address')
        yield (name, mac)
