import joblib
from sklearn.ensemble import RandomForestClassifier
try:
    from Version_3.src.config import RF_PARAMS
except ImportError:
    from config import RF_PARAMS


def train_random_forest(X_train, y_train):

    print("\n" + "=" * 60)
    print("Training Random Forest")
    print("=" * 60)

    model = RandomForestClassifier(**RF_PARAMS)

    model.fit(X_train, y_train)

    joblib.dump(model, "../models/random_forest.pkl")

    print("Model saved -> models/random_forest.pkl")

    return model