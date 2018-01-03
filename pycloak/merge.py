
def merge(preferred, secondary):
    if isinstance(preferred, dict):
        if not isinstance(secondary, dict):
            return preferred
        return mergeDicts(preferred, secondary)

    if isinstance(preferred, list):
        if not isinstance(secondary, list):
            return preferred

        return mergeLists(preferred, secondary)
    else:
        return preferred

def mergeDicts(preferred, secondary):
    return_dict = {}

    for key, preferred_value in preferred.items():
        if not secondary.get(key):
            return_dict[key] = preferred_value
        else:
            return_dict[key] = merge(preferred_value, secondary[key])

    # Perhaps not the most efficient, but you know what they say about premature optimization....
    for key, secondary_value in secondary.items():
        if not return_dict.get(key):
            return_dict[key] = secondary_value

    return return_dict

def mergeLists(preferred, secondary):
    return preferred
