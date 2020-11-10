import numpy as np
from scipy import optimize
import inspect

fix_ascii = True


def _fix_ascii():
    import sys
    from io import TextIOWrapper
    sys.stdout = TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace')


if fix_ascii:

    _fix_ascii()


def power(x):
    superscipt_dict = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
        "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻"}
    power_string = ""
    for s in str(x):
        try:
            power_string += superscipt_dict[s]
        except KeyError:  # Some ugly weirdness
            power_string += "⁻"
    return power_string


def chi_squared(f, xs, ys, errors):
    return sum([((y - f(x)) / error)**2 for x, y, error in zip(xs, ys, errors)])


class ParamDict(dict):
    def __repr__(self):
        total_str = ""
        for name, param in self.items():
            total_str += f"{name} = {str(param)}\n"
        return total_str[:-1]


def val(x):
    if isinstance(x, floatE):
        return x.val
    return x


def error(x):
    if isinstance(x, floatE):
        return x.error
    return 0


class floatE:
    """This class implements 'float' class with errors. Also does uncorrelated error propagation during the
    arithmetic operations +, -, *, /, **.
    """

    def __init__(self, val, error):
        assert error >= 0, f"The error ({error}) must be greater than 0!"
        self.val = val
        self.error = error

    def __repr__(self):
        # return f"floatE({self.val}, {self.error})"
        return str(self)

    def __str__(self):
        val_order = int(np.floor(np.log10(abs(self.val))))
        error_order = int(np.floor(np.log10(self.error)))
        if abs(val_order) >= 4:  # compounded scientific notation
            f_val = self.val / 10**val_order
            f_error = self.error / 10**val_order
            format_arg = f".{val_order - error_order+1}f"
            return f"({f_val:{format_arg}} \u00B1 {f_error:{format_arg}})\u00B710{power(val_order)}"
        else:
            if error_order <= 0:  # Decimal formattig
                format_arg = f".{abs(error_order) + 1}f"
                return f"{self.val:{format_arg}} \u00B1 {self.error:{format_arg}}"
            if error_order <= 2:  # Integer formatting
                return f"{self.val:.0f} \u00B1 {self.error:.0f}"
            # Proper formatting either as default or too hard
            return f"{self.val} \u00B1 {self.error}"

    def LaTeXify(self):
        val_order = int(np.floor(np.log10(abs(self.val))))
        error_order = int(np.floor(np.log10(self.error)))
        if abs(val_order) >= 4:  # compounded scientific notation
            f_val = self.val / 10**val_order
            f_error = self.error / 10**val_order
            format_arg = f".{val_order - error_order+1}f"
            return (rf"({f_val:{format_arg}} \pm {f_error:{format_arg}}) \cdot 10^"
                    + "{" + rf"{val_order}" + "}")
        else:
            if error_order <= 0:  # Decimal
                format_arg = f".{abs(error_order) + 1}f"
                return rf"{self.val:{format_arg}} \pm {self.error:{format_arg}}"
            # Proper formatting iether as default or too hard
            return rf"{self.val} \pm {self.error}"

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
            return floatE(self.val**a, abs(a * self.val * (a - 1) * self.error))

    def __rpow__(self, a):  # a^self
        return floatE(a ** self.val, abs(np.log(a) * a**self.val * self.error))


def better_curve_fit(f, xdata, ydata, p0=None, sigma=None, **kwargs):
    """
    A modified version of curve_fit which returns more useful information.
    Returns:
        - params: a dictionary of paramters in the form of {param_name: value pm error}
        - chi2: The overal χ^2, assuming a sigma has been given.

    """
    popt, pcov = optimize.curve_fit(
        f, xdata, ydata, p0=p0, sigma=sigma, **kwargs)
    argspec = inspect.getfullargspec(f)
    params = ParamDict({param: floatE(val, error)
                        for param, val, error in zip(argspec[0][1:], popt, np.sqrt(np.diag(pcov)))})
    if sigma.any():
        chi2 = chi_squared(lambda x: f(x, *popt), xdata, ydata,
                           sigma) / (len(xdata) - len(popt))
        return params, chi2
    return params
