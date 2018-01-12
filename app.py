import json
import numpy as np
import base64
import urllib
import xml.etree.ElementTree as ET
import rdflib
import shutil

from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
from xml.dom.minidom import parse, parseString
from flask import Flask, request
from flask_cors import CORS
from utils.DataLoader import DataLoader
from utils.DimensionalityReducer import DimensionalityReducer
from validation.Analyzer import Analyzer
from utils import Expressions

app = Flask(__name__)
CORS(app)
dataLoader = DataLoader("dataset4")
gene_labels = dataLoader.getGeneLabels()
gene_names = dataLoader.getGeneNames()
dimReducer = DimensionalityReducer()
analyzer = Analyzer()


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/testGenes', methods=["POST"])
def testGene():
    data = request.get_json()["genes"]
    genes = data["genes"]
    response = {}

    #DisGeNet - move down to individual gene
    sparql = SPARQLWrapper('http://rdf.disgenet.org/sparql/')
    sparql.setQuery("""
    SELECT DISTINCT
        ?gda
        <http://identifiers.org/ncbigene/1356> as ?gene
        ?score
        ?disease
        ?diseaselabel
        ?diseasename
        ?semanticType
    WHERE {
        ?gda sio:SIO_000628 <http://identifiers.org/ncbigene/1356>, ?disease ;
            sio:SIO_000253 ?source ;
            sio:SIO_000216 ?scoreIRI .
        ?disease sio:SIO_000008 ?semanticType .
        ?disease a ncit:C7057 .
        ?scoreIRI sio:SIO_000300 ?score .
        FILTER regex(?source, "UNIPROT|CTD_human")
        FILTER (?score >= 0.2)
        ?disease dcterms:title ?diseasename .
        ?disease rdfs:label ?diseaselabel
    }
    ORDER BY DESC(?score)
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)

    for gene in genes:

        #protein Atlas - TODO: save xml as file and only load new if we don't have it yet
        proteinAtlas = False
        try:

            url = 'https://www.proteinatlas.org/'+ gene +'.xml'
            file_name = 'data/proteinatlas/'+ gene +'.xml'

            if not os.path.isfile(fname):
                with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)

            f = open(file_name, 'r')
            xml = f.read()
            f.close()
            dom = parseString(xml.read())
            proteinClass = dom.getElementsByTagName('proteinClass')
            for c in proteinClass:
                if c.attributes['name'].value == "Cancer-related genes":
                    proteinAtlas = True
        except:
            print("Error accessing proteinatlas for gene: " + gene)


        #for result in results["results"]["bindings"]:
        #    print(result["label"]["value"])

        response[gene] = {'proteinAtlas': proteinAtlas, 'disgenet': results}

    return json.dumps(response)

@app.route("/algorithms", methods=["GET"])
def algorithms():
    response = {
        'algorithms': [
            {
                "name": 'PCA',
                "parameters": [
                    {
                        "name": "#Components",
                        "key": "n_components",
                        "default": 3
                    },
                    {
                        "name": "#Features per component",
                        "key": "n_features_per_component",
                        "default": 10
                    }
                ],
                "key": "getPCA"
            },
            {
                "name": 'Decision Tree',
                "parameters": [
                    {
                        "name": "#Features",
                        "key": "k",
                        "default": 20

                    }
                ],
                "key": "getDecisionTreeFeatures"
            },
            {
                "name": 'Feature Selection Normalization:Exclude',
                "parameters": [
                    {
                        "name": "#Features",
                        "key": "k",
                        "default": 20

                    },
                    {
                        "name": "#Considered features",
                        "key": "n",
                        "default": 5000

                    }
                ],
                "key": "getNormalizedFeaturesE"
            },
            {
                "name": 'Feature Selection Normalization:Substract',
                "parameters": [
                    {
                        "name": "#Features",
                        "key": "k",
                        "default": 20

                    },
                    {
                        "name": "#Considered features",
                        "key": "n",
                        "default": 5000

                    }
                ],
                "key": "getNormalizedFeaturesS"
            },
            {
                "name": "Feature Selection",
                "parameters": [
                    {
                        "name": "#Features",
                        "key": "k",
                        "default": 20

                    }
                ],
                "key": "getFeatures"
            },
            {
                "name": "Sequential Forward Selection (normalized)",
                "key": "getFeaturesBySFS",
                "parameters": []
            }
        ],
    }

    return json.dumps(response)


@app.route("/runAlgorithm", methods=["POST"])
def runSpecificAlgorithm():
    # POST key, parameters, cancerTypes, healthyTissueTypes, sickTissueTypes
    # match to specific algorithm
    algorithm = request.get_json()["algorithm"]
    # algorithm = {
    #     "key": "getPCA",
    #     "cancerTypes": ["LUAD"],
    #     "sickTissueTypes": ["TP"],
    #     "healthyTissueTypes": ["NT"],
    #     "parameters": {
    #         "n_components": 3,
    #         "n_features_per_component": 10
    #         }
    #
    # }
    key = algorithm["key"]

    sick = dataLoader.getData(
        algorithm["sickTissueTypes"], algorithm["cancerTypes"])
    healthy = dataLoader.getData(
        algorithm["healthyTissueTypes"], algorithm["cancerTypes"])
    data = dataLoader.getData(
        algorithm["healthyTissueTypes"] + algorithm["sickTissueTypes"], algorithm["cancerTypes"])

    calcExpressionMatrix = False

    if key == "getPCA":
        _, X, gene_indices = dimReducer.getPCA(
            data.expressions, algorithm["parameters"]["n_components"], algorithm["parameters"]["n_features_per_component"])
    elif key == "getDecisionTreeFeatures":
        gene_indices, X = dimReducer.getDecisionTreeFeatures(
            data, algorithm["parameters"]["k"])
    elif key == "getNormalizedFeaturesE":
        gene_indices, X, Y = dimReducer.getNormalizedFeaturesE(
            sick, healthy, algorithm["parameters"]["k"], algorithm["parameters"]["n"], "chi2")
        sick_response = X
        X = np.vstack((X, Y))
        calcExpressionMatrix = True
    elif key == "getNormalizedFeaturesS":
        gene_indices, X, Y = dimReducer.getNormalizedFeaturesS(
            sick, healthy, algorithm["parameters"]["k"], algorithm["parameters"]["n"], "chi2")
        sick_response = X
        X = np.vstack((X, Y))
        calcExpressionMatrix = True
    elif key == "getFeatures":
        gene_indices, X = dimReducer.getFeatures(
            data, algorithm["parameters"]["k"])
    elif key == "getFeaturesBySFS":
        gene_indices, X, Y = dimReducer.getFeaturesBySFS(
            sick, healthy)
        sick_response = X
        X = np.vstack((X, Y))
        calcExpressionMatrix = True

    responseData = {}
    for label in np.unique(data.labels):
        responseData[label] = X[data.labels == label, :].T.tolist()

    # calculate expression matrix
    expressionMatrix = None
    if calcExpressionMatrix:
        sick_reduced = Expressions(sick_response, sick.labels)
        healthy_reduced = Expressions(Y, healthy.labels)
        expressionMatrix = analyzer.computeExpressionMatrix(
            sick_reduced, healthy_reduced, gene_indices)

    # evaluation
    evaluation = analyzer.computeFeatureValidation(sick, healthy, gene_indices)

    response = {
        'data': responseData,
        'genes': gene_labels[gene_indices].tolist(),
        'expressionMatrix': expressionMatrix,
        'geneNames': gene_names[gene_indices].tolist(),
        'evaluation': evaluation,
    }
    return json.dumps(response)


@app.route('/statistics', methods=["GET"])
def getStatistics():
    statistics = dataLoader.getStatistics()

    return json.dumps(statistics.tolist())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=True, threaded=True)
