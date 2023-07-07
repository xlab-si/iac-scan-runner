import random
print("Hello world!")

def increment(x):
    x = x + 1
    return x

increment(randInt(0,9))
print(increment(randInt(0,9)))

a = 2
string = "This is a string, this is an int: " + str(increment(8))
for i in range(10):
    for j in range(10):
        a += 1

this_is_a_list = ["foo", 1, 2, [3, 4, "bar"]]
print("a")