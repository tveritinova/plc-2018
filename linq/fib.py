from linq import linq

def fib_gen():
    a, b = 1, 1
    while True:
        yield a
        a, b = b, a + b

print (linq(fib_gen()) \
    .Where(lambda x: x % 3 == 0) \
    .Select(lambda x: x ** 2 if x % 2 else x) \
    .Take(5) \
    .ToList())