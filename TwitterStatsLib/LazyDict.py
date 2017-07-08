""" Simple module implementing lazy-loading dictionary class LazyDict """

class LazyDict(dict):
    """ Simple implementation of dictionary which lazily compute values for its keys
        when they are accessed

        Note: calling repr function on LazyDict object does not compute any values

        Usage:
            mydict = LazyDict()
            mydict['value'] = zero_argument_function
    """

    def __init__(self):
        self._computed_dict = {} # already computed dict keys
        super(LazyDict, self).__init__(self)

    def __setitem__(self, key, value):
        if callable(value):
            super(LazyDict, self).__setitem__(key, value)
            if self._computed_dict.has_key(key):
                self._computed_dict.pop(key)
        else:
            raise TypeError('Supplied dictionary key is not callable')

    def __repr__(self):
        repr_str = '{'
        for key, value in super(LazyDict, self).iteritems():

            value_or_not_computed = 'NOT_COMPUTED' + repr(value)
            if self.is_computed(key):
                value_or_not_computed = repr(self._computed_dict[key])
            repr_str += repr(key) + ": " + value_or_not_computed + ", "

        if len(repr_str) > 2:
            return repr_str[:-2] + '}'
        return '{}'


    def __getitem__(self, key):
        if self.is_computed(key):
            return self._computed_dict[key]
        else:
            func = super(LazyDict, self).__getitem__(key)
            func_value = func() # callability already checked in __setitem__
            self._computed_dict[key] = func_value
            return func_value

    def is_computed(self, key):
        """ Returns True if value for key is already computed
            or False if value for key is not computed """

        return self._computed_dict.has_key(key)
