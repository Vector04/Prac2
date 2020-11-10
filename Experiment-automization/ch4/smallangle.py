import numpy as np 
import click

def sin(x, n=10):
    return np.sin(np.linspace(0, 2 * np.pi, n))


def tan(x, n=10):
    return np.tan(np.linspace(0, 2 * np.pi, n))

@click.command()
@click.argument('epsilon', required=True, type=float)
def approx(epsilon):
    x = 0
    while True:
        if x - np.sin(x) >= epsilon:
            click.echo(round(x, 3))
            return
        else:
            x += 0.001


if __name__ == '__main__':
    approx()
