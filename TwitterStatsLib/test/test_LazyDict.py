""" UnitTests for LazyDict """

from unittest import TestCase
from TwitterStatsLib import LazyDict

class InnerTestClass(object):
    """ Class to use in tests """
    pass

class TestLazyDict(TestCase):
    """ UnitTests for LazyDict """

    def test_adding(self):
        """ Basic happy path adding path """
        lazy_dict = LazyDict()
        lazy_dict['first'] = lambda: 'value'
        lazy_dict['second'] = lambda: 'another value'
        self.assertEqual(len(lazy_dict), 2)

    def test_adding_not_callable(self):
        """ Adding not callable object for dictionary key """
        with self.assertRaises(TypeError):
            lazy_dict = LazyDict()
            lazy_dict['first'] = 'non-callable value'

    def test_accessing_element(self):
        """ Test accessing element for first time """
        lazy_dict = LazyDict()
        lazy_dict['first'] = lambda: 'value'
        lazy_dict['second'] = lambda: 'another value'
        lazy_dict['int'] = lambda: 10
        lazy_dict['object'] = InnerTestClass
        self.assertEqual(lazy_dict['first'], 'value')
        self.assertEqual(lazy_dict['second'], 'another value')
        self.assertEqual(lazy_dict['int'], 10)
        self.assertIsInstance(lazy_dict['object'], InnerTestClass)

    def test_accessing_cached_element(self):
        """ Test accessing element for second time (cached access) """
        lazy_dict = LazyDict()
        lazy_dict['first'] = lambda: 'value'
        lazy_dict['object'] = InnerTestClass
        self.assertFalse(lazy_dict.is_computed('first'))
        self.assertEqual(lazy_dict['first'], 'value')
        self.assertTrue(lazy_dict.is_computed('first'))
        self.assertEqual(lazy_dict['first'], 'value')
        self.assertFalse(lazy_dict.is_computed('object'))
        self.assertIsInstance(lazy_dict['object'], InnerTestClass)
        self.assertTrue(lazy_dict.is_computed('object'))
        self.assertIsInstance(lazy_dict['object'], InnerTestClass)

    def test_changing_element(self):
        """ Test modifying element (changing callable) """
        lazy_dict = LazyDict()
        lazy_dict['first'] = lambda: 'value'
        self.assertEqual(lazy_dict['first'], 'value')
        self.assertTrue(lazy_dict.is_computed('first'))
        lazy_dict['first'] = lambda: 'another value'
        self.assertFalse(lazy_dict.is_computed('first'))
        self.assertEqual(lazy_dict['first'], 'another value')
        self.assertTrue(lazy_dict.is_computed('first'))
