import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Plotter:

    def __init__(self, plot_dir="./plots"):
        self.plot_dir = plot_dir
        # Remove trailing slash to ensure consistency
        if self.plot_dir[-1] == "/":
          self.plot_dir = self.plot_dir[:-1]

    def correlation_plot(self, dataframe, variables):
        corr = dataframe.corr()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cax = ax.matshow(corr, cmap='seismic', vmin=-1, vmax=1)
        fig.colorbar(cax)
        ticks = np.arange(0, len(variables), 1)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(variables, rotation='vertical')
        ax.set_yticklabels(variables)
        plt.savefig("{0}/corr.png".format(self.plot_dir))
