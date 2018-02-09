from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from functools import partial
import types

import netaddr
from ansible import errors

def cidr_merge(value):
    if not isinstance(value, (list, tuple, types.GeneratorType)):
        raise errors.AnsibleFilterError('cidr_merge: need sequence or iterable')
    return [ str(ip) for ip in netaddr.cidr_merge(value) ]

class FilterModule(object):
    def filters(self):
        return { 'cidr_merge': cidr_merge }

