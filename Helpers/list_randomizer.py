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

    @staticmethod
    def construct_from_video_list(full_video_list, list_of_used):
        used = []
        not_used = []
        for i in range(len(full_video_list)):
            item = full_video_list[i]
            if item in list_of_used:
                used.append(item)
            else:
                not_used.append(item)

        new_list_randomizer = ListRandomizer(not_used)
        new_list_randomizer.extend(used, True)
        return new_list_randomizer

    def get_used(self):
        return self._list[self._current_last_index : len(self._list)]

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

    def extend(self, new_list: list, add_as_used: bool):

        if add_as_used:
            self._list.extend(new_list)
        else:
            new_list.extend(self._list)
            self._current_last_index += len(new_list)
