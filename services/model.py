"""
Contains the code for the AI model that predicts diseases based on symptoms.
"""

import pandas as pd
import numpy as np
import re
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import warnings

from schema.responses.model import ModelMetrics, ModelStatus

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure logging
logger = logging.getLogger(__name__)

# Global state for ML models and data
ml_models: Dict = {}
data_dictionaries: Dict = {"severity": {}, "descriptions": {}, "precautions": {}}
symptoms_dict: Dict = {}
feature_names: List[str] = []
label_encoder = None
model_status = ModelStatus(
    loaded=False, data_path="data/", master_data_path="master-data/"
)


def load_models_and_data(
    data_path: str = "data/", master_data_path: str = "master-data/"
) -> bool:
    """Load ML models and supporting data"""
    global ml_models, data_dictionaries, symptoms_dict, feature_names, label_encoder, model_status

    try:
        logger.info("Loading ML models and data...")

        data_path = Path(data_path)
        master_data_path = Path(master_data_path)

        # Update model status paths
        model_status.data_path = str(data_path)
        model_status.master_data_path = str(master_data_path)

        # Load training and testing data
        training_file = data_path / "training.csv"
        testing_file = data_path / "testing.csv"

        if not training_file.exists() or not testing_file.exists():
            raise FileNotFoundError(f"Data files not found in {data_path}")

        training_data = pd.read_csv(training_file)
        testing_data = pd.read_csv(testing_file)

        # Prepare features and labels
        feature_names = training_data.columns[:-1].tolist()
        X = training_data[feature_names]
        y = training_data["prognosis"]

        # Create symptoms dictionary
        symptoms_dict = {symptom: index for index, symptom in enumerate(feature_names)}

        # Encode labels
        label_encoder = preprocessing.LabelEncoder()
        label_encoder.fit(y)
        y_encoded = label_encoder.transform(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.33, random_state=42
        )

        # Train Decision Tree
        dt_classifier = DecisionTreeClassifier(random_state=42)
        dt_classifier.fit(X_train, y_train)

        # Train SVM
        svm_classifier = SVC(probability=True, random_state=42)
        svm_classifier.fit(X_train, y_train)

        # Calculate metrics
        dt_accuracy = accuracy_score(y_test, dt_classifier.predict(X_test))
        svm_accuracy = accuracy_score(y_test, svm_classifier.predict(X_test))
        cv_scores = cross_val_score(dt_classifier, X_test, y_test, cv=3)

        # Store models
        ml_models = {
            "decision_tree": dt_classifier,
            "svm": svm_classifier,
            "training_data": training_data,
            "reduced_data": training_data.groupby(training_data["prognosis"]).max(),
            "label_encoder": label_encoder,
        }

        # Load supporting data
        load_severity_dict(master_data_path)
        load_description_dict(master_data_path)
        load_precaution_dict(master_data_path)

        # Update model status
        model_status.loaded = True
        model_status.last_loaded = datetime.now().isoformat()
        model_status.metrics = ModelMetrics(
            decision_tree_accuracy=dt_accuracy,
            svm_accuracy=svm_accuracy,
            cross_validation_mean=cv_scores.mean(),
            total_symptoms=len(feature_names),
            total_diseases=len(label_encoder.classes_),
        )

        logger.info(
            f"Models loaded successfully. DT Accuracy: {dt_accuracy:.3f}, SVM Accuracy: {svm_accuracy:.3f}"
        )
        return True

    except Exception as e:
        logger.error(f"Error loading models and data: {str(e)}")
        model_status.loaded = False
        raise e


def load_severity_dict(master_data_path: Path) -> None:
    """Load symptom severity data"""
    global data_dictionaries

    severity_file = master_data_path / "symptom_severity.csv"
    if severity_file.exists():
        try:
            with open(severity_file, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) >= 2:
                        try:
                            data_dictionaries["severity"][row[0]] = int(row[1])
                        except ValueError:
                            continue
            logger.info(f"Loaded {len(data_dictionaries['severity'])} severity entries")
        except Exception as e:
            logger.error(f"Error loading severity data: {e}")


def load_description_dict(master_data_path: Path) -> None:
    """Load symptom descriptions"""
    global data_dictionaries

    desc_file = master_data_path / "symptom_Description.csv"
    if desc_file.exists():
        try:
            with open(desc_file, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) >= 2:
                        data_dictionaries["descriptions"][row[0]] = row[1]
            logger.info(
                f"Loaded {len(data_dictionaries['descriptions'])} description entries"
            )
        except Exception as e:
            logger.error(f"Error loading description data: {e}")


def load_precaution_dict(master_data_path: Path) -> None:
    """Load precaution data"""
    global data_dictionaries

    precaution_file = master_data_path / "symptom_precaution.csv"
    if precaution_file.exists():
        try:
            with open(precaution_file, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) >= 5:
                        precautions = [p.strip() for p in row[1:5] if p.strip()]
                        data_dictionaries["precautions"][row[0]] = precautions
            logger.info(
                f"Loaded {len(data_dictionaries['precautions'])} precaution entries"
            )
        except Exception as e:
            logger.error(f"Error loading precaution data: {e}")


