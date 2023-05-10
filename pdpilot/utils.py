""" Utility functions. """


def convert_keys_to_ints(dictionary):
    """Convert string keys that are integers into integers."""
    new_dictionary = {}
    for key, value in dictionary.items():
        if isinstance(key, str) and key.isdigit():
            new_dictionary[int(key)] = value
        else:
            new_dictionary[key] = value
    return new_dictionary
