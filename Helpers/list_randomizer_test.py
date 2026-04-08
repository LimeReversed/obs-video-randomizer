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
