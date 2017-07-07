""" UnitTests for LazyDict """

from unittest import TestCase
from TwitterStatsLib import LazyDict

class TestLazyDict(TestCase):
    """ UnitTests for LazyDict """

    def test_adding_happy_path(self):
        """ Basic happy path adding path """
        lazy_dict = LazyDict()
        lazy_dict['first'] = lambda: 'value'
        lazy_dict['second'] = lambda: 'another value'
        self.assertEqual(len(lazy_dict), 2)
