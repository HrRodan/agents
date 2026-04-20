from functools import partial, lru_cache, wraps, singledispatch

# 1. @lru_cache: Memoization to speed up expensive/recursive calls
@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 2. @wraps: Preserve metadata of the original function when decorating
def simple_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(f"Calling function: {f.__name__}")
        return f(*args, **kwargs)
    return wrapper

@simple_decorator
def greet(name):
    """Greets the user."""
    return f"Hello, {name}!"

# 3. partial: Freeze some arguments of a function
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

# 4. @singledispatch: Function overloading based on the first argument type
@singledispatch
def process(data):
    print(f"Generic processing: {data}")

@process.register(int)
def _(data):
    print(f"Processing an integer: {data + 10}")

@process.register(list)
def _(data):
    print(f"Processing a list of length: {len(data)}")

if __name__ == "__main__":
    print("--- lru_cache example ---")
    print(f"Fibonacci(30): {fibonacci(30)}")
    print(fibonacci.cache_info())

    print("\n--- wraps example ---")
    print(greet("Alice"))
    print(f"Function Name: {greet.__name__}")
    print(f"Docstring: {greet.__doc__}")

    print("\n--- partial example ---")
    print(f"5 squared: {square(5)}")
    print(f"2 cubed: {cube(2)}")

    print("\n--- singledispatch example ---")
    process("Hello")
    process(100)
    process([1, 2, 3])
