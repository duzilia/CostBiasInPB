import prefsampling.approval as ps
from pabutools.election import parse_pabulib
from pabutools.election import write_pabulib
from pabutools.election import Project, ApprovalBallot, ApprovalProfile, Cost_Sat, Instance
from collections import defaultdict
import random
import numpy as np
import os


######
# creates ballots
# disjoint resampling values according to source paper
# also creates sorted counts, so that the proportionality can be calculated
######
def create_ballots(num_votes, num_projects):

    created_ballots = ps.disjoint_resampling(num_votes,num_projects,0.75,0.125)

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


def make_instances(num_elections, num_votes, num_projects, budget, num_profiles, prop_prob_start=1, prop_prob_step=0.025):
    for e in range(num_elections):

        # 1: create Approval Ballots and Counts for Proportionality
        created_ballots, sorted_counts = create_ballots(num_votes, num_projects)

        # 2: create all the instances with the differently proportional costs and the probability of proportionality list
        cost_instances, prop_prob_list = create_list_cost_instances(num_votes, num_projects, budget, sorted_counts, num_profiles, prop_prob_start, prop_prob_step)

        # 3: create the profile
        profile = create_profile(created_ballots, cost_instances[0])

        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),"instances")

        # 4: save instance files
        for var in range(len(cost_instances)):
            
            instance_file = os.path.join(folder,f"instance_{str(e)}_{str(var)}.pb")
            write_pabulib(cost_instances[var], profile, instance_file)


make_instances(num_elections=100, num_votes=1000,num_projects=20,budget=500000,num_profiles=40,prop_prob_start=1,prop_prob_step=0.025)
