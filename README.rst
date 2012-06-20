===========================================================================
 Propernoun -- Update PowerDNS from DHCP leases & libvirt virtual machines
===========================================================================

Propernoun monitors an ISC ``dhcpd`` leases file, and multiple remote
``libvirt`` servers, for leases assigned to virtual machines. It then
updates a PowerDNS database to add/delete DNS entries for these
virtual machines.


Installation
============

You can install Propernoun like any other Python package, but it also
comes with a convenient bootstrap script that sets it up in a virtual
environment under the source directory. Just run::

	./bootstrap

And from there on, use::

	./virtualenv/bin/propernoun ARGS..

You can also symlink that to e.g. ``~/bin/``.


Usage
=====

TODO
