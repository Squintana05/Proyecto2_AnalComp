from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from tab2_model import (
    ARTIFACT_DIR,
    BEST_VALIDATION_CONFIG,
    ENCODED_DATA_PATH,
    MODEL_INPUT_COLUMNS,
    TARGET_THRESHOLD,
    build_tab2_municipality_summary,
)


SEED = 42


def build_model(input_dim, num_classes, hidden_layers=(16, 24, 8), dropout_rate=0.2, learning_rate=1e-3):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(input_dim,)))

    for units in hidden_layers:
        model.add(tf.keras.layers.Dense(units, activation="relu"))
        model.add(tf.keras.layers.Dropout(dropout_rate))

    model.add(tf.keras.layers.Dense(num_classes, activation="softmax"))
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def build_training_frame() -> pd.DataFrame:
    data = pd.read_csv(ENCODED_DATA_PATH)
    data["nivel_educacion_padres"] = round((data["fami_educacionmadre"] + data["fami_educacionpadre"]) / 2, 0)
    data["hacinamiento"] = data["fami_personashogar"] / (data["fami_cuartoshogar"] + 1)
    data["nivel_ingles"] = data["punt_ingles"].apply(lambda value: 0 if value <= TARGET_THRESHOLD else 1)

    selected = [
        "cole_bilingue",
        "cole_jornada",
        "cole_area_ubicacion",
        "cole_naturaleza",
        "cole_caracter",
        "cole_area_ubicacion",
        "fami_tienecomputador",
        "fami_tieneinternet",
        "fami_estratovivienda",
        "nivel_educacion_padres",
        "hacinamiento",
        "nivel_ingles",
    ]

    frame = data[selected].copy().dropna()
    frame = frame[~frame.isin([-1, "-1"]).any(axis=1)].copy()

    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded_array = encoder.fit_transform(frame[["cole_jornada", "cole_caracter"]])
    encoded_cols = encoder.get_feature_names_out(["cole_jornada", "cole_caracter"])
    encoded_df = pd.DataFrame(encoded_array, columns=encoded_cols, index=frame.index).astype(int)

    final_frame = pd.concat([frame.drop(columns=["cole_jornada", "cole_caracter"]), encoded_df], axis=1)
    return final_frame


def export_tab2_artifact():
    np.random.seed(SEED)
    tf.random.set_seed(SEED)

    frame = build_training_frame()
    X = frame.drop(columns="nivel_ingles")
    y = frame["nivel_ingles"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=SEED,
        shuffle=True,
        stratify=y,
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=SEED,
        shuffle=True,
        stratify=y_temp,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train.astype("float32"))
    X_val_scaled = scaler.transform(X_val.astype("float32"))
    X_test_scaled = scaler.transform(X_test.astype("float32"))

    smote = SMOTE(random_state=SEED)
    X_train_bal, y_train_bal = smote.fit_resample(X_train_scaled, y_train.astype("int32"))

    params = BEST_VALIDATION_CONFIG
    model = build_model(
        input_dim=X_train.shape[1],
        num_classes=2,
        hidden_layers=params["hidden_layers"],
        dropout_rate=params["dropout_rate"],
        learning_rate=params["learning_rate"],
    )

    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=8,
        restore_best_weights=True,
    )

    model.fit(
        X_train_bal,
        y_train_bal,
        validation_data=(X_val_scaled, y_val.astype("int32")),
        epochs=params["epochs"],
        batch_size=params["batch_size"],
        verbose=1,
        callbacks=[early_stop],
    )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    model.save(ARTIFACT_DIR / "tab2_model.keras")

    probability_reference = model.predict(X_test_scaled, verbose=0)[:, 1].astype(float).tolist()
    bundle = {
        "feature_order": MODEL_INPUT_COLUMNS,
        "scaler_mean": scaler.mean_.astype(float).tolist(),
        "scaler_scale": scaler.scale_.astype(float).tolist(),
        "probability_reference": probability_reference,
        "target_threshold": TARGET_THRESHOLD,
        "best_validation_config": {
            **params,
            "hidden_layers": list(params["hidden_layers"]),
        },
    }

    (ARTIFACT_DIR / "tab2_bundle.json").write_text(
        json.dumps(bundle, indent=2),
        encoding="utf-8",
    )

    municipality_summary = build_tab2_municipality_summary()
    municipality_summary.to_csv(ARTIFACT_DIR / "municipality_summary.csv", index=False)

    # Placeholder for explainability. Replace with permutation importance or SHAP
    # once the notebook environment exposes that output.
    impact_rows = pd.DataFrame(
        {
            "feature": MODEL_INPUT_COLUMNS,
            "importance": np.zeros(len(MODEL_INPUT_COLUMNS)),
        }
    )
    impact_rows.to_csv(ARTIFACT_DIR / "feature_importance.csv", index=False)


if __name__ == "__main__":
    export_tab2_artifact()
