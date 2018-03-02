from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from functools import partial
import types

import netaddr
from ansible import errors

class FilterModule(object):
    def filters(self):
        return { 'cidr_merge': cidr_merge }

def cidr_merge(value, action='merge', slop=None):
    if not hasattr(value, '__iter__'):
        raise errors.AnsibleFilterError('cidr_merge: expected iterable, got ' + repr(value))

    if action == 'merge':
        return [str(ip) for ip in netaddr.cidr_merge(value)]

    elif action == 'span':                                                              # spanning_cidr needs at least two values
        if len(value) == 0:
            return None
        elif len(value) == 1:
            return str(netaddr.IPNetwork(value[0]))
        else:
            return str(netaddr.spanning_cidr(value))

    elif action == 'subnetspan':
        if len(value) == 0:
            return []
        try:
            ips = sorted([netaddr.IPNetwork(v) for v in value])
            ret = []
            low = ips[0]
            for ip in ips:
                if ip.version != low.version:
                    # We've moved from IPv4 to IPv6, add the range and restart
                    ret.extend(netaddr.iprange_to_cidrs(low, high))
                    low = ip
                if slop and ip.prefixlen > slop:
                    ip.prefixlen = slop
                high = ip.broadcast
            ret.extend(netaddr.iprange_to_cidrs(low, high))
            return [str(ip) for ip in ret]
        except Exception as e:
            raise errors.AnsibleFilterError('cidr_merge: error in netaddr:\n%s' % e)

    else:
        raise errors.AnsibleFilterError("cidr_merge: invalid action '%s'" % action)
