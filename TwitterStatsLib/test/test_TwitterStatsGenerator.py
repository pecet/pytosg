""" UnitTests for TwitterStatsGenerator """

from unittest import TestCase
from collections import OrderedDict
from TwitterStatsLib import TwitterStatsGenerator

class TestMap(TestCase):
    """ UnitTests for TwitterStatsGenerator._map method """

    def test_simple_mapping(self):
        d = {}
        values = {"1st": 111, "2nd": 222}
        d = TwitterStatsGenerator._map(d, values, ["1st", "2nd"], False)
        self.assertDictEqual(d, {111: 222})

        d = {}
        d = TwitterStatsGenerator._map(d, values, ["2nd", "1st"], False)
        self.assertDictEqual(d, {222: 111})

    def test_simple_mapping_and_adding(self):
        d = {}
        values = {"name": "john", "age": 34}
        d = TwitterStatsGenerator._map(d, values, ["name", "age"], False)
        self.assertDictEqual(d, {"john": 34})

        values = {"name": "alan", "age": 12}
        d = TwitterStatsGenerator._map(d, values, ["name", "age"], False)
        self.assertDictEqual(d, {"john": 34, "alan": 12})

    def test_complex_mapping(self):
        d = {}
        values = {"cc": "us", "first_name": "john", "last_name": "smith", "age": 34}
        d = TwitterStatsGenerator._map(d, values, ["cc", "last_name", "first_name", "age"], False)

        values = {"cc": "us", "first_name": "alan", "last_name": "smith", "age": 12}
        d = TwitterStatsGenerator._map(d, values, ["cc", "last_name", "first_name", "age"], False)

        values = {"cc": "us", "first_name": "alan", "last_name": "alanovsky", "age": 101}
        d = TwitterStatsGenerator._map(d, values, ["cc", "last_name", "first_name", "age"], False)

        values = {"cc": "pl", "first_name": "jan", "last_name": "kowalski", "age": 65}
        d = TwitterStatsGenerator._map(d, values, ["cc", "last_name", "first_name", "age"], False)
        expected = {"us":
                        {"smith":
                            {"john": 34, "alan": 12},
                         "alanovsky":
                            {"alan": 101}
                        },
                    "pl":
                        {"kowalski":
                            {"jan": 65}
                        }
                   }

        self.assertDictEqual(d, expected)

    def test_complex_mapping_ordered_dict(self):
        d = OrderedDict()
        values = {"1st": 111, "2nd": 222, "3rd": 333}
        d = TwitterStatsGenerator._map(d, values, ["1st", "2nd", "3rd"], True)
        self.assertIsInstance(d[111], OrderedDict)
        expected = OrderedDict()
        expected[111] = OrderedDict()
        expected[111][222] = 333
        self.assertDictEqual(d, expected)


