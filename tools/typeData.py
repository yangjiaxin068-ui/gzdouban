from . import homeData

def getMovieTypeData():
    df = homeData.getDataFrame()
    types = df['types'].values
    type_list = []
    for i in types:
        if isinstance(i,list):
             for j in i:
                type_list.append(j)
        else:
                type_list.append(i)
    typeDic = {}
    for i in type_list:
        if not i:
            continue
        if typeDic.get(i,-1) == -1:
            typeDic[i] = 1
        else:
            typeDic[i] = typeDic[i] + 1
    result = []
    for key,value in typeDic.items():
        result.append({
            'name':key,
            'value':value
        })
    return result

