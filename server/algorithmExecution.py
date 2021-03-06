import numpy as np

from utils.DimensionalityReducer import DimensionalityReducer
from validation.Analyzer import Analyzer
from server.availableAlgorithms import is_normalized
from utils import Expressions
from utils.Sampler import Sampler
from datetime import datetime

dimReducer = DimensionalityReducer()
analyzer = Analyzer()

def execute(algorithm, dataLoader, one_against_rest, oversampling):
    start = datetime.now()
    data = getData(algorithm, dataLoader, oversampling)
    print("Got data", flush=True)
    print(datetime.now() - start, flush=True)
    
    
    start = datetime.now()
    labels, gene_indices = run(algorithm, data, one_against_rest)
    print("Feature Selection done", flush=True)
    print(datetime.now() - start, flush=True)
    
    start = datetime.now()
    expression_matrix = calcExpressionMatrix(algorithm, data, gene_indices, one_against_rest)
    print("Expression Matrix done", flush=True)
    print(datetime.now() - start, flush=True)
    
    start = datetime.now()
    evaluation = evaluate(algorithm, data, gene_indices, one_against_rest)
    print("Validation done", flush=True)
    print(datetime.now() - start, flush=True)

    if one_against_rest:
        response = {}
        for cancer_type, cancer_type_indices in gene_indices.items():
            genes = dataLoader.getGeneLabels()[cancer_type_indices]
            geneNames = dataLoader.getGeneNames()[cancer_type_indices]
            response[cancer_type] = assembleResponse(data, labels, cancer_type_indices,
                expression_matrix[cancer_type], evaluation[cancer_type], genes, geneNames)
        response["meanFitness"] = evaluation["meanFitness"]
        return response
    else:
        genes = dataLoader.getGeneLabels()[gene_indices]
        geneNames = dataLoader.getGeneNames()[gene_indices]
        return assembleResponse(data, labels, gene_indices, expression_matrix, evaluation, genes, geneNames)

def  assembleResponse(data, labels, gene_indices, expression_matrix, evaluation, geneLabels, geneNames):
    X = data["combined"].expressions[:, gene_indices]
    X = X[:,0:3]
    response_data = {}
    for label in np.unique(labels):
        response_data[label] = X[labels == label, :].T.tolist()

    return {
        'data': {key: scores[0:3] for (key, scores) in response_data.items()},
        'genes': geneLabels.tolist(),
        'expressionMatrix': expression_matrix,
        'geneNames': geneNames.tolist(),
        'evaluation': evaluation,
    }

def getData(algorithm, dataLoader, oversampling):
    cancer_types = algorithm["cancerTypes"]
    sick_tissue_types = algorithm["sickTissueTypes"]
    healthy_tissue_types = algorithm["healthyTissueTypes"]

    sick = dataLoader.getData(sick_tissue_types, cancer_types)
    sick = dataLoader.replaceLabels(sick)
    healthy = dataLoader.getData(healthy_tissue_types, cancer_types)
    healthy = dataLoader.replaceLabels(healthy)

    if oversampling:
        sampler = Sampler()
        healthy = sampler.over_sample(healthy)
        sick = sampler.over_sample(sick)

    combined = Expressions(np.vstack((sick.expressions, healthy.expressions)), np.hstack((sick.labels, healthy.labels)))
    data = {
        "sick": sick,
        "healthy": healthy,
        "combined": combined
    }
    return data


def run(algorithm, data, oneAgainstRest):
    method = algorithm["key"]
    k = algorithm["parameters"].get("k")
    n = algorithm["parameters"].get("n")
    m = algorithm["parameters"].get("m")
    norm = algorithm["parameters"].get("norm")
    fitness = algorithm["parameters"].get("fitness")

    # workaround to include relief as algorithm instead of normalization method
    if method == "relief":
        method = "norm"
        norm = "relief"
    
    method_is_normalized = is_normalized(method)
    if method_is_normalized:
        labels = np.hstack((data["sick"].labels, data["healthy"].labels))
    else:
        labels = data["combined"].labels

    if oneAgainstRest:
        sick = data["sick"] if method_is_normalized else data["combined"]
        healthy = data["healthy"] if method_is_normalized else ""
        
        if norm != None:
            features = dimReducer.getOneAgainstRestFeatures(sick, healthy, k, method=method, fitness=fitness, normalization=norm)
        else:
            features = dimReducer.getOneAgainstRestFeatures(sick, healthy, k, method=method, fitness=fitness)

        return labels, features

    elif method == "basic":
        gene_indices = dimReducer.getFeatures(data["combined"], k)

    elif method == "tree":
        gene_indices = dimReducer.getDecisionTreeFeatures(data["combined"], k)

    elif method == "norm":
        gene_indices = dimReducer.getNormalizedFeatures(
            data["sick"], data["healthy"], norm, k, n, "chi2")

    elif method == "sfs":
        gene_indices = dimReducer.getFeaturesBySFS(
            data["sick"], data["healthy"], k, n, m, norm, fitness)

    elif method == "ea":
        gene_indices = dimReducer.getEAFeatures(
            data["sick"], data["healthy"], k, n, m, norm, fitness)

    return labels, gene_indices


def calcExpressionMatrix(algorithm, data, gene_indices, oneAgainstRest):
    # only calc expression matrix if data contains sick and healthy samples
    sick_tissue_types = algorithm["sickTissueTypes"]
    healthy_tissue_types = algorithm["healthyTissueTypes"]
    if len(sick_tissue_types) == 0 or len(healthy_tissue_types) == 0:
        return None

    if oneAgainstRest:
        return analyzer.computeExpressionMatrixOneAgainstRest(data["sick"], data["healthy"], gene_indices)
    else:
        return analyzer.computeExpressionMatrix(data["sick"], data["healthy"], gene_indices)


def evaluate(algorithm, data, gene_indices, oneAgainstRest):
    cancer_types = algorithm["cancerTypes"]
    sick_tissue_types = algorithm["sickTissueTypes"]
    healthy_tissue_types = algorithm["healthyTissueTypes"]

    if len(cancer_types) == 1 or len(sick_tissue_types) == 0 or len(healthy_tissue_types) == 0:
        sick = data["combined"]
        healthy = ""
    else:
        sick = data["sick"]
        healthy = data["healthy"]

    if oneAgainstRest:
        return analyzer.computeFeatureValidationOneAgainstRest(sick, healthy, gene_indices)
    else:
        return analyzer.computeFeatureValidation(sick, healthy, gene_indices)
