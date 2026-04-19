import functools
import time

# 1. Using @functools.lru_cache to memoize a recursive function
@functools.lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 2. Using functools.partial to create a pre-configured function
def power(base, exponent):
    return base ** exponent

square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)

# 3. Using functools.singledispatch for type-based function overloading
@functools.singledispatch
def format_data(data):
    return f"Generic: {data}"

@format_data.register(int)
def _(data):
    return f"Integer: {data}"

@format_data.register(list)
def _(data):
    return f"List of length {len(data)}: {', '.join(map(str, data))}"

# 4. Using @functools.wraps to preserve metadata in a decorator
def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}...")
        return func(*args, **kwargs)
    return wrapper

@logger
def say_hello(name):
    """Greets the user."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("--- 1. LRU Cache (Fibonacci) ---")
    start = time.perf_counter()
    result = fibonacci(35)
    end = time.perf_counter()
    print(f"Fibonacci(35) = {result} (Time: {end - start:.6f}s)")
    print(f"Cache Performance: {fibonacci.cache_info()}\n")

    print("--- 2. Partial Functions ---")
    print(f"Square of 5: {square(5)}")
    print(f"Cube of 5: {cube(5)}\n")

    print("--- 3. Single Dispatch ---")
    print(format_data(42))
    print(format_data([1, 2, 3]))
    print(format_data("Hello")) # Generic fallback
    print("")

    print("--- 4. Wraps Decorator ---")
    print(say_hello("World"))
    print(f"Function Name: {say_hello.__name__}")
    print(f"Function Docstring: {say_hello.__doc__}")
