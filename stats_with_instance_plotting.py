import prefsampling.approval as ps
from pabutools.election import parse_pabulib
from pabutools.election import write_pabulib
from pabutools.election import Project, ApprovalBallot, ApprovalProfile, Cost_Sat, Instance
from collections import defaultdict
import random
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
from pabutools.rules import greedy_utilitarian_welfare
from pabutools.rules import method_of_equal_shares
import scipy.stats as stats
import copy

def get_current_datetime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


######
# creates ballots
# disjoint resampling values according to source paper
# also creates sorted counts, so that the proportionality can be calculated
######
def create_ballots(num_votes, num_projects):

    created_ballots = ps.disjoint_resampling(num_votes,num_projects,0.75,0.125,num_central_votes=4)

    number_counts = defaultdict(int)

    for number_set in created_ballots:
        for number in number_set:
            number_counts[number] += 1

    sorted_counts = dict(sorted(number_counts.items()))

    return created_ballots, sorted_counts


##### 
# creates one instance with given proportionality probability
#####
def create_cost_instance(budget, prop_prob, num_projects, sorted_counts, num_votes):

    new_instance = Instance()
    new_instance.budget_limit = budget

    for p in range(num_projects):
        p_name = "p"+str(p)
        prop_cost = int((sorted_counts[p]/num_votes)*budget)
        higher_prob = random.random()

        if higher_prob > prop_prob:
            mu = prop_cost + (budget-prop_cost)/2  # Mean of the normal distribution
            sigma = 20000  # Standard deviation of the normal distribution
            random_number = np.random.normal(mu, sigma)
            higher_cost = min(max(round(random_number), prop_cost), budget)
            project = Project(p_name, higher_cost)
            new_instance.add(project)
            helper_dict = {'cost': higher_cost}
            new_instance.project_meta.update({p_name: helper_dict}) 

        else:
            project = Project(p_name, prop_cost)
            new_instance.add(project)
            helper_dict = {'cost': prop_cost}
            new_instance.project_meta.update({p_name: helper_dict}) 

    return new_instance


######
# creates list of instances with given proportionality probability step
######
def create_list_cost_instances(num_votes, num_projects, budget, sorted_counts, num_instances, prop_prob_start, prop_prob_step):

    prop_prob = prop_prob_start
    cost_instances = []
    prop_prob_list = []

    for i in range(num_instances):
        prop_prob = prop_prob - prop_prob_step
        prop_prob_list.append(round(prop_prob,2))
        cost_instances.append(create_cost_instance(budget, prop_prob, num_projects, sorted_counts, num_votes))

    return cost_instances, prop_prob_list


#####
# creates a profile for a given instance
#####
def create_profile(created_ballots, instance):

    profile = ApprovalProfile()

    for b in created_ballots:
        ballot = ApprovalBallot()
        for project in b:
            p_name = "p"+str(project)
            ballot.add(instance.get_project(p_name))
        profile.append(ballot)


    return profile


######
# creates histogram for one instance
######
def histogramm(sorted_counts, cost_instance, num_votes, budget, save_name):

    budget_percentages = {project: (cost['cost'] / budget) * 100 for project, cost in cost_instance.project_meta.items()}
    
    votes_percentages = {"p"+str(project): (votes / num_votes) * 100 for project, votes in sorted_counts.items()}
    
    differences = [budget_percentages[project] - votes_percentages[project] for project in budget_percentages]
    
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)  
    plt.scatter(list(votes_percentages.values()), list(budget_percentages.values()))
    plt.plot([0, 100], [0, 100], color='gray', linestyle='--', label='Proportional')
    plt.xlabel('Percentage of Votes Received')
    plt.ylabel('Percentage of Budget Used')
    plt.title('Approval Votes vs. Budget Usage')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)  
    plt.hist(differences, bins=20, color='skyblue', edgecolor='black')
    plt.xlabel('Difference (Budget - Votes)')
    plt.ylabel('Number of Projects')
    plt.title('Difference between Budget and Votes Percentages')
    plt.grid(True)
    
    plt.tight_layout()
    
    plt.savefig(save_name)
    plt.close()


######
# saves histograms for all instances
######
def save_histograms(sorted_counts, cost_instances, num_votes, budget, output_dir, prop_prob_list):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for index, cost_profile in enumerate(cost_instances):

        prop_prob = prop_prob_list[index]

        histogram_name = os.path.join(output_dir,f"histogram_{index}_{prop_prob}.png")

        histogramm(sorted_counts, cost_profile, num_votes, budget, histogram_name)


#####
# creates binary list to check if something is in the outcome or not
#####
def fill_outcome_array(instance, outcome, in_outcome):

    for project in instance.project_meta:
        if project in outcome:
            in_outcome.append(1)
        else:
            in_outcome.append(0)

    return in_outcome


#####
# fills a list with the percentage of the budget each project received
#####
def calc_budget_perc(instance, budget_perc):
    budget = instance.budget_limit

    for project in instance.project_meta: 
        cost = int(instance.project_meta[project]['cost'])
        budget_perc.append(cost/budget)

    return budget_perc


#####
# fills a list with the percentage of the votes each project received
#####
def calc_votes_perc(sorted_counts, num_votes):
    
    votes_perc = []
    for i in sorted_counts:
        votes_perc.append(i/num_votes)

    return votes_perc


