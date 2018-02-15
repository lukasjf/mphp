from collections import OrderedDict

algorithms = {
    'tree': {
        "name": "Decision Tree",
        "parameters": [
            {
                "key": "k",
                "name": "#Features",
                "default": 10
            }
        ]
    },
    'norm': {
        "name": "Normalized Feature Selection",
        "parameters": [
            {
                "key": "k",
                "name": "#Features",
                "default": 10
            },
            {
                "key": "n",
                "name": "#Excluded features",
                "default": 5000
            },
            {
                "key": "norm",
                "name": "Normalization method",
                "default": "exclude",
                "available": ["subtract", "exclude", "relief"]
            }
        ]
    },
    "basic": {
        "name": "Feature Selection",
        "parameters": [
            {
                "key": "k",
                "name": "#Features",
                "default": 10
            }
        ]
    },
    "sfs": {
        "name": "Sequential Forward Selection (normalized)",
        "parameters": [
            {
                "key": "k",
                "name": "#Features",
                "default": 10
            },
            {
                "key": "n",
                "name": "#Excluded features",
                "default": 5000
            },
            {
                "key": "m",
                "name": "#Preselected features",
                "default": 100
            },
            {
                "key": "norm",
                "name": "Preselection normalization",
                "default": "exclude",
                "available": ["subtract", "exclude", "relief"]
            },
            {
                "key": "fitness",
                "name": "Fitness function",
                "default": "combined",
                "available": ["combined", "classification", "clustering", "sick_vs_healthy", "distance"]
            }
        ]
    },
    "ea": {
        "name": "Evolutionary Algorithm",
        "parameters": [
            {
                "key": "k",
                "name": "#Features",
                "default": 10
            },
            {
                "key": "n",
                "name": "#Excluded features",
                "default": 5000
            },
            {
                "key": "m",
                "name": "#Preselected features",
                "default": 100
            },
            {
                "key": "norm",
                "name": "Preselection normalization",
                "default": "exclude",
                "available": ["subtract", "exclude", "relief"]
            },
            {
                "key": "fitness",
                "name": "Fitness function",
                "default": "combined",
                "available": ["combined", "classification", "clustering", "sick_vs_healthy", "distance"]
            }
        ]
    }
}


def is_normalized(method):
    normalized_methods = [
        key for key in algorithms.keys()
        if any(x.get("key", None) == "norm" for x in algorithms[key]["parameters"])
    ]
    return method in normalized_methods
