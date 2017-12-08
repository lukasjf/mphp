# %%
import numpy as np
from utils.DataLoader import DataLoader
from utils.DimensionalityReducer import DimensionalityReducer
from utils.EA.crossover import *
from utils.EA.mutation import *
from utils.EA.algorithm import ea_for_plot, run
from utils.EA.fitness import fitness
from utils.EA.ea_utils import display_stat_1
import utils.EA.config as c

print("import successful")

# %%
dataLoader = DataLoader("dataset4")
dimReducer = DimensionalityReducer()

healthy = dataLoader.getData(["healthy"], ["THCA","LUAD"])
sick = dataLoader.getData(["sick"], ["THCA","LUAD"])
gene_labels = dataLoader.getGeneLabels()

print("got data")

# %%
chromo_size = 100
selected_genes, sick_X, healthy_X = dimReducer.getNormalizedFeatures(sick,healthy,"exclude", chromo_size)
print("preselected genes")


#%%

### PARAMS FOR EA
if c.crossover == "uniform":
    crossover = uniform_crossover
elif c.crossover == "two_points":
    crossover = two_points_crossover
else: 
    crossover = one_point_crossover

mutation = binary_mutation

fitness_function = fitness(sick_X, sick.labels, healthy_X, healthy.labels)

best, stat, stat_aver = ea_for_plot(c, chromo_size, fitness_function, crossover, mutation)

display_stat_1(stat, stat_aver)
print(best)