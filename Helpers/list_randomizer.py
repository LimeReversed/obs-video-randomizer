import random
import json


class ListRandomizer(object):

    def __init__(self, new_list):
        self._list = new_list
        self._current_last_index = len(new_list) - 1

    def to_json(self):
        json_string = json.dumps(self, default=lambda obj: self.__dict__, indent=4)
        return json_string

    @staticmethod
    def construct_from_json(json_object):
        new_list_randomizer = ListRandomizer(json_object["list"])
        new_list_randomizer._current_last_index = json_object["current_last_index"]
        return new_list_randomizer

    def get_next_element(self):
        if self._current_last_index < 0:
            self._current_last_index = len(self._list) - 1

        next_index = random.randint(0, self._current_last_index)
        next_element = self._list[next_index]

        # Put the element at the end of the array
        tmp = self._list[next_index]
        self._list[next_index] = self._list[self._current_last_index]
        self._list[self._current_last_index] = tmp
        self._current_last_index -= 1

        return next_element

    def merge(self, new_list_randomizer: "ListRandomizer"):

        used = new_list_randomizer._list[new_list_randomizer._current_last_index:len(new_list_randomizer._list)]
        not_used = new_list_randomizer._list[0:new_list_randomizer._current_last_index + 1]
        self.extend(not_used, False)
        self.extend(used, True)

    def extend(self, new_list: list, mark_as_used: bool):

        if mark_as_used:
            self._list.extend(new_list)
        else:
            new_list.extend(self._list)
            self._current_last_index += len(new_list)
