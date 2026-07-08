alist = [123, 44, 22]


gen = (item for item in alist)
set_com = {item for item in alist}
dict_com = {key:value for key , value in enumerate(alist)}
print(dict_com)
print(next(gen))
print(next(gen))