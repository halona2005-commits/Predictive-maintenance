"""
===========================================================
XGBoost Model
===========================================================
"""

import joblib

from xgboost import XGBClassifier

try:
    from Version_3.src.config import XGB_PARAMS
except ImportError:
    from config import XGB_PARAMS


class XGBoostModel:

    def __init__(self):

        self.model = XGBClassifier(**XGB_PARAMS)

    # --------------------------------------------------
    # Train
    # --------------------------------------------------

    def fit(self, X_train, y_train):

        print("\n" + "=" * 60)
        print("Training XGBoost")
        print("=" * 60)

        self.model.fit(X_train, y_train)

        return self

    # --------------------------------------------------
    # Predict
    # --------------------------------------------------

    def predict(self, X):

        return self.model.predict(X)

    # --------------------------------------------------
    # Predict Probability
    # --------------------------------------------------

    def predict_proba(self, X):

        return self.model.predict_proba(X)

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(self, path="../models/xgboost.pkl"):

        joblib.dump(self.model, path)

        print(f"Model saved -> {path}")

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    @classmethod
    def load(cls, path="../models/xgboost.pkl"):

        obj = cls()

        obj.model = joblib.load(path)

        return obj