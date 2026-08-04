"""
===========================================================
Isolation Forest Model
Research Version
===========================================================
"""

import joblib
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score

try:
    from Version_3.src.config import IF_PARAMS
except ImportError:
    from config import IF_PARAMS


class IsolationForestModel:

    def __init__(self):

        self.model = IsolationForest(**IF_PARAMS)

        self.threshold = 0.0

    # --------------------------------------------------
    # Train
    # --------------------------------------------------

    def fit(self, X_train, y_train, X_val=None, y_val=None):

        print("\n" + "=" * 60)
        print("Training Isolation Forest")
        print("=" * 60)

        # Train ONLY on normal samples

        X_normal = X_train[y_train == 0]

        print(f"Normal samples : {len(X_normal)}")

        self.model.fit(X_normal)

        if X_val is not None and y_val is not None:

            self.optimize_threshold(
                X_val,
                y_val
            )

        return self

    # --------------------------------------------------
    # Threshold Optimisation
    # --------------------------------------------------

    def optimize_threshold(
            self,
            X_val,
            y_val
    ):

        print("Optimising threshold...")

        scores = self.model.decision_function(X_val)

        thresholds = np.linspace(

            scores.min(),

            scores.max(),

            100

        )

        best_f1 = -1

        best_threshold = 0.0

        for threshold in thresholds:

            prediction = (

                scores < threshold

            ).astype(int)

            current_f1 = f1_score(

                y_val,

                prediction,

                zero_division=0

            )

            if current_f1 > best_f1:

                best_f1 = current_f1

                best_threshold = threshold

        self.threshold = best_threshold

        print(f"Best Threshold : {best_threshold:.5f}")

        print(f"Validation F1  : {best_f1:.4f}")

    # --------------------------------------------------
    # Predict
    # --------------------------------------------------

    def predict(self, X):

        scores = self.model.decision_function(X)

        return (

            scores < self.threshold

        ).astype(int)

    # --------------------------------------------------
    # Decision Score
    # --------------------------------------------------

    def decision_scores(self, X):

        return self.model.decision_function(X)

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(

        self,

        path="../models/isolation_forest.pkl"

    ):

        joblib.dump(

            {

                "model": self.model,

                "threshold": self.threshold

            },

            path

        )

        print(f"Model saved -> {path}")

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    @classmethod
    def load(

            cls,

            path="../models/isolation_forest.pkl"

    ):

        data = joblib.load(path)

        obj = cls()

        obj.model = data["model"]

        obj.threshold = data["threshold"]

        return obj