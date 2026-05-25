from __future__ import annotations

import bisect
import json
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[1]
JQ_ARTIFACT_ROOT = REPO_ROOT / "ciencia_datos" / "ciencia_datosJQ"
RAW_DATA_PATH = PROJECT_ROOT / "cleaned_data.csv"
ENCODED_DATA_PATH = PROJECT_ROOT / "data_encoded.csv"
ARTIFACT_DIR = Path(__file__).resolve().parent / "model_artifacts" / "tab2_english_classifier"
MLFLOW_MODEL_ID = "m-f8c8b4101ab8411c9d940e522be6e20e"
MLFLOW_RUN_ID = "d21d9791d9ce46a39a667d2075ec7cc4"
MODEL_ARTIFACT_DIR = JQ_ARTIFACT_ROOT / "mlartifacts" / "4" / "models" / MLFLOW_MODEL_ID / "artifacts"
PREPROCESSING_ARTIFACT_DIR = JQ_ARTIFACT_ROOT / "mlartifacts" / "4" / MLFLOW_RUN_ID / "artifacts" / "preprocessing"
MODEL_PATH = MODEL_ARTIFACT_DIR / "data" / "model.keras"
SCALER_PATH = PREPROCESSING_ARTIFACT_DIR / "final_scaler.pkl"
BUNDLE_PATH = ARTIFACT_DIR / "tab2_bundle.json"
MUNICIPALITY_SUMMARY_PATH = ARTIFACT_DIR / "municipality_summary.csv"
FEATURE_IMPORTANCE_PATH = ARTIFACT_DIR / "feature_importance.csv"
BOYACA_GEOJSON_PATH = Path(__file__).resolve().parent / "data" / "boyaca_municipios.geojson"

TARGET_THRESHOLD = 58
TARGET_LABELS = {
    0: "<=58",
    1: ">58",
}

# Best validation configuration found in MLflow for experiment pregunta2_ff-boyaca.
BEST_VALIDATION_CONFIG = {
    "run_uuid": "3ba27b3195e64278b196da97039ebfd8",
    "batch_size": 64,
    "dropout_rate": 0.2,
    "epochs": 5,
    "hidden_layers": (16, 24, 8),
    "learning_rate": 0.001,
    "mean_f1_macro": 0.6722291890485284,
}

# Best completed test run available in MLflow.
BEST_TRAINED_RUN = {
    "run_uuid": "daba2adc05524dd39280a20d8d166a49",
    "batch_size": 64,
    "dropout_rate": 0.2,
    "epochs": 5,
    "hidden_layers": (8, 8, 16),
    "learning_rate": 0.001,
    "test_f1_macro": 0.6804054231249307,
    "test_cross_entropy": 0.5305829651525006,
}

# Raw-to-encoded mappings inferred directly from cleaned_data.csv and data_encoded.csv.
RAW_TO_MODEL_MAPS: dict[str, dict[Any, Any]] = {
    "cole_area_ubicacion": {
        "RURAL": 0,
        "URBANO": 1,
        "Rural": 0,
        "Urbana": 1,
        "Urbano": 1,
    },
    "cole_bilingue": {
        "N": 0,
        "S": 1,
        "No": 0,
        "Si": 1,
        "SI": 1,
        "NO": 0,
    },
    "cole_caracter": {
        "TÉCNICO": 1,
        "Tecnico": 1,
        "Técnico": 1,
        "TÉCNICO/ACADÉMICO": 2,
        "Tecnico/Academico": 2,
        "Técnico/Académico": 2,
        "ACADÉMICO": 3,
        "Academico": 3,
        "Académico": 3,
        "NO APLICA": 4,
        "No aplica": 4,
    },
    "cole_jornada": {
        "MAÑANA": 1,
        "Manana": 1,
        "Mañana": 1,
        "TARDE": 2,
        "Tarde": 2,
        "NOCHE": 3,
        "Noche": 3,
        "SABATINA": 4,
        "Sabatina": 4,
        "UNICA": 5,
        "Unica": 5,
        "Única": 5,
        "COMPLETA": 6,
        "Completa": 6,
    },
    "cole_naturaleza": {
        "NO OFICIAL": 0,
        "No oficial": 0,
        "OFICIAL": 1,
        "Oficial": 1,
    },
    "fami_tienecomputador": {
        "No": 0.0,
        "Si": 1.0,
        "NO": 0.0,
        "SI": 1.0,
    },
    "fami_tieneinternet": {
        "No": 0.0,
        "Si": 1.0,
        "NO": 0.0,
        "SI": 1.0,
    },
    "fami_estratovivienda": {
        "Sin Estrato": 0.0,
        "Estrato 1": 1.0,
        "Estrato 2": 2.0,
        "Estrato 3": 3.0,
        "Estrato 4": 4.0,
        "Estrato 5": 5.0,
        "Estrato 6": 6.0,
        0: 0.0,
        1: 1.0,
        2: 2.0,
        3: 3.0,
        4: 4.0,
        5: 5.0,
        6: 6.0,
    },
    "fami_educacionmadre": {
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
    },
    "fami_educacionpadre": {
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
    },
}

