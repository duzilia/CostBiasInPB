import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

#####
# plots and saves the pbc comparative statistical data from a given csv
#####
def plot_pbc_from_csv(csv_file, output_folder):
    df = pd.read_csv(csv_file)

    grouped_df = df.groupby('var').mean().reset_index()

    proportionality_prob = 1 - (0.025 * (grouped_df['var'] + 1))

    sorted_indices = np.argsort(proportionality_prob)
    proportionality_prob = proportionality_prob[sorted_indices]
    stat_val_greedy_budget = grouped_df['stat_val_greedy_budget'].iloc[sorted_indices]
    p_val_greedy_budget = grouped_df['p_val_greedy_budget'].iloc[sorted_indices]
    stat_val_MES_budget = grouped_df['stat_val_MES_budget'].iloc[sorted_indices]
    p_val_MES_budget = grouped_df['p_val_MES_budget'].iloc[sorted_indices]

    stat_val_greedy_diff = grouped_df['stat_val_greedy_diff'].iloc[sorted_indices]
    p_val_greedy_diff = grouped_df['p_val_greedy_diff'].iloc[sorted_indices]
    stat_val_MES_diff = grouped_df['stat_val_MES_diff'].iloc[sorted_indices]
    p_val_MES_diff = grouped_df['p_val_MES_diff'].iloc[sorted_indices]

    plt.figure(figsize=(12, 24))

    plt.subplot(4, 1, 1)
    plt.plot(proportionality_prob, stat_val_greedy_budget, label='Greedy', color='blue')
    plt.plot(proportionality_prob, stat_val_MES_budget, label='MES', color='orange')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('Statistic Value')
    plt.title('Statistics for Budget Percentage')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 2)
    plt.plot(proportionality_prob, p_val_greedy_budget, label='Greedy', color='blue')
    plt.plot(proportionality_prob, p_val_MES_budget, label='MES', color='orange')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('P-value')
    plt.title('P-values for Budget Percentage')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 3)
    plt.plot(proportionality_prob, stat_val_greedy_budget - stat_val_MES_budget, label='Difference (Greedy - MES)', color='green')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('Difference in Statistic Value')
    plt.title('Difference in Statistics (Greedy - MES) for Budget Percentage')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 4)
    plt.plot(proportionality_prob, p_val_greedy_budget - p_val_MES_budget, label='Difference (Greedy - MES)', color='purple')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('Difference in P-value')
    plt.title('Difference in P-values (Greedy - MES) for Budget Percentage')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(f'{output_folder}/pbc_budget_percentage.png')
    plt.close()

    plt.figure(figsize=(12, 24))

    plt.subplot(4, 1, 1)
    plt.plot(proportionality_prob, stat_val_greedy_diff, label='Greedy', color='blue')
    plt.plot(proportionality_prob, stat_val_MES_diff, label='MES', color='orange')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('Statistic Value')
    plt.title('Statistics for Difference')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 2)
    plt.plot(proportionality_prob, p_val_greedy_diff, label='Greedy', color='blue')
    plt.plot(proportionality_prob, p_val_MES_diff, label='MES', color='orange')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('P-value')
    plt.title('P-values for Difference')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 3)
    plt.plot(proportionality_prob, stat_val_greedy_diff - stat_val_MES_diff, label='Difference (Greedy - MES)', color='green')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('Difference in Statistic Value')
    plt.title('Difference in Statistics (Greedy - MES) for Difference')
    plt.legend()
    plt.grid(True)

    plt.subplot(4, 1, 4)
    plt.plot(proportionality_prob, p_val_greedy_diff - p_val_MES_diff, label='Difference (Greedy - MES)', color='purple')
    plt.xlabel('Proportionality Probability')
    plt.ylabel('Difference in P-value')
    plt.title('Difference in P-values (Greedy - MES) for Difference')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(f'{output_folder}/pbc_difference.png')
    plt.close()
