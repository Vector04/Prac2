"""Some miscelaneous helper functions."""
import numpy as np
from lmfit import Parameters, models
from scipy import optimize

def power(x):
    """Returns superscripted versions of input string x."""
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


def formatter(val, error):
    """Returns a formatted version to represent val ± error with the correct significance.
    """
    # It may have been neater to create a floatE object as defined in data_analysis_tools.py, but the current solution increases compatibility.

    # Handling some special cases
    if error == 0:
        return f"{val} \u00B1 0"

    if val == 0:
        val_order = 0
    else:
        val_order = int(np.floor(np.log10(abs(val))))
    error_order = int(np.floor(np.log10(error)))

    if abs(val_order) >= 4:  # We use compounded scientific notation
        f_val = val / 10**val_order
        f_error = error / 10**val_order
        format_arg = f".{val_order - error_order+1}f"
        return f"({f_val:{format_arg}} \u00B1 {f_error:{format_arg}})\u00B710{power(val_order)}"
    else:
        if error_order <= 0:  # We use decimal notation
            format_arg = f".{abs(error_order) + 1}f"
            return f"{val:{format_arg}} \u00B1 {error:{format_arg}}"
        # Proper formatting either as default or too hard
        return f"{val} \u00B1 {error}"



def fit_phase_diagram(Vs, dVs, Is, dIs):
    """Fits the Give V and I data. Returns a fit report, max power voltage and fitted Vs and Is."""
    dIs = np.array(dIs)
    dIs[dIs == 0] = 1

    def I(U, I_L=0.1, I_0=-25):
        e = 1.6e-19
        k = 1.23e-23
        T = 300
        I1 = I_L - (10**I_0) * (np.exp((e * U) / (5 * k * T)))
        I1[I1 < 0] = 0
        return I1
    
    UIModel = models.Model(I)
    params = Parameters()
    # add with tuples: (NAME VALUE VARY MIN  MAX  EXPR  BRUTE_STEP)
    params.add_many(('I_L', 0.02, True, 0, 1, None, 0.0005), ('I_0', -23, True, None, -3, None, 0.01))
    result = UIModel.fit(Is, 
                         params=params, 
                         U=Vs, 
                         weights=1/np.array(dIs))

    best_params = result.best_values
    # We return the fit report, as well as a fit to draw
    fit_Vs = np.linspace(min(Vs), max(Vs), 60)
    fit_Is = I(fit_Vs, **best_params)


    # Also, we want to find the voltage for maximum power
    def P(U):
        return -U * I(U, **best_params)

    U_max = optimize.fmin(P, x0=5.5, maxfun=None)[0]

    return result.fit_report() + f"\n\n Voltage for max power: {U_max} V", (fit_Vs, fit_Is)


class Queue:
    def __init__(self, length):
        self._length = length
        self.data = []
        self.pointer = 0 # The first item in the queue, gets deleted upon additional entry

    def add(self, entry):
        if len(self.data) == self._length:
            self.data[self.pointer] = entry
            self.pointer += 1
            self.pointer %= self._length
        else:
            self.data.append(entry)

    def __len__(self):
        return min(len(self.data), self._length)

    def __str__(self):
        return str(self.data[self.pointer:] + self.data[:self.pointer])

    def to_array(self):
        return self.data[self.pointer:] + self.data[:self.pointer]

