from pabutools.election import parse_pabulib
from pabutools.election import write_pabulib
from pabutools.election import Project, ApprovalBallot, ApprovalProfile, Cost_Sat, Instance
from collections import defaultdict
import os
import matplotlib.pyplot as plt
from pabutools.rules import greedy_utilitarian_welfare
from pabutools.rules import method_of_equal_shares

def load_instance(file):

    instance, profile = parse_pabulib(file)

    return instance, profile


def calc_outcomes(instance, profile):
    outcome_MES = method_of_equal_shares(instance, profile.as_multiprofile(), sat_class=Cost_Sat, voter_budget_increment=1)
    outcome_greedy = greedy_utilitarian_welfare(instance, profile.as_multiprofile(), sat_class=Cost_Sat)

    return outcome_MES, outcome_greedy


def cost_over_budget(instance,outcome, ratio):
    for p in instance:
        if p in outcome:
            ratio.append(int(instance.project_meta[p]['votes'])/int(instance.meta['num_votes']))

    return ratio


#####
# calculates the ratio of project votes/possible approvals
# for both greedy and MES
#####
def sel_popular(filename, ratio_sel_greedy, ratio_sel_MES):
    instance, profile = load_instance(filename)
    outcome_MES, outcome_greedy = calc_outcomes(instance, profile)

    ratio_sel_greedy = cost_over_budget(instance, outcome_greedy, ratio_sel_greedy)

    ratio_sel_MES = cost_over_budget(instance, outcome_MES, ratio_sel_MES)


    return ratio_sel_greedy, ratio_sel_MES


##### 
# plots and saves the calculated ratios
#####
def plot_histogram(ratio_sel_greedy, ratio_sel_MES, folder_path):
 
    plt.hist([ratio_sel_greedy, ratio_sel_MES], bins=10, color=['blue', 'orange'], label=['Greedy', 'MES'], alpha=0.7)

    plt.xlabel('Project Votes/Possible Approvals')
    plt.ylabel('Frequency')
    plt.title('Selected Project Votes/Possible Approvals: Greedy vs MES')
    plt.legend()
    
    file_path = os.path.join(folder_path, "greedy_vs_mes_histogram_appr_sel.png")
    plt.savefig(file_path)
    plt.close()


#####
# calculates and plots the ratio of project votes/possible approvals
# for all files in a given folder
#####
def process_all_files_in_folder(folder_path):

    ratio_sel_greedy = []
    ratio_sel_MES = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        sel_popular(file_path, ratio_sel_greedy, ratio_sel_MES)

    plot_histogram(ratio_sel_greedy, ratio_sel_MES, folder_path)