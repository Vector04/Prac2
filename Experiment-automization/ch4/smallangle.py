import numpy as np 
import click

@click.group()
def cli():
    pass


def sin(x, n=10):
    return np.sin(np.linspace(0, 2 * np.pi, n))


def tan(x, n=10):
    return np.tan(np.linspace(0, 2 * np.pi, n))

@cli.command()
# @click.option('--epsilon', default=0.1, type=float, help="This is my help message.")
@click.argument('epsilon', type=float)
def approx(epsilon):
    x = 0
    while True:
        if x - np.sin(x) >= epsilon:
            click.echo(round(x, 3))
            return
        else:
            x += 0.001

