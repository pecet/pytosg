""" Simple module to add InsertableOrderedDict, variant of OrderedDict with addafter method """
# pylint: disable=E1101
# disable error while accessing private member of OrderedDict
from collections import OrderedDict
class InsertableOrderedDict(OrderedDict):
    """ OrderedDict extending class which adds method to insert new key at arbitary position """
    def insertafter(self, afterkey, key, value, dict_setitem=dict.__setitem__):
        # Each link is stored as a list of length three:  [0=PREV, 1=NEXT, 2=KEY].
        if afterkey not in self:
            raise KeyError('Cannot insert new value after not-existing key \'{0}\''.format(afterkey))

        node = self._OrderedDict__map[afterkey]
        node_next = node[1]
        if key in self:
            del self[key]
        node[1] = node_next[0] = self._OrderedDict__map[key] = [node, node_next, key]
        dict_setitem(self, key, value)
