import shap
import pandas as pd
import numpy as np

class AMLShapExplainer:
    def __init__(self, model, background_data):
        """
        Initializes the SHAP TreeExplainer for scikit-learn's Isolation Forest.
        background_data should be a pandas DataFrame containing features: 'degree', 'pagerank'.
        """
        self.model = model
        self.background_data = background_data
        # Using a sample of background data to keep explanation calculation fast
        self.explainer = shap.TreeExplainer(self.model, self.background_data)

    def explain(self, degree, pagerank):
        """
        Generates SHAP values for a single node's degree and pagerank.
        Returns a dictionary containing the feature contributions and the base value.
        """
        instance = pd.DataFrame([[degree, pagerank]], columns=['degree', 'pagerank'])
        
        # Calculate SHAP values
        shap_values = self.explainer(instance)
        
        # Extract features and their contributions
        contribs = shap_values.values[0]
        base_value = shap_values.base_values[0]
        
        return {
            "degree_contribution": float(contribs[0]),
            "pagerank_contribution": float(contribs[1]),
            "base_value": float(base_value),
            "prediction_value": float(base_value + np.sum(contribs))
        }
