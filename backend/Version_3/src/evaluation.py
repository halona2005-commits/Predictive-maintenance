"""
===========================================================
MODEL EVALUATION
AI-Based Intelligent Predictive Maintenance
Version 2 Final
===========================================================
"""

import os
import time

import psutil
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    matthews_corrcoef,
    ConfusionMatrixDisplay,
    roc_curve,
    precision_recall_curve
)


def evaluate_model(model, X_test, y_test, model_name):

    print("\n" + "=" * 60)
    print(f"Evaluating {model_name}")
    print("=" * 60)

    os.makedirs("../results", exist_ok=True)
    os.makedirs("../plots", exist_ok=True)

    process = psutil.Process()

    memory_before = process.memory_info().rss

    start = time.perf_counter()

    y_pred = model.predict(X_test)

    end = time.perf_counter()

    memory_after = process.memory_info().rss

    latency = (end - start) * 1000

    cpu_usage = psutil.cpu_percent(interval=0.1)

    # ----------------------------------------------------
    # Basic Metrics
    # ----------------------------------------------------

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    mcc = matthews_corrcoef(
        y_test,
        y_pred
    )

    # ----------------------------------------------------
    # ROC AUC
    # ----------------------------------------------------

    probabilities = None
    auc_score = 0

    try:

        if hasattr(model, "predict_proba"):

            probabilities = model.predict_proba(X_test)[:, 1]

            auc_score = roc_auc_score(
                y_test,
                probabilities
            )

        elif hasattr(model, "decision_function"):

            probabilities = -model.decision_function(X_test)

            auc_score = roc_auc_score(
                y_test,
                probabilities
            )

    except Exception:

        probabilities = None
        auc_score = 0

    # ----------------------------------------------------
    # Confusion Matrix
    # ----------------------------------------------------

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    tn, fp, fn, tp = cm.ravel()

    specificity = float(
        tn / (tn + fp)
    )

    # ----------------------------------------------------
    # Classification Report
    # ----------------------------------------------------

    print("\nClassification Report\n")

    report = classification_report(
        y_test,
        y_pred,
        zero_division=0
    )

    print(report)

    report_path = (
        f"../results/"
        f"{model_name.lower().replace(' ','_')}_report.txt"
    )

    with open(report_path, "w") as file:
        file.write(report)

    print(
        f"Classification report saved -> {report_path}"
    )

        # ----------------------------------------------------
    # Confusion Matrix Plot
    # ----------------------------------------------------

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Normal", "Failure"]
    )

    fig, ax = plt.subplots(figsize=(6, 6))

    disp.plot(
        ax=ax,
        cmap="Blues",
        colorbar=False
    )

    plt.title(f"{model_name} Confusion Matrix")

    plt.tight_layout()

    confusion_path = (
        f"../plots/"
        f"{model_name.lower().replace(' ','_')}_confusion_matrix.png"
    )

    plt.savefig(
        confusion_path,
        dpi=300
    )

    plt.close()

    print("Confusion Matrix saved.")

    # ----------------------------------------------------
    # ROC Curve
    # ----------------------------------------------------

    if probabilities is not None:

        try:

            fpr, tpr, _ = roc_curve(
                y_test,
                probabilities
            )

            plt.figure(figsize=(6, 6))

            plt.plot(
                fpr,
                tpr,
                linewidth=2,
                label=f"AUC = {auc_score:.4f}"
            )

            plt.plot(
                [0, 1],
                [0, 1],
                "--"
            )

            plt.xlabel("False Positive Rate")

            plt.ylabel("True Positive Rate")

            plt.title(f"{model_name} ROC Curve")

            plt.legend()

            plt.tight_layout()

            plt.savefig(
                f"../plots/{model_name.lower().replace(' ','_')}_roc_curve.png",
                dpi=300
            )

            plt.close()

            print("ROC Curve saved.")

        except Exception:

            print("ROC Curve skipped.")

    else:

        print("ROC Curve skipped.")

    # ----------------------------------------------------
    # Precision Recall Curve
    # ----------------------------------------------------

    if probabilities is not None:

        try:

            precision_vals, recall_vals, _ = (
                precision_recall_curve(
                    y_test,
                    probabilities
                )
            )

            plt.figure(figsize=(6, 6))

            plt.plot(
                recall_vals,
                precision_vals,
                linewidth=2
            )

            plt.xlabel("Recall")

            plt.ylabel("Precision")

            plt.title(
                f"{model_name} Precision Recall Curve"
            )

            plt.tight_layout()

            plt.savefig(
                f"../plots/{model_name.lower().replace(' ','_')}_pr_curve.png",
                dpi=300
            )

            plt.close()

            print("Precision Recall Curve saved.")

        except Exception:

            print("Precision Recall Curve skipped.")

    else:

        print("Precision Recall Curve skipped.")

        # ----------------------------------------------------
    # Save Results
    # ----------------------------------------------------

    results = {
        "Model": model_name,
        "Accuracy": round(accuracy, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1 Score": round(f1, 4),
        "ROC AUC": round(auc_score, 4),
        "MCC": round(mcc, 4),
        "Specificity": round(specificity, 4),
        "Latency (ms)": round(latency, 2),
        "CPU (%)": round(cpu_usage, 2),
        "RAM (MB)": round(
            abs(memory_after - memory_before) / (1024 * 1024),
            2
        )
    }

    results_df = pd.DataFrame([results])

    csv_path = "../results/model_results.csv"

    if os.path.exists(csv_path):

        old = pd.read_csv(csv_path)

        old = pd.concat(
            [old, results_df],
            ignore_index=True
        )

        old.to_csv(
            csv_path,
            index=False
        )

    else:

        results_df.to_csv(
            csv_path,
            index=False
        )

    print(f"\nResults saved -> {csv_path}")

    # ----------------------------------------------------
    # Summary
    # ----------------------------------------------------

    print("\nSummary")
    print("-" * 60)

    for key, value in results.items():
        print(f"{key:18}: {value}")

    print("-" * 60)

    return results