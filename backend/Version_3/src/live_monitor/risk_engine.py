"""
===========================================================
WEIGHTED RISK ENGINE
===========================================================
"""

RF_WEIGHT = 0.25
XGB_WEIGHT = 0.25
LSTM_WEIGHT = 0.20
COMPRESSED_WEIGHT = 0.15
OCSVM_WEIGHT = 0.10
ISO_WEIGHT = 0.05


def calculate_risk(
    rf_pred,
    xgb_pred,
    iso_pred,
    ocsvm_pred,
    compressed_pred,
    lstm_pred,
    pem_score,
    pem_status,
    md_score,
    md_status
):

    model_score = (
    rf_pred * RF_WEIGHT +
    xgb_pred * XGB_WEIGHT +
    lstm_pred * LSTM_WEIGHT +
    compressed_pred * COMPRESSED_WEIGHT +
    ocsvm_pred * OCSVM_WEIGHT +
    iso_pred * ISO_WEIGHT
)

    if pem_status == "ANOMALY":
        pem_component = 1.0

    elif pem_status == "WARNING":
        pem_component = 0.5

    else:
        pem_component = 0.0

    if md_status == "ANOMALY":
        md_component = 1.0

    elif md_status == "WARNING":
        md_component = 0.5

    else:
        md_component = 0.0

    score = (
    0.20 * model_score +
    0.40 * pem_component +
    0.40 * md_component
)

    confidence = round(score * 100, 2)

    votes = (
        rf_pred +
        xgb_pred +
        iso_pred +
        ocsvm_pred +
        compressed_pred +
        lstm_pred
    )

    if score >= 0.80:
        risk = "CRITICAL"

    elif score >= 0.60:
        risk = "HIGH"

    elif score >= 0.40:
        risk = "MEDIUM"

    elif score >= 0.20:
        risk = "LOW"

    else:
        risk = "NORMAL"

    return {

        "score": round(score, 3),

        "risk": risk,

        "confidence": confidence,

        "votes": votes,

        "models": {

            "Random Forest": rf_pred,

            "XGBoost": xgb_pred,

            "Isolation Forest": iso_pred,

            "One-Class SVM": ocsvm_pred,

            "Compressed IF": compressed_pred,

            "LSTM": lstm_pred

        }

    }