"""Some miscelaneous helper functions."""
import numpy as np
from lmfit import Parameters, models


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

    # We return the fit report, as well as a fit to draw
    fit_Vs = np.linspace(min(Vs), max(Vs), 60)
    fit_Is = I(fit_Vs, **result.best_values)

    return result.fit_report(), (fit_Vs, fit_Is)

Vs = [5.719354838709678, 5.7064516129032254, 5.658064516129032, 5.64516129032258, 5.619354838709677, 5.541935483870968, 5.509677419354839, 5.422580645161291, 5.2935483870967746, 5.164516129032258, 4.619354838709677, 3.5387096774193543, 2.4, 1.5709677419354837, 0.8483870967741935, 0.5064516129032258, 0.25483870967741934, 0.16129032258064516, 0.15483870967741936, 0.11290322580645162, 0.08064516129032258, 0.08709677419354839, 0.08387096774193548]
dVs = [0.02090561515615439, 0.022809896167307962, 0.024139725075960856, 0.018247916933846434, 0.032896900087695205, 0.00912395846692306, 0.016448450043847672, 0.012069862537980577, 0.028489551181702613, 0.004561979233461844, 0.04351850826849044, 0.016448450043847672, 0.1094875016030783, 0.03193385463423125, 0.016448450043847734, 0.08070965163352775, 0.0277494363452988, 0.019885206461190245, 0.020905615156154383, 0.01988520646119024, 0.016448450043847693, 0.020905615156154383, 0.04762846148462387]
Is = [0.0034317089910775563, 0.003660489590482727, 0.004575611988103408, 0.006177076183939602, 0.007778540379775795, 0.006405856783344772, 0.006405856783344772, 0.0075497597803706245, 0.009151223976206817, 0.012811713566689543, 0.009380004575611988, 0.011210249370853353, 0.010066346373827499, 0.01990391214824983, 0.012125371768474032, 0.01098146877144818, 0.010295126973232668, 0.010295126973232671, 0.01098146877144818, 0.010523907572637839, 0.010295126973232668, 0.011439029970258521, 0.01075268817204301]
dIs = [0.0, 0.0003235446264866382, 0.00032354462648663784, 0.004376830581036145, 0.0027643665004791975, 0.0014102983305808688, 0.0008560186197149261, 0.0005603957315907525, 0.0012941785059465522, 0.004054002550141695, 0.0006470892529732757, 0.0006470892529732764, 0.0003235446264866382, 0.0135888743124388, 0.00413074126864969, 0.0, 0.0005603957315907525, 0.0005603957315907525, 0.0005603957315907525, 0.0003235446264866382, 1.4763604050866443e-18, 0.0006470892529732764, 0.0003235446264866382]
fit_phase_diagram(Vs, dVs, Is, dIs)



