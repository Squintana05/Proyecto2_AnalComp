from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DM_ROOT = REPO_ROOT / "ciencia_datos" / "ciencia_datosDM"
MODEL_PATH = (
    DM_ROOT
    / "mlartifacts"
    / "887865422362070209"
    / "0d1709afa4584d268dfa31b61e6bc949"
    / "artifacts"
    / "model_pregunta1"
    / "data"
    / "model.keras"
)
SCALER_PATH = (
    DM_ROOT
    / "mlartifacts"
    / "887865422362070209"
    / "0d1709afa4584d268dfa31b61e6bc949"
    / "artifacts"
    / "preprocessing"
    / "final_scaler.pkl"
)

EDUCATION_MAP = {
    "Ninguno": 0.0,
    "Primaria incompleta": 1.0,
    "Primaria completa": 2.0,
    "Secundaria (Bachillerato) incompleta": 3.0,
    "Secundaria (Bachillerato) completa": 4.0,
    "Técnica o tecnológica incompleta": 5.0,
    "Técnica o tecnológica completa": 6.0,
    "Educación profesional incompleta": 7.0,
    "Educación profesional completa": 8.0,
    "Postgrado": 9.0,
}

JORNADA_MAP = {
    "Mañana": 1,
    "Tarde": 2,
    "Noche": 3,
    "Sabatina": 4,
    "Única": 5,
    "Unica": 5,
    "Completa": 6,
}

DEFAULT_TAB1_PAYLOAD = {
    "cole_area": "Urbana",
    "cole_bilingue": "No",
    "cole_jornada": "Mañana",
    "cole_naturaleza": "Oficial",
    "estu_genero": "Masculino",
    "fami_cuartos": 3,
    "fami_educacionmadre": "Secundaria (Bachillerato) completa",
    "fami_educacionpadre": "Secundaria (Bachillerato) completa",
    "fami_estrato": 2,
    "fami_personas": 4,
    "fami_computador": "Si",
    "fami_internet": "Si",
    "fami_lavadora": "Si",
}

TAB1_GROUPS = {
    "Edu. familiar": ["fami_educacionmadre", "fami_educacionpadre"],
    "Estrato": ["fami_estrato"],
    "Composición hogar": ["fami_cuartos", "fami_personas"],
    "Tecnología": ["fami_computador", "fami_internet", "fami_lavadora"],
    "Bilingüe": ["cole_bilingue"],
    "Jornada": ["cole_jornada"],
    "Área": ["cole_area"],
    "Naturaleza": ["cole_naturaleza"],
    "Género": ["estu_genero"],
}


@dataclass
class Tab1Prediction:
    score: float
    base_score: float
    contributions: dict[str, float]


@lru_cache(maxsize=1)
def load_tab1_model(model_path: Path | str = MODEL_PATH):
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("TensorFlow is required to run the tab1 model.") from exc

    resolved_path = Path(model_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Tab 1 model artifact not found at {resolved_path}")
    return tf.keras.models.load_model(resolved_path)


@lru_cache(maxsize=1)
def load_tab1_scaler(scaler_path: Path | str = SCALER_PATH):
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("joblib is required to load the tab1 scaler.") from exc

    resolved_path = Path(scaler_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Tab 1 scaler artifact not found at {resolved_path}")
    return joblib.load(resolved_path)


def _bool_to_num(value: Any) -> float:
    return 1.0 if value in (1, "Si", "SI", True, "S", "Yes") else 0.0


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(DEFAULT_TAB1_PAYLOAD)
    normalized.update({k: v for k, v in payload.items() if v is not None})
    normalized["fami_cuartos"] = int(normalized["fami_cuartos"])
    normalized["fami_personas"] = int(normalized["fami_personas"])
    normalized["fami_estrato"] = int(normalized["fami_estrato"])
    return normalized


def build_tab1_vector(payload: dict[str, Any]) -> list[float]:
    scaler = load_tab1_scaler()
    normalized = _normalize_payload(payload)

    capital_educativo = (
        EDUCATION_MAP.get(normalized["fami_educacionmadre"], 4.0)
        + EDUCATION_MAP.get(normalized["fami_educacionpadre"], 4.0)
    ) / 2.0

    scaled = scaler.transform(
        pd.DataFrame(
            [
                {
                    "capital_educativo": capital_educativo,
                    "fami_cuartoshogar": float(normalized["fami_cuartos"]),
                    "fami_personashogar": float(normalized["fami_personas"]),
                    "fami_estratovivienda": float(normalized["fami_estrato"]),
                }
            ]
        )
    )[0]

    jornada_code = JORNADA_MAP.get(normalized["cole_jornada"], 1)
    jornada_one_hot = [1.0 if jornada_code == code else 0.0 for code in range(1, 7)]

    return [
        1.0 if normalized["cole_area"] == "Urbana" else 0.0,
        _bool_to_num(normalized["cole_bilingue"]),
        1.0 if normalized["cole_naturaleza"] == "Oficial" else 0.0,
        1.0 if normalized["estu_genero"] == "Masculino" else 0.0,
        float(scaled[0]),
        float(scaled[1]),
        float(scaled[2]),
        float(scaled[3]),
        _bool_to_num(normalized["fami_computador"]),
        _bool_to_num(normalized["fami_internet"]),
        _bool_to_num(normalized["fami_lavadora"]),
        *jornada_one_hot,
    ]


def predict_tab1_score(payload: dict[str, Any]) -> float:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("NumPy is required to run the tab1 model.") from exc

    model = load_tab1_model()
    vector = build_tab1_vector(payload)
    prediction = model.predict(np.asarray([vector], dtype="float32"), verbose=0).ravel()[0]
    return float(prediction)


def explain_tab1_prediction(payload: dict[str, Any]) -> Tab1Prediction:
    normalized = _normalize_payload(payload)
    base_payload = dict(DEFAULT_TAB1_PAYLOAD)
    base_score = predict_tab1_score(base_payload)

    cursor_payload = dict(base_payload)
    contributions: dict[str, float] = {}
    running_score = base_score

    for label, fields in TAB1_GROUPS.items():
        for field in fields:
            cursor_payload[field] = normalized[field]
        next_score = predict_tab1_score(cursor_payload)
        contributions[label] = float(next_score - running_score)
        running_score = next_score

    final_score = predict_tab1_score(normalized)
    residual = final_score - running_score
    if abs(residual) > 1e-6:
        contributions["Interacciones"] = float(residual)

    return Tab1Prediction(
        score=float(final_score),
        base_score=float(base_score),
        contributions=contributions,
    )
