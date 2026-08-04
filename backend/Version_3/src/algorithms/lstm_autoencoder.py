"""
===========================================================
LSTM Autoencoder
===========================================================
"""

import numpy as np
import joblib
import tensorflow as tf
from pathlib import Path

from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input,
    LSTM,
    RepeatVector,
    TimeDistributed,
    Dense
)


# ---------------------------------------------------------
# Sequence Creator
# ---------------------------------------------------------

def create_sequences(X, y=None, sequence_length=5):

    sequences = []
    labels = []

    for i in range(len(X) - sequence_length + 1):

        sequences.append(
            X[i:i + sequence_length]
        )

        if y is not None:
            labels.append(
                y.iloc[i + sequence_length - 1]
            )

    X_seq = np.array(sequences)

    if y is None:
        return X_seq

    return X_seq, np.array(labels)


# ---------------------------------------------------------
# LSTM Autoencoder Class
# ---------------------------------------------------------

class LSTMAutoencoder:

    def __init__(self):

        self.model = None

        self.threshold = None

    # -----------------------------------------------------

    def build(self, sequence_length, n_features):

        inputs = Input(
            shape=(sequence_length, n_features)
        )

        encoded = LSTM(
            32,
            activation="relu"
        )(inputs)

        decoded = RepeatVector(
            sequence_length
        )(encoded)

        decoded = LSTM(
            32,
            activation="relu",
            return_sequences=True
        )(decoded)

        outputs = TimeDistributed(
            Dense(n_features)
        )(decoded)

        self.model = Model(
            inputs,
            outputs
        )

        self.model.compile(

            optimizer="adam",

            loss="mse"

        )

    # -----------------------------------------------------

    def fit(self, X_train):

        print("\n" + "=" * 60)
        print("Training LSTM Autoencoder")
        print("=" * 60)

        self.build(
            X_train.shape[1],
            X_train.shape[2]
        )

        callbacks = [

            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=5,
                restore_best_weights=True
            ),

            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=3
            )

        ]

        history = self.model.fit(

            X_train,

            X_train,

            epochs=50,

            batch_size=32,

            validation_split=0.1,

            callbacks=callbacks,

            verbose=1

        )

        reconstruction = self.model.predict(
            X_train,
            verbose=0
        )

        mse = np.mean(
            np.square(
                X_train - reconstruction
            ),
            axis=(1, 2)
        )

        self.threshold = np.percentile(
            mse,
            95
        )

        print(f"\nThreshold : {self.threshold:.6f}")

        return history
    # -----------------------------------------------------

    def predict(self, X):

        reconstruction = self.model.predict(
            X,
            verbose=0
        )

        mse = np.mean(

            np.square(

                X - reconstruction

            ),

            axis=(1, 2)

        )

        return (

            mse > self.threshold

        ).astype(int)

    # -----------------------------------------------------

    def save(self):

        base_dir = Path(__file__).resolve().parents[2]

        self.model.save(
            base_dir / "models" / "lstm_autoencoder.keras"
        )

        joblib.dump(
            self.threshold,
            base_dir / "models" / "lstm_threshold.pkl"
        )

        print("LSTM model saved successfully.")

   # -----------------------------------------------------

    def load(self):

        base_dir = Path(__file__).resolve().parents[2]

        self.model = tf.keras.models.load_model(
            base_dir / "models" / "lstm_autoencoder.keras"
        )

        self.threshold = joblib.load(
            base_dir / "models" / "lstm_threshold.pkl"
        )

        print("LSTM model loaded successfully.")