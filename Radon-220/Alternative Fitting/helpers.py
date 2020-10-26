import time


def timeit(function):
    def timed(*args, **kwargs):
        ts = time.perf_counter_ns()
        result = function(*args, **kwargs)
        te = time.perf_counter_ns()
        print(f"{function.__name__}: {(te - ts) / 10**6} ms")
        return result

    return timed


def power(x):
    superscipt_dict = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
        "7": "⁷", "8": "⁸", "9": "⁹"}
    power_string = ""
    for s in str(x):
        power_string += superscipt_dict[s]
    return power_string


def chi_squared(f, xs, ys, errors):
    return sum([((y - f(x)) / error)**2 for x, y, error in zip(xs, ys, errors)])


class ParamDict(dict):
    def __repr__(self):
        total_str = ""
        for name, param in self.items():
            total_str += f"{name} = {str(param)}\n"
        return total_str[:-1]
