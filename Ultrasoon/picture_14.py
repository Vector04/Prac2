import numpy as np
import pandas as pd
import os

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal
import click

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.sans-serif": ["Computer Modern Roman"],
    "font.size": 12,
    "font.weight": 600,
})

# folder = 'meting3/'


# @click.command()
# @click.argument('folder', type=str)
def make_image(folder):
    """Make an image using all the data in `folder'.

        FOLDER should be in the form of `metingX/', with X an integer.
    """
    # if '.csv' in [os.path.splitext(file)[1] for file in os.listdir(folder)]:
    #     df = pd.read_csv(f'{folder}data.csv')
    #     df_temp = df['t', df.columns[0]]
    #     # df.drop(["Unnamed: 0", "t"], index=1, inplace=True)
    #     df.drop(["Unnamed: 0", "t"], axis=1, inplace=True)
    #     xs = [float(x) for x in df.columns]
    #     x_start, x_end = min(xs), max(xs)
    #     stepsize = xs[1] - xs[0]


    # else:
    # Getting basic data about the image
    xs = sorted([float(os.path.splitext(file)[0])
                 for file in os.listdir(folder) if os.path.splitext(file)[1] == '.txt'])
    x_start, x_end = min(xs), max(xs)
    stepsize = xs[1] - xs[0]

    #plt.rcParams["font.family"] = "Helvetica"

    df = pd.DataFrame()

    # Loading data
    for x in np.arange(x_start, x_end + stepsize, stepsize):

        df_temp = pd.read_csv(f"{folder}{x:.6f}.txt", sep='\t', header=None)

        # Initial processing
        df[f'{x}'] = np.abs(signal.hilbert(df_temp[1] - 127))

    print(df.columns)
    # Timed points to distance conversion
    total_y_points = len(df[f"{xs[0]:.1f}"])

    total_time = (df_temp.iloc[-1, 0] - df_temp.iloc[0, 0]) / 1000  # s
    velocity = 1500  # m/s
    total_distance_y = total_time * velocity * 1000  # mm

    # Creating our picture
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    plt.tight_layout()
    ax1.imshow(df)

    # Proper fomatting
    delta_x = x_end - x_start

    ax1.set_aspect(1.5 * total_distance_y / total_y_points)
    ax1.set_xlim(delta_x / stepsize, 0)
    ax1.invert_yaxis()

    ticks_y = ticker.FuncFormatter(
        lambda y, pos: f"{(y / total_y_points *  total_distance_y):.0f}")
    ax1.yaxis.set_major_formatter(ticks_y)

    ticks_x = ticker.FuncFormatter(
        lambda x, pos: f"{((x*stepsize) + x_start):.0f}")
    ax1.xaxis.set_major_formatter(ticks_x)

    ax1.set_title("Image")
    ax1.set_xlabel(r'Horizontal distance $x\ (mm)$')
    ax1.set_ylabel(r"Depth $y\ (mm)$")


    ys = [sum(df[x]) for x in df.columns]
    ax2.plot(xs, ys, c='#2190eb')
    ax2.set_xlim(x_end, x_start)
    ax2.set_aspect(0.012)

    ax2.set_title("Total Amplitude")
    ax2.set_xlabel(r"Horizontal distance $x\ (mm)$")
    ax2.set_ylabel("Total Amplitude (V)")

    plt.show()


if __name__ == '__main__':
    # Change this later!
    make_image("meting14/")
