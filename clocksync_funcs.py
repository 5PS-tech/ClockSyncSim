#######################
# Functions to run Clock Sync Simulation
#######################

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from itertools import combinations

# Adjustment functions
def daisy_adj(df, current_index, reporting_node, comparison_node, r=2):
    reporting_node_val = df.loc[current_index,str(reporting_node)]
    comparison_node_val = df.loc[current_index,str(comparison_node)]

    dif = reporting_node_val-comparison_node_val
    return dif/r

def no_adj(df, current_index, reporting_node, comparison_node, r=2):
    return 0

def local_increment(clock_freq,timeslot_period,freq_tolerance=.5):

    fmax=clock_freq*(1+freq_tolerance/100) # Max freq per error
    fmin=clock_freq*(1-freq_tolerance/100) # Min freq per error

    rand_macrotick_length = timeslot_period * np.random.uniform(fmin, fmax)
    return rand_macrotick_length


# Error plot function
def sim_plot(df, node_count):
    fig=plt.figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')

    print("Plot Setup Commencing...")

    # combs = list(combinations(range(node_count),2))
    # print(combs)
    #
    #
    combs = sum(1 for pair in combinations(range(node_count),2))

    for comb, t in enumerate(combinations(range(node_count),2)):
        n0, n1 = t
        if (comb%(combs//4)) == 0 and comb < combs-4:
            print("{}.0%".format(math.ceil((comb/combs)*100)), end =" - ")
        plt.scatter(df.index, df[str(n0)]-df[str(n1)])

    print("100.0%") #Plot Setup Complete...
    print("Please wait a moment for the plot to appear.\n")

    plt.xlabel('Time Slots')
    plt.ylabel('Skew (ticks)')
    plt.title('Skews between Clocks')


# Simulation function
def clock_sync_sim(freq_tolerance=.5, adjustment_func=daisy_adj, clock_freq = 40, timeslot_period = 1, node_count=4, sim_length=40, r=2):

    clock_freq = clock_freq*(10**6)
    timeslot_period = timeslot_period*(10**-3)

    nominal_macrotick_length = clock_freq * timeslot_period

    df = pd.DataFrame(index=range(sim_length), columns=['Counter','Node Reporting']+[str(node) for node in range(node_count)])
    df.Counter=df.index*nominal_macrotick_length

    df['Node Reporting'] = df.index%node_count
    nodes_ref = list(range(node_count))

    print("Simulation Setup Commencing...")
    for i in df.index:
        reporting_node = df.loc[i,'Node Reporting']
        comparison_nodes = nodes_ref.copy()
        comparison_nodes.remove(reporting_node)

        if (i%(sim_length//4)) == 0 and i < sim_length-4:
            print("{}.0%".format(math.ceil((i/sim_length)*100)), end =" - ")

        for j in range(node_count):
            if i == 0:
                df.loc[i,str(j)] = 0
            else:
                prev_time = df.loc[i-1,str(j)]
                df.loc[i,str(j)] = prev_time + local_increment(clock_freq,timeslot_period,freq_tolerance)

        for comparison_node in comparison_nodes:
            df.loc[i,str(comparison_node)] = df.loc[i,str(comparison_node)] + adjustment_func(df, i, reporting_node, comparison_node, r)

    print("100.0%\n") #Simulation Setup Complete

    fmax=clock_freq*(1+freq_tolerance/100) # Max freq per error
    fmin=clock_freq*(1-freq_tolerance/100) # Min freq per error

    # max_dev = rho(max drift rate) * R(resync interval) * 2 * r
    rho = (fmax-fmin)/clock_freq
    max_dev = rho*timeslot_period*(10**6) # Convert to usec
    nominal_tick_count = max_dev*clock_freq/(10**6) # Divide by unit adjustment

    sim_plot(df, node_count)
    print("Maximum Deviation: +/- {:.2f} usec ({} ticks at nominal frequency)".format(max_dev,math.ceil(nominal_tick_count)))
    return df
