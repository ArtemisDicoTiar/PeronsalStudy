def my_utility(a, b):
    # ...
    pass

def first_func():
    for _ in range(1000):
        my_utility(4, 5)

def second_func():
    for _ in range(10):
        my_utility(1, 3)

def my_program():
    for _ in range(20):
        first_func()
        second_func()

from cProfile import Profile
from pstats import Stats

profiler = Profile()
profiler.runcall(my_program)

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')

# cannot recognize which calls which
stats.print_stats()

# can recognize which calls which
stats.print_callers()
