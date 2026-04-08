from list_randomizer import ListRandomizer
from unittest import TestCase


class InitializeArrayRandomizer(TestCase):

    def setUp(self):
        self.list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.list_randomizer = ListRandomizer(self.list)

    def test_elements_should_not_repeat(self):

        used_elements = []

        for i in range(len(self.list)):
            next_element = self.list_randomizer.get_next_element()
            if next_element in used_elements:
                self.fail()
            used_elements.append(next_element)

        print(f"Original list: {self.list}")
        print(f"Used elements: {used_elements}")
        self.assertTrue(len(self.list) == len(used_elements))

    def test_elements_should_not_repeat_runs_multiple_times(self):
        used_elements = []

        for nr in range(5):

            for i in range(len(self.list)):
                next_element = self.list_randomizer.get_next_element()
                if next_element in used_elements:
                    self.fail()
                used_elements.append(next_element)

            print(f"Original list: {self.list}")
            print(f"Used elements: {used_elements}")
            self.assertFalse(not len(self.list) == len(used_elements))
            used_elements = []

        pass

    def test_extend_should_add_elements_to_the_end_of_the_list(self):
        new_list = [11, 12, 13]
        self.list_randomizer.extend(new_list, True)
        
        print(f"Final list: {self.list_randomizer._list}")
        self.assertEqual(self.list_randomizer._list, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        self.assertEqual(self.list_randomizer._current_last_index, 12)

    def test_extend_should_add_elements_to_the_beginning_of_the_list(self):
        new_list = [11, 12, 13]
        self.list_randomizer.extend(new_list, False)
        
        print(f"Final list: {self.list_randomizer._list}")
        self.assertEqual(self.list_randomizer._list, [11, 12, 13, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(self.list_randomizer._current_last_index, 12)

    def test_merge_should_merge_two_list_randomizers(self):
        new_list_randomizer = ListRandomizer([11, 12, 13])
        self.list_randomizer.merge(new_list_randomizer)

        print(f"Final list: {self.list_randomizer._list}")
        self.assertEqual(self.list_randomizer._list, [11, 12, 13, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(self.list_randomizer._current_last_index, 12)