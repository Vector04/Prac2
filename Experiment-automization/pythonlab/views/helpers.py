"""Some miscelaneous helper functions."""
import numpy as np

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