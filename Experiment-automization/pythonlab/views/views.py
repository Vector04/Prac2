"""Contains functions to create a command-line tool, evokes functions from pythonlab.model."""


import click
from pythonlab.models.models import *
from pythonlab.views.helpers import formatter


@click.group()
def cli():
    pass

@cli.command()
@click.option('-s', '--search', default='', type=str, help='The search query.')
def list(search):
    """Shows all connected devices.
    You can search for specific devices by also passing a search query.
    """
    resources = DiodeExperiment.get_resources(search)

    # Checking whether there are any results at all
    found = False
    for resource in resources:
        click.echo(resource)
        found = True

    # Message if there are no results
    if not found:
        click.echo(f"No devices found with '{search}'!")

@cli.command()
@click.argument('port')
def info(port):
    """Shows information of a particular device.
    The appropiate PORT can be found using the list command.
    """
    info = DiodeExperiment.get_info(port)
    # Exception handling if we cannot get any information
    if info is None:
        click.echo(f"Cannot get info of '{port}'!")
    else:
        click.echo(info) 

@cli.command()
@click.argument('voltage')
@click.option('-c', '--count', default=1, type=int, help='Repetions of measurement')
def measure(voltage, count):
    """Measures current through diode after applying given voltage.

    Also returns uncertainty of the measurement. The measurement is repeated [count] times.
    """
    current, dcurrent = DiodeExperiment.get_current(voltage, count)
    # Neatly presenting measurement result with the help of the 
    # helpers.formatter() function
    click.echo(f"{formatter(current, dcurrent)} A")


@cli.command()
@click.option('-vmi', type=float, default=0, help='The lowerbound of the voltage scanning range.') 
@click.option('-vma', type=float, default=3, help='The upperbound of the voltage scanning range.')
@click.option('-n', default=15, type=int, help='The amount of voltages in scanning range.')
@click.argument('out', type=click.File('w'), default='-', required=False)
def scan(vmi, vma, n, out):
    """Measures voltage across diode after applying a range of voltages.
    This range consists of [n] (default 15) points between [vmi] and [vmax].
    The resulting voltages can be shown to the console if [OUT] is left blank,
    or can be written to a file, specified with [OUT].
    """
    for i, voltage in enumerate(DiodeExperiment.get_voltages(vmi, vma, n)):
        click.echo(f"{i},{voltage}", file=out)