def find_replace(arg1):
    dictionary = {" ": '_',
                'Š': 'S',
                'ł': 'l',
                'ë': 'e',
                'Ż': 'Z',
                'ę': 'e'}

    if(type(arg1) is list):
        return [find_replace(el) for el in arg1]
    # is the item in the dict?
    elif(type(arg1) is str):
        for item in arg1:
            # iterate by keys
            if item in dictionary.keys():
            # look up and replace
                arg1 = arg1.replace(item, dictionary[item])
                # return updated string
        return arg1
    else:
        return arg1

def translation(data):
    if(type(data) is list):
        return [trans(el) for el in data]
    else:
        return trans(data)


from trans import trans
print(trans)
lista1 = ['ŠKODA', 'Citroën', 'Żuk', 'Wałga']
print(find_replace(lista1))
print(translation(lista1))










    