import sys
from io import TextIOWrapper
import numpy as np
from scipy import optimize

sys.stdout = TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace')

from helpers import *

# The firstidea: Create a custom class with (val, error) as attributes.
# We will need to make a new version of curve_fit, etc.
# Can we enherit this class from np.float? or even regular float?
# Add units?
# Numpy testing (sqrt for example)
# Fix str() for 3 ± 0.9, fix str() for large relaive erors (710.47 pm 1.7e2)
# Use isinstance?
# pandas columns, np arrays? Would be very cool if this worked
# add dundermethod like iadd, etc (inplace operations)

# In order to make this work for other operations, we need to monkeypatch np.sqrt.
# This is ugly, but the alternative is to modify the numpy.sqrt() function.
# We'd need to do the same thing for math.sqrt() (Eventually)
# We especially need to be VERY VERY careful when dealing with a new version of curve_fit, when that time comes.
# An important design decision now is if we want to do arrays with errors. --> Will this be useful?
# Formatin


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
