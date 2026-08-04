"""
SHAP Explainability
"""

import os
import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def explain_model(model, X_train, X_test, feature_names):

    print("\n" + "=" * 60)
    print("Generating SHAP Explanations")
    print("=" * 60)

    os.makedirs("../plots", exist_ok=True)
    os.makedirs("../results", exist_ok=True)

    X_sample = X_test[:200]

    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X_sample)

    # ---------------------------------------
    # Handle SHAP output format
    # ---------------------------------------

    if isinstance(shap_values, list):
        shap_array = shap_values[1]
    else:
        shap_array = shap_values

        if len(shap_array.shape) == 3:
            shap_array = shap_array[:, :, 1]

    # ---------------------------------------
    # Feature Importance
    # ---------------------------------------

    importance = np.abs(shap_array).mean(axis=0)

    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importance
    })

    importance_df = importance_df.sort_values(
        by="Importance",
        ascending=False
    )

    importance_df.to_csv(
        "../results/feature_importance.csv",
        index=False
    )

    print("Feature importance saved.")

    # ---------------------------------------
    # SHAP Summary
    # ---------------------------------------

    plt.figure()

    shap.summary_plot(
        shap_array,
        X_sample,
        feature_names=feature_names,
        show=False
    )

    plt.tight_layout()

    plt.savefig(
        "../plots/shap_summary.png",
        dpi=300
    )

    plt.close()

    # ---------------------------------------
    # SHAP Bar Plot
    # ---------------------------------------

    plt.figure()

    shap.summary_plot(
        shap_array,
        X_sample,
        feature_names=feature_names,
        plot_type="bar",
        show=False
    )

    plt.tight_layout()

    plt.savefig(
        "../plots/shap_bar.png",
        dpi=300
    )

    plt.close()

    print("SHAP plots saved.")