#####
# fills a list with the differences between budget and votes percentages
#####
def calc_differences(budget_perc, votes_perc):
    diff = []

    for i in range(len(budget_perc)):
        diff.append(budget_perc[i]-votes_perc[i])

    return diff
        

#####
# calculates outcomes
# calculates point biseral coefficients
#####
def calc_pbc(profile, instances, s_counts, num_votes):
    result_pbc_MES = []
    result_pbc_greedy = []

    sorted_counts = list(s_counts.values())

    for instance in instances:
        in_outcome_MES = []
        in_outcome_greedy = []
        budget_perc = []
        votes_perc= []
        diff = []
        
        outcome_MES = method_of_equal_shares(instance, profile.as_multiprofile(), sat_class=Cost_Sat, voter_budget_increment=1)
        
        outcome_greedy = greedy_utilitarian_welfare(instance, profile.as_multiprofile(), sat_class=Cost_Sat)

        in_outcome_MES = fill_outcome_array(instance, outcome_MES, in_outcome_MES)
        in_outcome_greedy = fill_outcome_array(instance, outcome_greedy, in_outcome_greedy)
        budget_perc = calc_budget_perc(instance, budget_perc)
        votes_perc = calc_votes_perc(sorted_counts, num_votes)

        result_pbc_MES.append(stats.pointbiserialr(in_outcome_MES, budget_perc))
        
        result_pbc_greedy.append(stats.pointbiserialr(in_outcome_greedy, budget_perc))

    return result_pbc_MES, result_pbc_greedy

#####
# plots calculated statistical values
# saves these plots
#####
def plot_coefficients(result_pbc_MES, result_pbc_greedy, output_folder, initial_probability, probability_step):
    
    statistics_MES, pvalues_MES = zip(*result_pbc_MES)
    statistics_greedy, pvalues_greedy = zip(*result_pbc_greedy)
    
    probabilities = [initial_probability - (probability_step * (i + 1)) for i in range(len(statistics_MES))]
    
    plt.figure(figsize=(10, 8))
    
    plt.subplot(3, 1, 1)
    plt.plot(probabilities, statistics_MES, label='PBC Statistical Value (MES)', color='blue')
    plt.plot(probabilities, statistics_greedy, label='PBC Statistical Value (Greedy)', color='orange')
    plt.xlabel('Probability')
    plt.ylabel('PBC Statistical Value')
    plt.title('PBC Statistical Value for Different Probabilities')
    plt.legend()
    plt.xticks(probabilities, [f'{prob:.2f}' for prob in probabilities], rotation=45)
    
    plt.subplot(3, 1, 2)
    plt.plot(probabilities, pvalues_MES, label='P-values (MES)', color='blue')
    plt.plot(probabilities, pvalues_greedy, label='P-values (Greedy)', color='orange')
    plt.xlabel('Probability')
    plt.ylabel('P-value')
    plt.title('P-values for Different Probabilities')
    plt.legend()
    plt.xticks(probabilities, [f'{prob:.2f}' for prob in probabilities], rotation=45)
    
    difference_statistics = [mes - greedy for mes, greedy in zip(statistics_MES, statistics_greedy)]
    plt.subplot(3, 1, 3)
    plt.plot(probabilities, difference_statistics, label='Difference in PBC Statistical Value (MES - Greedy)', color='green')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('Difference in PBC Statistical Value')
    plt.title('Difference in PBC Statistical Value (MES - Greedy)')
    plt.legend()
    plt.xticks(probabilities, [f'{prob:.2f}' for prob in probabilities], rotation=45)
    
    plt.tight_layout()

    coefficients_plot_path = os.path.join(output_folder, "pbc_coefficients.png")
    plt.savefig(coefficients_plot_path)
    plt.close()



def run_election_simulation(num_votes, num_projects, budget, num_profiles, prop_prob_start=1, prop_prob_step=0.025):
    # 1: create Approval Ballots and Counts for Proportionality
    created_ballots, sorted_counts = create_ballots(num_votes, num_projects)

    # 2: create all the instances with the differently proportional costs and the probability of proportionality list
    cost_instances, prop_prob_list = create_list_cost_instances(num_votes, num_projects, budget, sorted_counts, num_profiles, prop_prob_start, prop_prob_step)

    # 3: create the profile
    profile = create_profile(created_ballots, cost_instances[0])

    # 4: save histograms for the cost instances
    histograms_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "statistics", f"histograms_{get_current_datetime()}")
    os.makedirs(histograms_folder, exist_ok=True)
    save_histograms(sorted_counts, cost_instances, num_votes, budget, histograms_folder, prop_prob_list)

    # 5: save instance files
    for var in range(len(cost_instances)):
        instance_file = os.path.join(histograms_folder,f"instance_{str(var)}.pb")
        write_pabulib(cost_instances[var], profile, instance_file)
    
    # 6: calculate and plot coefficients
    result_pbc_MES, result_pbc_greedy = calc_pbc(profile, cost_instances, sorted_counts, num_votes)
    plot_coefficients(result_pbc_MES,result_pbc_greedy, histograms_folder, prop_prob_start, prop_prob_step)
