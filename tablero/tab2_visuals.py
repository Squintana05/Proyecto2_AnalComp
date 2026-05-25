from __future__ import annotations

from typing import Any


def build_municipality_heat_figure(summary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    municipalities = [row["cole_mcpio_ubicacion"] for row in summary_rows]
    values = [round(float(row["promedio_ingles"]), 2) for row in summary_rows]
    counts = [int(row["total_estudiantes"]) for row in summary_rows]

    return {
        "data": [
            {
                "type": "bar",
                "x": municipalities,
                "y": values,
                "marker": {
                    "color": values,
                    "colorscale": [
                        [0.0, "#C94C4C"],
                        [0.5, "#E8B400"],
                        [1.0, "#009640"],
                    ],
                    "colorbar": {"title": "Promedio"},
                },
                "customdata": counts,
                "hovertemplate": (
                    "<b>%{x}</b><br>"
                    "Promedio Ingles: %{y}<br>"
                    "Estudiantes: %{customdata}<extra></extra>"
                ),
            }
        ],
        "layout": {
            "title": "Desempeno promedio en Ingles por municipio",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "margin": {"l": 40, "r": 20, "t": 52, "b": 90},
            "xaxis": {"tickangle": -60, "title": ""},
            "yaxis": {"title": "Puntaje promedio"},
        },
    }


def build_prediction_percentile_figure(percentile: float, probability: float) -> dict[str, Any]:
    return {
        "data": [
            {
                "type": "indicator",
                "mode": "gauge+number",
                "value": percentile,
                "number": {"suffix": " %", "font": {"size": 34}},
                "title": {"text": f"Percentil en Boyaca<br><span style='font-size:13px'>Probabilidad >58: {probability:.2%}</span>"},
                "gauge": {
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#003876"},
                    "steps": [
                        {"range": [0, 25], "color": "#fde8e8"},
                        {"range": [25, 50], "color": "#fff4d6"},
                        {"range": [50, 75], "color": "#e2f5ea"},
                        {"range": [75, 100], "color": "#ccebdc"},
                    ],
                },
            }
        ],
        "layout": {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "margin": {"l": 20, "r": 20, "t": 60, "b": 20},
        },
    }


def build_feature_impact_figure(feature_rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [row["feature"] for row in feature_rows]
    values = [float(row["importance"]) for row in feature_rows]

    return {
        "data": [
            {
                "type": "bar",
                "orientation": "h",
                "y": labels[::-1],
                "x": values[::-1],
                "marker": {
                    "color": values[::-1],
                    "colorscale": [
                        [0.0, "#dbe5ef"],
                        [0.4, "#7aa6d9"],
                        [0.7, "#1d5aa6"],
                        [1.0, "#003876"],
                    ],
                },
                "hovertemplate": "%{y}<br>Importancia: %{x:.4f}<extra></extra>",
            }
        ],
        "layout": {
            "title": "Variables con mayor impacto global en la clasificacion",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "margin": {"l": 150, "r": 20, "t": 52, "b": 30},
            "xaxis": {"title": "Importancia"},
            "yaxis": {"title": ""},
        },
    }
