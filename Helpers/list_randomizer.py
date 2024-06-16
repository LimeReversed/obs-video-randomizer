import random
import json


class ListRandomizer(object):

    def __init__(self, list):
        self.list = list
        self._current_last_index = len(list) - 1

    def to_json(self):
        json_string = json.dumps(self, default=lambda obj: self.__dict__, indent=4)
        return json_string

    @staticmethod
    def construct_from_json(json_object):
        new_list_randomizer = ListRandomizer(json_object["list"])
        new_list_randomizer._current_last_index = json_object["current_last_index"]
        return new_list_randomizer

    def get_next_element(self):
        next_index = random.randint(0, self._current_last_index)
        next_element = self.list[next_index]

        # Put the element at the end of the array
        tmp = self.list[next_index]
        self.list[next_index] = self.list[self._current_last_index]
        self.list[self._current_last_index] = tmp

        if self._current_last_index - 1 >= 0:
            self._current_last_index -= 1
        else:
            self._current_last_index = len(self.list) - 1

        return next_element