TAB2_REQUIRED_FIELDS = [
    "cole_bilingue",
    "cole_jornada",
    "cole_area_ubicacion",
    "cole_naturaleza",
    "cole_caracter",
    "cole_mcpio_ubicacion",
    "fami_tienecomputador",
    "fami_tieneinternet",
    "fami_estratovivienda",
    "fami_educacionmadre",
    "fami_educacionpadre",
    "fami_personashogar",
    "fami_cuartoshogar",
]

JORNADA_ONE_HOT_VALUES = [1, 2, 3, 4, 5, 6]
CARACTER_ONE_HOT_VALUES = [1, 2, 3, 4]

# The notebook accidentally repeats cole_area_ubicacion in the feature matrix.
# We preserve that duplicate here to stay consistent with the trained model.
MODEL_INPUT_COLUMNS = [
    "cole_bilingue",
    "cole_area_ubicacion",
    "cole_naturaleza",
    "cole_area_ubicacion_dup",
    "fami_tienecomputador",
    "fami_tieneinternet",
    "fami_estratovivienda",
    "nivel_educacion_padres",
    "hacinamiento",
    "cole_jornada_1",
    "cole_jornada_2",
    "cole_jornada_3",
    "cole_jornada_4",
    "cole_jornada_5",
    "cole_jornada_6",
    "cole_caracter_1",
    "cole_caracter_2",
    "cole_caracter_3",
    "cole_caracter_4",
]


@dataclass
class Tab2Bundle:
    feature_order: list[str]
    scaler_mean: list[float]
    scaler_scale: list[float]
    probability_reference: list[float]
    target_threshold: int = TARGET_THRESHOLD

    @classmethod
    def from_path(cls, path: Path | str = BUNDLE_PATH) -> "Tab2Bundle":
        bundle_path = Path(path)
        if bundle_path.exists():
            payload = json.loads(bundle_path.read_text(encoding="utf-8"))
            return cls(
                feature_order=payload["feature_order"],
                scaler_mean=payload["scaler_mean"],
                scaler_scale=payload["scaler_scale"],
                probability_reference=payload.get("probability_reference", []),
                target_threshold=payload.get("target_threshold", TARGET_THRESHOLD),
            )

        scaler = load_tab2_scaler()
        return cls(
            feature_order=list(scaler.feature_names_in_),
            scaler_mean=scaler.mean_.astype(float).tolist(),
            scaler_scale=scaler.scale_.astype(float).tolist(),
            probability_reference=build_tab2_probability_reference(),
            target_threshold=TARGET_THRESHOLD,
        )


