from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from functools import partial
import types

import netaddr
from ansible import errors

class FilterModule(object):
    def filters(self):
        return { 'cidr_merge': cidr_merge }

def cidr_merge(value, action='merge'):
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

    else:
        raise errors.AnsibleFilterError("cidr_merge: invalid action '%s'" % action)
