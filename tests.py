qwe= {'qwe ] asd ] 123': 123}

print(list(qwe.keys())[0].split(' ] '))

print((list(qwe.keys())[0].split(' ] '))[0])

print(qwe.values())
# print(qwe.get(qwe.keys()))

print(list(qwe.values())[0])


# from queue import Queue

# print('asd')

# asd = Queue(maxsize=3)

# asd.put(1)
# asd.put(2)
# asd.put(3)

# print(asd.get())
# print(asd.get())
# print(asd.get())

# # a = (asd.get(block=False))
# # print(type(a))

# try:
#     a = (asd.get(block=False))
#     print(type(a))
# except Exception as e:
#     print('asdf')
#     print(e)
