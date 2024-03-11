import matplotlib.pyplot as plt
import json
import numpy as np

fnames = ['cwnd.json','loss.json','rtt.json','throughput.json']
def run(filename):
    # Load the JSON data
    with open(filename) as f:
        data = json.load(f)

    species = data['scenarios']
    penguin_means = data['values']

    x = np.arange(len(species))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in penguin_means.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(data['ylabel'])
    # ax.set_title('Algorithm Performance')
    ax.set_xticks(x + width, species)
    ax.legend(loc='upper left', ncols=3)
    ax.set_ylim(data['ylim_low'],data['ylim_high'])
    # Turn on the grid
    # Modify the grid style
    ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    # Save the plot to the current directory
    plt.savefig(data['save_name'])

if __name__ == '__main__':
    for fname in fnames:
        run(fname)