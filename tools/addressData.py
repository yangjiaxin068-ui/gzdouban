from . import homeData


def _count_items(values):
    result = {}
    for value in values:
        if not value:
            continue
        result[value] = result.get(value, 0) + 1

    sorted_items = sorted(result.items(), key=lambda item: item[1])
    return [item[0] for item in sorted_items], [item[1] for item in sorted_items]


def getAddressData():
    df = homeData.getDataFrame()
    addrsses = df['country'].values
    address = []
    for i in addrsses:
        if isinstance(i, list):
            for j in i:
                address.append(j)
        else:
                address.append(i)
    return _count_items(address)


def getLangData():
    df = homeData.getDataFrame()
    langs = df['lang'].values
    langes = []
    for i in langs:
        if isinstance(i, list):
            for j in i:
                langes.append(j)
        else:
            langes.append(i)
    return _count_items(langes)
