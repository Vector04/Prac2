import sys
from io import TextIOWrapper
import numpy as np
from scipy import optimize
import time 

sys.stdout = TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace')



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


# The firstidea: Create a custom class with (val, error) as attributes.
# We will need to make a new version of curve_fit, etc.
# Can we enherit this class from np.float? or even regular float?
# Add units?
# Numpy testing (sqrt for example)
# Fix str() for 3 ± 0.9, fix str() for large relaive erors (710.47 pm 1.7e2)
# Use isinstance?
# pandas columns, np arrays? Would be very cool if this worked
# add dundermethod like iadd, etc (inplace operations)

class floatE:
    """This class implements 'float' class with errors. Also does error propagation during the 
    arithmetic operations +, -, *, /, **.
    """

    def __init__(self, val, error):
        assert error >= 0, f"The error ({error}) must be greater than 0!"
        self.val = val
        self.error = error

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        val_order = int(np.log10(abs(self.val)))
        error_order = int(np.log10(self.error))
        d_order = val_order - error_order
        if val_order >= 4:
            f_val = self.val / 10**val_order
            f_error = self.error / 10**val_order
            format_arg = f".{d_order+1}f"
            return f"({f_val:{format_arg}} \u00B1 {f_error:{format_arg}})\u00B710{power(val_order)}"
        else:
            format_arg = f".{abs(error_order)+3}g"
            return f"{self.val:{format_arg}} \u00B1 {self.error:.2g}"

    def __add__(self, a):
        try:
            return floatE(self.val + a.val, self.error + a.error)
        except AttributeError:
            return floatE(self.val + a, self.error)

    def __radd__(self, a):
        return floatE(self.val + a, self.error)

    def __sub__(self, a):
        try:
            if self is a:
                return floatE(0,0)
            return floatE(self.val - a.val, self.error + a.error)
        except AttributeError:
            return floatE(self.val - a, self.error)

    def __rsub__(self, a):
        return floatE(self.val - a, self.error)

    def __mul__(self, a):
        try:
            return floatE(self.val * a.val, np.sqrt((self.val * a.error)**2 + (a.val * self.error)**2))
        except AttributeError:
            return floatE(self.val * a, self.error * a)

    def __rmul__(self, a):
        return floatE(self.val * a, self.error * abs(a))

    def __truediv__(self, a):
        try:
            return floatE(self.val / a.val, np.sqrt((self.error / a.val)**2 + (self.val * a.error / a.val**2)**2))
        except AttributeError:
            return floatE(self.val / a, self.error / a)

    def __rtruediv__(self, a):
        return floatE(a / self.val, a * self.error / self.val**2)

    def __pow__(self, a):
        try:
            error = np.sqrt((a.val * self.val**(a.val - 1) * self.error) **
                            2 + (np.log(self.val) * self.val**a.val * a.error) ** 2)
            return floatE(self.val**a.val, error)
        except AttributeError:  # `a` is a regular float
            return floatE(self.val**a, a * self.val * (a - 1) * self.error)

    def __rpow__(self, a):  # a^self
        return floatE(a ** self.val, abs(np.log(a) * a**self.val * self.error))


def val(x):
    if isinstance(x, floatE):
        return x.val
    return x


def error(x):
    if isinstance(x, floatE):
        return x.error
    return 0


