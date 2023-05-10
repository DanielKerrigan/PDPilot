""" Unit tests for utility functions."""

from pdpilot.utils import convert_keys_to_ints


def test_empty_convert_keys_to_ints():
    """empty dict"""
    assert convert_keys_to_ints({}) == {}


def test_strings_convert_keys_to_ints():
    """all string keys"""
    my_dict = {"a": 1, "b": "b", "c": False}
    assert convert_keys_to_ints(my_dict) == my_dict


def test_ints_convert_keys_to_ints():
    """all int keys"""
    my_dict = {1: 1, 2: "b", 3: False}
    assert convert_keys_to_ints(my_dict) == my_dict


def test_str_ints_convert_keys_to_ints():
    """all int keys"""
    my_dict = {"1": 1, 2: "b", "3": False, "c": 4}
    my_dict_conv = {1: 1, 2: "b", 3: False, "c": 4}
    assert convert_keys_to_ints(my_dict) == my_dict_conv
