import os
import csv
from pabutools.election import parse_pabulib
from pabutools.rules import greedy_utilitarian_welfare, method_of_equal_shares
import scipy.stats as stats
from collections import defaultdict
from pabutools.election import Project, ApprovalBallot, ApprovalProfile, Cost_Sat, Instance

def fill_outcome_array(instance, outcome):
    in_outcome = []
    for project in instance.project_meta:
        if project in outcome:
            in_outcome.append(1)
        else:
            in_outcome.append(0)
    return in_outcome


def calc_budget_perc(instance):
    budget = instance.budget_limit
    budget_perc = []
    for project in instance.project_meta:
        cost = int(instance.project_meta[project]['cost'])
        budget_perc.append(cost / budget)
    return budget_perc


def calc_votes_perc(sorted_counts, num_votes):
    return [votes / num_votes for votes in sorted_counts.values()]


def calc_differences(budget_perc, votes_perc):
    return [budget - votes for budget, votes in zip(budget_perc, votes_perc)]


#####
# calculates the outcomes for a given instance
# calculates the pbc values from that
#####
def calc_pbc(profile, instance, sorted_counts, num_votes):
    in_outcome_MES = []
    in_outcome_greedy = []
    budget_perc = []
    votes_perc = []
    
    outcome_MES = method_of_equal_shares(instance, profile.as_multiprofile(), sat_class=Cost_Sat, voter_budget_increment=1)
    outcome_greedy = greedy_utilitarian_welfare(instance, profile.as_multiprofile(), sat_class=Cost_Sat)
    
    in_outcome_MES = fill_outcome_array(instance, outcome_MES)
    in_outcome_greedy = fill_outcome_array(instance, outcome_greedy)
    budget_perc = calc_budget_perc(instance)
    votes_perc = calc_votes_perc(sorted_counts, num_votes)
    diff = calc_differences(budget_perc, votes_perc)

    in_outcome_MES = list(map(float, in_outcome_MES))
    in_outcome_greedy = list(map(float, in_outcome_greedy))
    budget_perc = list(map(float, budget_perc))
    diff = list(map(float, diff))
    
    stat_val_MES_diff, p_val_MES_diff = stats.pointbiserialr(in_outcome_MES, diff)
    stat_val_greedy_diff, p_val_greedy_diff = stats.pointbiserialr(in_outcome_greedy, diff)
    
    stat_val_MES_budget, p_val_MES_budget = stats.pointbiserialr(in_outcome_MES, budget_perc)
    stat_val_greedy_budget, p_val_greedy_budget = stats.pointbiserialr(in_outcome_greedy, budget_perc)
    
    return (
        stat_val_greedy_budget, p_val_greedy_budget, 
        stat_val_MES_budget, p_val_MES_budget, 
        stat_val_greedy_diff, p_val_greedy_diff, 
        stat_val_MES_diff, p_val_MES_diff
    )


#####
# for all instances in a given folder
# calculate outcomes and pbc values
# save in csv
#####
def process_election_instances(folder_path, output_csv):
    files = sorted([f for f in os.listdir(folder_path) if f.endswith('.pb')])

    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            'var', 
            'stat_val_greedy_budget', 'p_val_greedy_budget', 
            'stat_val_MES_budget', 'p_val_MES_budget', 
            'stat_val_greedy_diff', 'p_val_greedy_diff', 
            'stat_val_MES_diff', 'p_val_MES_diff'
        ])

        for file in files:
            var = file.split('_')[-1].split('.')[0]
            instance_file = os.path.join(folder_path, file)
            instance, profile = parse_pabulib(instance_file)
            num_votes = profile.num_ballots()
            sorted_counts = defaultdict(int)

            for number_set in profile:
                for number in number_set:
                    sorted_counts[number] += 1
            
            results = calc_pbc(profile, instance, sorted_counts, num_votes)
            
            csvwriter.writerow([var] + list(results))

            print(file)