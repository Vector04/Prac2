import click
from pythonlab.models.models import *

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

def formatter(val, error):
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

    if error == 0:
        return f"{val} \u00B1 0"
    val_order = int(np.floor(np.log10(abs(val))))
    error_order = int(np.floor(np.log10(error)))
    if abs(val_order) >= 4:  # compounded scientific notation
        f_val = val / 10**val_order
        f_error = error / 10**val_order
        format_arg = f".{val_order - error_order+1}f"
        return f"({f_val:{format_arg}} \u00B1 {f_error:{format_arg}})\u00B710{power(val_order)}"
    else:
        if error_order <= 0:  # Decimal
            format_arg = f".{abs(error_order) + 1}f"
            return f"{val:{format_arg}} \u00B1 {error:{format_arg}}"
        # Proper formatting either as default or too hard
        return f"{val} \u00B1 {error}"


@click.group()
def cli():
    pass

@cli.command()
@click.option('-s', '--search', default='', type=str, help='The search query.')
def list(search):
    resources = DiodeExperiment.get_resources(search)
    found = Falset
    for resource in resources:
        click.echo(resource)
        found = True
    if not found:
        click.echo(f"No devices found with '{search}'!")

@cli.command()
@click.argument('port')
def info(port):
    info = DiodeExperiment.get_info(port)
    if info is None:
        click.echo(f"Cannot get info of '{port}'!")
    else:
        click.echo(info) 

@cli.command()  
@click.argument('voltage')
@click.option('-c', '--count', default=1,type=int, help='Repetions of measurement')
def measure(voltage, count):
    current, dcurrent = DiodeExperiment.get_current(voltage, count)
    click.echo(f"{formatter(current, dcurrent)} A")


@cli.command()
@click.option('-vmi', type=float) 
@click.option('-vma', type=float)
@click.argument('out', type=click.File('w'), default='-', required=False)
def scan(vmi, vma, out):
    for i, voltage in enumerate(DiodeExperiment.get_voltages(vmi, vma)):
        click.echo(f"{i},{voltage}", file=out)