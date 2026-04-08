from Helpers.list_randomizer import ListRandomizer
from unittest import TestCase


class InitializeArrayRandomizer(TestCase):

    def setUp(self):
        self.list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.list_randomizer = ListRandomizer(self.list)

    # def test_elements_should_not_repeat(self):

    #     used_elements = []

    #     for i in range(len(self.list_randomizer._list)):
    #         next_element = self.list_randomizer.get_next_element()
    #         if next_element in used_elements:
    #             self.fail()

    #     print(self.list)
    #     self.assertTrue(len(self.list_randomizer._list), 10)

    # def test_elements_should_not_repeat_runs_multiple_times(self):
    #     used_elements = []

    #     for nr in range(5):

    #         for i in range(len(self.list_randomizer._list)):
    #             next_element = self.list_randomizer.get_next_element()
    #             if next_element in used_elements:
    #                 self.fail()

    #         print(self.list)
    #         self.assertTrue(len(self.list_randomizer._list), 10)
    #         used_elements = []

    #     pass

    def test_extend(self):
        new_list = [11, 12, 13, 14, 15]
        self.list_randomizer.extend(new_list, False)

        self.assertEqual(len(self.list_randomizer._list), 15)