def search_symptoms(
    symptom_query: str, max_matches: int = 10
) -> Tuple[List[str], bool]:
    """Search for symptoms matching user input"""
    if not model_status.loaded:
        raise RuntimeError("Models not loaded")

    # Normalize input
    search_term = symptom_query.replace(" ", "_").lower()

    # Create regex pattern for flexible matching
    pattern = re.compile(search_term, re.IGNORECASE)

    # Search through available symptoms
    matches = []
    exact_match = False

    for symptom in feature_names:
        if symptom.lower() == search_term:
            exact_match = True
            matches.insert(0, symptom)  # Put exact match first
        elif pattern.search(symptom.lower()):
            matches.append(symptom)

    # Remove duplicates while preserving order
    seen = set()
    unique_matches = []
    for match in matches:
        if match not in seen:
            seen.add(match)
            unique_matches.append(match)

    return unique_matches[:max_matches], exact_match


def get_primary_diagnosis(symptom: str) -> str:
    """Get primary diagnosis using decision tree traversal"""
    if not model_status.loaded:
        raise RuntimeError("Models not loaded")

    try:
        tree = ml_models["decision_tree"].tree_
        feature_names_array = np.array(feature_names)

        def recurse(node):
            if tree.feature[node] != _tree.TREE_UNDEFINED:
                feature_name = feature_names_array[tree.feature[node]]

                if feature_name.lower() == symptom.lower():
                    # Follow the positive branch
                    return recurse(tree.children_right[node])
                else:
                    # Follow the negative branch
                    return recurse(tree.children_left[node])
            else:
                # Leaf node - get diagnosis
                class_probabilities = tree.value[node][0]
                predicted_class = np.argmax(class_probabilities)
                return label_encoder.inverse_transform([predicted_class])[0]

        return recurse(0)

    except Exception as e:
        logger.error(f"Error in primary diagnosis: {str(e)}")
        return "Unknown"


def get_secondary_diagnosis(symptoms: List[str]) -> str:
    """Get secondary diagnosis using SVM with symptom vector"""
    if not model_status.loaded:
        raise RuntimeError("Models not loaded")

    try:
        # Create input vector
        input_vector = np.zeros(len(feature_names))

        for symptom in symptoms:
            # Normalize symptom name
            normalized_symptom = symptom.replace(" ", "_").lower()

            # Find matching feature
            for i, feature in enumerate(feature_names):
                if feature.lower() == normalized_symptom:
                    input_vector[i] = 1
                    break

        # Get prediction
        prediction = ml_models["svm"].predict([input_vector])
        return label_encoder.inverse_transform(prediction)[0]

    except Exception as e:
        logger.error(f"Error in secondary diagnosis: {str(e)}")
        return "Unknown"


def calculate_severity(symptoms: List[str], days: int) -> str:
    """Calculate severity assessment based on symptoms and duration"""
    try:
        total_severity = 0
        symptom_count = 0

        for symptom in symptoms:
            normalized_symptom = symptom.replace(" ", "_").lower()
            # Try to find severity score
            for severity_key in data_dictionaries["severity"]:
                if severity_key.lower() == normalized_symptom:
                    total_severity += data_dictionaries["severity"][severity_key]
                    symptom_count += 1
                    break

        if symptom_count == 0:
            return "Unable to assess severity - no matching symptoms found"

        severity_score = (total_severity * days) / (symptom_count + 1)

        logger.info(
            f"Severity calculation: score={severity_score:.2f}, symptoms={symptom_count}, days={days}"
        )

        if severity_score > 13:
            return "High - Consult a doctor immediately"
        elif severity_score > 7:
            return "Moderate - Consider medical consultation"
        else:
            return "Low - Monitor symptoms and take precautions"

    except Exception as e:
        logger.error(f"Error calculating severity: {str(e)}")
        return "Unable to assess severity due to processing error"


def get_disease_description(disease: str) -> str:
    """Get description for a disease"""
    return data_dictionaries["descriptions"].get(disease, "No description available")


def get_disease_precautions(disease: str) -> List[str]:
    """Get precautions for a disease"""
    precautions = data_dictionaries["precautions"].get(
        disease, ["Consult a healthcare professional"]
    )
    # Filter out empty strings and strip whitespace
    return [p.strip() for p in precautions if p.strip()]


def get_model_status() -> ModelStatus:
    """Get current model status"""
    return model_status


def is_models_loaded() -> bool:
    """Check if models are loaded"""
    return model_status.loaded


def get_available_symptoms() -> List[str]:
    """Get list of all available symptoms"""
    return feature_names.copy() if model_status.loaded else []


def get_available_diseases() -> List[str]:
    """Get list of all available diseases"""
    if not model_status.loaded:
        return []
    return label_encoder.classes_.tolist()


def validate_symptom(symptom: str) -> bool:
    """Validate if a symptom exists in the database"""
    if not model_status.loaded:
        return False

    normalized = symptom.replace(" ", "_").lower()
    return any(feature.lower() == normalized for feature in feature_names)


def get_model_metrics() -> Optional[ModelMetrics]:
    """Get model performance metrics"""
    return model_status.metrics


def reload_models() -> bool:
    """Reload models and data"""
    try:
        return load_models_and_data(
            model_status.data_path, model_status.master_data_path
        )
    except Exception as e:
        logger.error(f"Error reloading models: {e}")
        return False