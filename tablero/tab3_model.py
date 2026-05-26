from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from patsy import build_design_matrices


REPO_ROOT = Path(__file__).resolve().parents[1]
SQ_ROOT = REPO_ROOT / "ciencia_datos" / "ciencia_datosSQ"
OLS_MODEL_PATH = SQ_ROOT / "ols_brecha" / "modelo_ols_baseline.pkl"
METADATA_PATH = SQ_ROOT / "ols_brecha" / "metadata.json"

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

CARACTER_MAP = {
    "Técnico": 1.0,
    "Tecnico": 1.0,
    "Técnico/Académico": 2.0,
    "Tecnico/Academico": 2.0,
    "Académico": 3.0,
    "Academico": 3.0,
    "No aplica": 4.0,
}

DEFAULT_TAB3_PAYLOAD = {
    "fami_internet": "Si",
    "fami_computador": "Si",
    "fami_estrato": 2,
    "fami_educacionmadre": "Secundaria (Bachillerato) completa",
    "fami_educacionpadre": "Secundaria (Bachillerato) completa",
    "fami_personas": 4,
    "fami_cuartos": 3,
    "cole_area": "Urbana",
    "cole_caracter": "Académico",
    "cole_jornada": "Mañana",
    "cole_naturaleza": "Oficial",
}

TAB3_GROUP_MAP = {
    "Estrato": lambda c: c.startswith("C(fami_estratovivienda)"),
    "Tecnología": lambda c: c == "indice_tech" or c.startswith("indice_tech:") or c.startswith("indice_tech:C("),
    "Educación madre": lambda c: c == "fami_educacionmadre",
    "Educación padre": lambda c: c == "fami_educacionpadre",
    "Composición hogar": lambda c: c in {"fami_cuartoshogar", "hacinamiento"},
    "Carácter": lambda c: c.startswith("C(cole_caracter)"),
    "Jornada": lambda c: c.startswith("C(cole_jornada)"),
    "Área": lambda c: c == "cole_area_ubicacion",
    "Naturaleza": lambda c: c == "cole_naturaleza",
    "Recursos del hogar": lambda c: c == "fami_tienelavadora",
    "Género": lambda c: c == "estu_genero",
}


@dataclass
class Tab3Prediction:
    brecha: float
    base: float
    contributions: dict[str, float]
    mat_est: float
    lec_est: float
    tech_effect: float
    rmse: float
    r2: float


@lru_cache(maxsize=1)
def load_tab3_metadata(metadata_path: Path | str = METADATA_PATH) -> dict[str, Any]:
    resolved_path = Path(metadata_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Tab 3 metadata not found at {resolved_path}")
    return json.loads(resolved_path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_tab3_model(model_path: Path | str = OLS_MODEL_PATH):
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("joblib is required to load the tab3 OLS model.") from exc

    resolved_path = Path(model_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Tab 3 OLS model not found at {resolved_path}")
    return joblib.load(resolved_path)


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(DEFAULT_TAB3_PAYLOAD)
    normalized.update({k: v for k, v in payload.items() if v is not None})
    normalized["fami_estrato"] = int(normalized["fami_estrato"])
    normalized["fami_personas"] = int(normalized["fami_personas"])
    normalized["fami_cuartos"] = int(normalized["fami_cuartos"])
    return normalized


def build_tab3_frame(payload: dict[str, Any]) -> pd.DataFrame:
    normalized = _normalize_payload(payload)
    tiene_internet = 1.0 if normalized["fami_internet"] in ("Si", "SI", 1, True) else 0.0
    tiene_computador = 1.0 if normalized["fami_computador"] in ("Si", "SI", 1, True) else 0.0
    punt_tecnologia = tiene_internet + tiene_computador

    row = {
        "fami_estratovivienda": float(normalized["fami_estrato"]),
        "indice_tech": float(punt_tecnologia),
        "fami_educacionmadre": EDUCATION_MAP.get(normalized["fami_educacionmadre"], 4.0),
        "fami_educacionpadre": EDUCATION_MAP.get(normalized["fami_educacionpadre"], 4.0),
        "fami_cuartoshogar": float(normalized["fami_cuartos"]),
        "hacinamiento": float(normalized["fami_personas"]) / max(float(normalized["fami_cuartos"]), 1.0),
        "fami_tienelavadora": 1.0,
        "cole_caracter": CARACTER_MAP.get(normalized["cole_caracter"], 3.0),
        "cole_jornada": JORNADA_MAP.get(normalized["cole_jornada"], 1),
        "cole_area_ubicacion": 1.0 if normalized["cole_area"] == "Urbana" else 0.0,
        "cole_naturaleza": 1.0 if normalized["cole_naturaleza"] == "Oficial" else 0.0,
        "estu_genero": 1.0,
    }
    return pd.DataFrame([row])


def predict_tab3_brecha(payload: dict[str, Any]) -> float:
    model = load_tab3_model()
    frame = build_tab3_frame(payload)
    return float(model.predict(frame).iloc[0])


def explain_tab3_prediction(
    payload: dict[str, Any],
    boyaca_math_avg: float,
    boyaca_reading_avg: float,
) -> Tab3Prediction:
    model = load_tab3_model()
    metadata = load_tab3_metadata()
    frame = build_tab3_frame(payload)

    prediction = float(model.predict(frame).iloc[0])
    design = build_design_matrices([model.model.data.design_info], frame, return_type="dataframe")[0]
    params = model.params

    base = float(params.get("Intercept", 0.0))
    contributions: dict[str, float] = {}

    for column in design.columns:
        if column == "Intercept":
            continue
        contribution = float(design.iloc[0][column] * params.get(column, 0.0))
        if abs(contribution) < 1e-9:
            continue
        for label, matcher in TAB3_GROUP_MAP.items():
            if matcher(column):
                contributions[label] = contributions.get(label, 0.0) + contribution
                break
        else:
            contributions["Otros"] = contributions.get("Otros", 0.0) + contribution

    row_no_tech = frame.copy()
    row_no_tech["indice_tech"] = 0.0
    row_no_tech["hacinamiento"] = row_no_tech["hacinamiento"]
    tech_prediction_without = float(model.predict(row_no_tech).iloc[0])
    tech_effect = prediction - tech_prediction_without

    mat_est = round(float(boyaca_math_avg + prediction / 2.0), 1)
    lec_est = round(float(boyaca_reading_avg - prediction / 2.0), 1)

    return Tab3Prediction(
        brecha=round(prediction, 1),
        base=round(base, 1),
        contributions={k: round(v, 1) for k, v in contributions.items()},
        mat_est=mat_est,
        lec_est=lec_est,
        tech_effect=round(tech_effect, 1),
        rmse=float(metadata.get("test_rmse", 8.0)),
        r2=float(metadata.get("test_r2", 0.05)),
    )