@lru_cache(maxsize=1)
def load_tab2_model(model_path: Path | str = MODEL_PATH):
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError(
            "TensorFlow is required to run the tab2 English model."
        ) from exc

    resolved_path = Path(model_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Tab 2 model artifact not found at {resolved_path}")
    return tf.keras.models.load_model(resolved_path)


@lru_cache(maxsize=1)
def load_tab2_scaler(scaler_path: Path | str = SCALER_PATH):
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError(
            "joblib is required to load the tab2 preprocessing artifacts."
        ) from exc

    resolved_path = Path(scaler_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Tab 2 scaler artifact not found at {resolved_path}")
    return joblib.load(resolved_path)


def _coerce_numeric(value: Any) -> float:
    if value is None or value == "":
        raise ValueError("Missing numeric value required by tab2 model.")
    return float(value)


def normalize_municipality_name(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _encode_value(field: str, value: Any) -> Any:
    mapping = RAW_TO_MODEL_MAPS.get(field)
    if mapping is None:
        return value
    if value in mapping:
        return mapping[value]
    raise ValueError(f"Unsupported value for {field}: {value!r}")


def encode_dashboard_payload(payload: dict[str, Any]) -> dict[str, float]:
    missing = [field for field in TAB2_REQUIRED_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Missing required tab2 fields: {', '.join(missing)}")

    encoded = {
        "cole_bilingue": float(_encode_value("cole_bilingue", payload["cole_bilingue"])),
        "cole_jornada": int(_encode_value("cole_jornada", payload["cole_jornada"])),
        "cole_area_ubicacion": float(_encode_value("cole_area_ubicacion", payload["cole_area_ubicacion"])),
        "cole_naturaleza": float(_encode_value("cole_naturaleza", payload["cole_naturaleza"])),
        "cole_caracter": int(_encode_value("cole_caracter", payload["cole_caracter"])),
        "fami_tienecomputador": float(_encode_value("fami_tienecomputador", payload["fami_tienecomputador"])),
        "fami_tieneinternet": float(_encode_value("fami_tieneinternet", payload["fami_tieneinternet"])),
        "fami_estratovivienda": float(_encode_value("fami_estratovivienda", payload["fami_estratovivienda"])),
        "fami_educacionmadre": float(_encode_value("fami_educacionmadre", payload["fami_educacionmadre"])),
        "fami_educacionpadre": float(_encode_value("fami_educacionpadre", payload["fami_educacionpadre"])),
        "fami_personashogar": _coerce_numeric(payload["fami_personashogar"]),
        "fami_cuartoshogar": _coerce_numeric(payload["fami_cuartoshogar"]),
    }

    encoded["nivel_educacion_padres"] = round(
        (encoded["fami_educacionmadre"] + encoded["fami_educacionpadre"]) / 2.0, 0
    )
    encoded["hacinamiento"] = encoded["fami_personashogar"] / (encoded["fami_cuartoshogar"] + 1.0)
    return encoded


def build_model_vector(encoded_payload: dict[str, float]) -> list[float]:
    vector = {
        "cole_bilingue": encoded_payload["cole_bilingue"],
        "cole_area_ubicacion": encoded_payload["cole_area_ubicacion"],
        "cole_naturaleza": encoded_payload["cole_naturaleza"],
        "cole_area_ubicacion_dup": encoded_payload["cole_area_ubicacion"],
        "fami_tienecomputador": encoded_payload["fami_tienecomputador"],
        "fami_tieneinternet": encoded_payload["fami_tieneinternet"],
        "fami_estratovivienda": encoded_payload["fami_estratovivienda"],
        "nivel_educacion_padres": encoded_payload["nivel_educacion_padres"],
        "hacinamiento": encoded_payload["hacinamiento"],
    }

    for value in JORNADA_ONE_HOT_VALUES:
        vector[f"cole_jornada_{value}"] = 1.0 if encoded_payload["cole_jornada"] == value else 0.0

    for value in CARACTER_ONE_HOT_VALUES:
        vector[f"cole_caracter_{value}"] = 1.0 if encoded_payload["cole_caracter"] == value else 0.0

    return [float(vector[column]) for column in MODEL_INPUT_COLUMNS]


def scale_model_vector(vector: list[float], bundle: Tab2Bundle) -> list[float]:
    if len(vector) != len(bundle.scaler_mean) or len(vector) != len(bundle.scaler_scale):
        raise ValueError("Vector size does not match scaler statistics from tab2 bundle.")

    scaled = []
    for value, mean, scale in zip(vector, bundle.scaler_mean, bundle.scaler_scale):
        scaled.append((value - mean) / scale if scale not in (0, 0.0) else value - mean)
    return scaled


def build_tab2_feature_frame(csv_path: Path | str = ENCODED_DATA_PATH):
    import pandas as pd

    data = pd.read_csv(csv_path)
    data["nivel_educacion_padres"] = round((data["fami_educacionmadre"] + data["fami_educacionpadre"]) / 2, 0)
    data["hacinamiento"] = data["fami_personashogar"] / (data["fami_cuartoshogar"] + 1)

    selected = data[
        [
            "cole_bilingue",
            "cole_jornada",
            "cole_area_ubicacion",
            "cole_naturaleza",
            "cole_caracter",
            "fami_tienecomputador",
            "fami_tieneinternet",
            "fami_estratovivienda",
            "nivel_educacion_padres",
            "hacinamiento",
        ]
    ].copy()

    frame = selected.dropna()
    frame = frame[~frame.isin([-1, "-1"]).any(axis=1)].copy()

    feature_frame = pd.DataFrame(index=frame.index)
    feature_frame["cole_bilingue"] = frame["cole_bilingue"].astype(float)
    feature_frame["cole_area_ubicacion"] = frame["cole_area_ubicacion"].astype(float)
    feature_frame["cole_naturaleza"] = frame["cole_naturaleza"].astype(float)
    feature_frame["cole_area_ubicacion_dup"] = frame["cole_area_ubicacion"].astype(float)
    feature_frame["fami_tienecomputador"] = frame["fami_tienecomputador"].astype(float)
    feature_frame["fami_tieneinternet"] = frame["fami_tieneinternet"].astype(float)
    feature_frame["fami_estratovivienda"] = frame["fami_estratovivienda"].astype(float)
    feature_frame["nivel_educacion_padres"] = frame["nivel_educacion_padres"].astype(float)
    feature_frame["hacinamiento"] = frame["hacinamiento"].astype(float)

    jornada_values = frame["cole_jornada"].astype(int)
    caracter_values = frame["cole_caracter"].astype(int)

    for value in JORNADA_ONE_HOT_VALUES:
        feature_frame[f"cole_jornada_{value}"] = (jornada_values == value).astype(int)

    for value in CARACTER_ONE_HOT_VALUES:
        feature_frame[f"cole_caracter_{value}"] = (caracter_values == value).astype(int)

    feature_frame = feature_frame.reindex(columns=MODEL_INPUT_COLUMNS, fill_value=0)
    return feature_frame.astype("float32")


@lru_cache(maxsize=1)
def build_tab2_probability_reference() -> list[float]:
    try:
        import numpy as np
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError("NumPy is required to build the tab2 probability reference.") from exc

    scaler = load_tab2_scaler()
    model = load_tab2_model()
    feature_frame = build_tab2_feature_frame()
    scaler_input = pd.DataFrame(
        feature_frame.to_numpy(dtype="float32"),
        columns=list(scaler.feature_names_in_),
    )
    scaled = scaler.transform(scaler_input)
    probabilities = model(np.asarray(scaled, dtype="float32"), training=False).numpy()[:, 1]
    return probabilities.astype(float).tolist()


def predict_tab2_probability(payload: dict[str, Any], bundle_path: Path | str = BUNDLE_PATH, model_path: Path | str = MODEL_PATH) -> float:
    try:
        import numpy as np
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "NumPy is required to run the tab2 English model. "
            "Export the trained artifact from the notebook environment first."
        ) from exc

    bundle = Tab2Bundle.from_path(bundle_path)
    encoded = encode_dashboard_payload(payload)
    vector = build_model_vector(encoded)
    scaler = load_tab2_scaler()
    feature_frame = pd.DataFrame([vector], columns=list(scaler.feature_names_in_), dtype="float32")
    scaled = scaler.transform(feature_frame)[0]

    model = load_tab2_model(model_path)
    probability = model(np.asarray([scaled], dtype="float32"), training=False).numpy()[0][1]
    return float(probability)


def probability_to_percentile(probability: float, reference: list[float]) -> float:
    if not reference:
        raise ValueError("Probability reference distribution is empty.")
    ordered = sorted(float(value) for value in reference)
    position = bisect.bisect_right(ordered, probability)
    return round((position / len(ordered)) * 100.0, 2)


def build_tab2_municipality_summary(csv_path: Path | str = RAW_DATA_PATH):
    import pandas as pd

    df = pd.read_csv(csv_path)
    working = df[
        [
            "cole_mcpio_ubicacion",
            "punt_ingles",
        ]
    ].copy()
    working = working.dropna()
    working["supera_umbral"] = (working["punt_ingles"] > TARGET_THRESHOLD).astype(int)

    summary = (
        working.groupby("cole_mcpio_ubicacion", as_index=False)
        .agg(
            promedio_ingles=("punt_ingles", "mean"),
            tasa_supera_58=("supera_umbral", "mean"),
            total_estudiantes=("punt_ingles", "size"),
        )
        .sort_values(["promedio_ingles", "total_estudiantes"], ascending=[False, False])
        .reset_index(drop=True)
    )
    return summary


def build_boyaca_percentile_reference(csv_path: Path | str = RAW_DATA_PATH) -> list[float]:
    import pandas as pd

    df = pd.read_csv(csv_path, usecols=["punt_ingles"]).dropna()
    return df["punt_ingles"].astype(float).tolist()


@lru_cache(maxsize=1)
def load_boyaca_geojson(path: Path | str = BOYACA_GEOJSON_PATH) -> dict[str, Any]:
    geojson_path = Path(path)
    if not geojson_path.exists():
        raise FileNotFoundError(f"Boyacá GeoJSON not found at {geojson_path}")
    geojson = json.loads(geojson_path.read_text(encoding="utf-8"))
    for feature in geojson.get("features", []):
        feature.setdefault("properties", {})
        feature["properties"]["MUNICIPIO_NORM"] = normalize_municipality_name(
            feature["properties"].get("NOMBRE_MPI")
        )
    return geojson


def _flatten_coordinates(geometry: dict[str, Any]) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []
    geom_type = geometry.get("type")
    raw_coords = geometry.get("coordinates", [])

    def visit(node):
        if isinstance(node, (list, tuple)) and node:
            if isinstance(node[0], (int, float)) and len(node) >= 2:
                coords.append((float(node[0]), float(node[1])))
            else:
                for child in node:
                    visit(child)

    if geom_type in {"Polygon", "MultiPolygon"}:
        visit(raw_coords)
    return coords


@lru_cache(maxsize=1)
def build_boyaca_centroids(path: Path | str = BOYACA_GEOJSON_PATH) -> dict[str, dict[str, float]]:
    geojson = load_boyaca_geojson(path)
    centroids: dict[str, dict[str, float]] = {}

    for feature in geojson.get("features", []):
        name = normalize_municipality_name(feature["properties"].get("NOMBRE_MPI"))
        points = _flatten_coordinates(feature.get("geometry", {}))
        if not points:
            continue
        longitudes = [point[0] for point in points]
        latitudes = [point[1] for point in points]
        centroids[name] = {
            "lon": sum(longitudes) / len(longitudes),
            "lat": sum(latitudes) / len(latitudes),
        }

    return centroids


@lru_cache(maxsize=1)
def load_tab2_municipality_summary() :
    import pandas as pd

    summary = build_tab2_municipality_summary().copy()
    summary["municipio_normalizado"] = summary["cole_mcpio_ubicacion"].map(normalize_municipality_name)
    summary = (
        summary.groupby("municipio_normalizado", as_index=False)
        .agg(
            promedio_ingles=("promedio_ingles", "mean"),
            tasa_supera_58=("tasa_supera_58", "mean"),
            total_estudiantes=("total_estudiantes", "sum"),
        )
    )

    centroids = build_boyaca_centroids()
    summary["display_name"] = summary["municipio_normalizado"].str.title()
    summary["lat"] = summary["municipio_normalizado"].map(lambda name: centroids.get(name, {}).get("lat"))
    summary["lon"] = summary["municipio_normalizado"].map(lambda name: centroids.get(name, {}).get("lon"))
    summary = summary.dropna(subset=["lat", "lon"]).reset_index(drop=True)
    return summary
