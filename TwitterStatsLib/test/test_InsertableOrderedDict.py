""" UnitTests for InsertableOrderedDict """

from unittest import TestCase
from TwitterStatsLib import InsertableOrderedDict

class TestInsertableOrderedDict(TestCase):
    """ UnitTests for InsertableOrderedDict """

    def test_insertafter_key(self):
        """ Test inserting after existing key """
        ins_dict = InsertableOrderedDict()
        ins_dict["A"] = 1
        ins_dict["C"] = 3
        self.assertEqual(len(ins_dict), 2)

        ins_dict.insertafter("A", "B", 2)
        self.assertEqual(len(ins_dict), 3)
        self.assertEqual(ins_dict["B"], 2)
        self.assertListEqual([('A', 1), ('B', 2), ('C', 3)], ins_dict.items())

    def test_insertafter_beggining(self):
        """ Test inserting after root key """
        ins_dict = InsertableOrderedDict()
        ins_dict["A"] = 1
        ins_dict["C"] = 3
        self.assertEqual(len(ins_dict), 2)
        ins_dict.insertafter(None, "Beginning", 0)
        self.assertEqual(len(ins_dict), 3)
        self.assertEqual(ins_dict["Beginning"], 0)
        self.assertListEqual([('Beginning', 0), ('A', 1), ('C', 3)], ins_dict.items())

    def test_insertafter_key(self):
        """ Test inserting after existing key with key which also already exists """
        ins_dict = InsertableOrderedDict()
        ins_dict["A"] = 1
        ins_dict["C"] = 3
        self.assertEqual(len(ins_dict), 2)

        ins_dict.insertafter("A", "B", 2)
        ins_dict.insertafter("C", "B", 101)
        self.assertEqual(len(ins_dict), 3)
        self.assertEqual(ins_dict["B"], 101)
        self.assertListEqual([('A', 1), ('C', 3), ('B', 101)], ins_dict.items())
