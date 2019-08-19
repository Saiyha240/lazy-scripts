import re
from copy import deepcopy
from typing import Dict, List, Any


class Encode(object):
    """
    This class searches for string respresentation of numbers in a nested dict or list and converts them
    to their proper format.
    """

    @staticmethod
    def traverse_dict(d: Dict) -> Dict:
        """
        Traverse a dictionary to look for and parse string numbers

        :param d: Dictionary object to traverse
        :return: Traversed dictionary where string types are already parsed
        """
        d_c: Dict = deepcopy(d)

        for key, value in d_c.items():
            d_c[key] = Encode.guess_encode(value)

        return d_c

    @staticmethod
    def traverse_list(l: List) -> List:
        """
        Traverse a list to look for and parse string numbers

        :param l: List object to traverse
        :return: Traversed list where string types are already parsed
        """
        l_c = deepcopy(l)

        for idx, item in enumerate(l_c):
            l_c[idx] = Encode.guess_encode(item)

        return l_c

    @staticmethod
    def parse_string(string: str) -> [str, int, float]:
        """
        Returns a number if the string is a valid number else return the string

        :param string: String object to check
        :return: int number or float number or string
        """
        if re.match(r'\d+\.\d+', string):
            return float(string)
        elif re.match(r'\d+', string):
            return int(string)

        return string

    @staticmethod
    def guess_encode(obj: Any) -> Any:
        """
        Check type to determine appropriate traversal

        :param obj: Object to traverse
        :return: Traversed object
        """
        if isinstance(obj, Dict):
            return Encode.traverse_dict(obj)
        elif isinstance(obj, List):
            return Encode.traverse_list(obj)
        elif isinstance(obj, str):
            return Encode.parse_string(obj)
