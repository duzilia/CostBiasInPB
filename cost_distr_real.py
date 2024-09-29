from pabutools.election import parse_pabulib
from pabutools.election import write_pabulib
from pabutools.election import Project, ApprovalBallot, ApprovalProfile, Cost_Sat, Instance
from collections import defaultdict
import os
import matplotlib.pyplot as plt
import numpy as np

#####
# loads instance from pb-file
#####
def load_instance(file):

    instance, profile = parse_pabulib(file)

    return instance, profile

#####
# returns lists of costs and percentage of budget that cost is
#####
def fill_arrays(file_path, costs, costs_budget):
    instance, profile = load_instance(file_path)

    for p in instance:
        costs.append(int(instance.project_meta[p]['cost']))
        costs_budget.append(int(instance.project_meta[p]['cost'])/int(instance.budget_limit))

    return costs, costs_budget

#####
# creates and saves frequency analysis of cost distribution
#####
def plot_histogram(data, title, filename, output_dir, ratio):

    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=30, density=True, alpha=0.6, color='g', edgecolor='black')

    mean = np.mean(data)
    std_dev = np.std(data)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std_dev) ** 2)
    plt.plot(x, p, 'k', linewidth=2)
    
    plt.title(title)
    if ratio is True:
        plt.xlabel('Project Cost/Budget')
    else:
        plt.xlabel('Project Cost')
    plt.ylabel('Frequency')

    plt.savefig(os.path.join(output_dir, filename))
    plt.close()