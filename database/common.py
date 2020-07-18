def group_by_primary_key(data, key):
    """
    Group the data by the specified unique key
    :param data: list of dictionaries that contain the specified key
    :param key: key to group by
    :return: dict of keys mapped to the data value containing that key
    """
    group = dict()
    if data:
        for item in data:
            group[item[key]] = item
    return group


def group_by_foreign_key(data, key):
    """
    Groups the data by the specified key
    :param data: list of dictionaries that contain the specified key
    :param key: key to group by
    :return: dict of keys mapped to a list of data values containing that key
    """
    group = dict()
    if data:
        for item in data:
            values = group.setdefault(item[key], [])
            values.append(item)
    return group