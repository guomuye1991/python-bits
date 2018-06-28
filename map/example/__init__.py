def outer():
    global name
    name = "gmy"

    def inner():
        global name
        name = "789"
        print(name)

    return inner



f = outer()
f()

print(name)
