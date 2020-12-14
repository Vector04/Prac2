import numpy as np
import pandas as pd
import os

from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal
import click


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
    fig, ax = plt.subplots()
    ax.imshow(df)

    # Proper fomatting
    delta_x = x_end - x_start

    ax.set_aspect(3*total_distance_y / total_y_points)
    ax.set_xlim(delta_x / stepsize, 0)
    ax.invert_yaxis()

    ticks_y = ticker.FuncFormatter(
        lambda y, pos: f"{(y / total_y_points *  total_distance_y):.0f}")
    ax.yaxis.set_major_formatter(ticks_y)

    ticks_x = ticker.FuncFormatter(
        lambda x, pos: f"{((x*stepsize) + x_start):.0f}")
    ax.xaxis.set_major_formatter(ticks_x)

    plt.suptitle(f"Afbeelding meting {folder[6:-1]}", fontsize=16)
    plt.xlabel(r'Horizontal distance $x\ (mm)$')
    plt.ylabel(r"Depth $y\ (mm)$")

    plt.savefig(f"{folder}picture.png")

    # Save dataframe
    df['t'] = df_temp[0]
    df.to_csv(f'{folder}data.csv')

    plt.show()


if __name__ == '__main__':
    # Change this later!
    make_image("meting14/")
