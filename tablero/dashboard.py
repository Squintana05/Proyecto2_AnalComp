from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
import plotly.graph_objects as go

from tab2_model import (
    TARGET_LABELS,
    Tab2Bundle,
    load_boyaca_geojson,
    load_tab2_municipality_summary,
    normalize_municipality_name,
    predict_tab2_probability,
    probability_to_percentile,
)


app = Dash(__name__)
app.title = "Saber 11 Boyacá"


COLORS = {
    "primary": "#003876",
    "secondary": "#009640",
    "accent": "#E8B400",
    "background": "#F0F4F8",
    "surface": "#FFFFFF",
    "text": "#1A2B3C",
    "muted": "#6B7C93",
    "border": "#DDE3EA",
    "blue": "#1D5AA6",
    "green": "#0C8B5F",
    "gold": "#D8A31A",
    "red": "#C94C4C",
}


CARD_STYLE = {
    "backgroundColor": COLORS["surface"],
    "borderRadius": "14px",
    "padding": "24px",
    "boxShadow": "0 2px 14px rgba(0, 0, 0, 0.06)",
    "border": f"1px solid {COLORS['border']}",
}


LABEL_STYLE = {
    "display": "block",
    "fontSize": "11px",
    "fontWeight": "700",
    "letterSpacing": "0.08em",
    "textTransform": "uppercase",
    "color": COLORS["muted"],
    "marginBottom": "8px",
}


INPUT_STYLE = {
    "fontSize": "14px",
    "borderRadius": "10px",
}


def rgba_from_hex(hex_color, alpha):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return hex_color
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    return f"rgba({red}, {green}, {blue}, {alpha})"


TAB_STYLE = {
    "padding": "16px 22px",
    "fontFamily": '"Segoe UI", sans-serif',
    "fontSize": "13px",
    "fontWeight": "700",
    "letterSpacing": "0.04em",
    "color": COLORS["muted"],
    "backgroundColor": COLORS["background"],
    "border": "none",
    "borderBottom": f"2px solid {COLORS['border']}",
    "borderTopLeftRadius": "14px",
    "borderTopRightRadius": "14px",
}


TAB_SELECTED_STYLE = {
    **TAB_STYLE,
    "color": "#FFFFFF",
    "background": "linear-gradient(90deg, #009640 0%, #77A83F 45%, #C94C4C 100%)",
    "borderBottom": "none",
    "boxShadow": "0 8px 20px rgba(0, 0, 0, 0.10)",
}


def etiqueta(texto, color):
    return html.Span(
        texto,
        style={
            "display": "inline-block",
            "padding": "6px 12px",
            "borderRadius": "999px",
            "fontSize": "11px",
            "fontWeight": "700",
            "letterSpacing": "0.05em",
            "textTransform": "uppercase",
            "backgroundColor": color,
            "color": "white",
            "marginRight": "8px",
            "marginBottom": "8px",
        },
    )


def tarjeta_texto(titulo, texto, borde, subtitulo=None, class_name=""):
    children = [
        html.Div(
            titulo,
            style={
                "fontSize": "11px",
                "fontWeight": "700",
                "letterSpacing": "0.08em",
                "textTransform": "uppercase",
                "color": COLORS["muted"],
                "marginBottom": "6px",
            },
        )
    ]

    if subtitulo:
        children.append(
            html.Div(
                subtitulo,
                style={
                    "fontSize": "24px",
                    "fontWeight": "800",
                    "color": borde,
                    "lineHeight": "1",
                    "marginBottom": "4px",
                },
            )
        )

    children.append(
        html.P(
            texto,
            style={
                "margin": "0",
                "color": COLORS["text"],
                "fontSize": "14px",
                "lineHeight": "1.55",
            },
        )
    )

    return html.Div(
        children,
        className=f"tab-summary-card {class_name}".strip(),
        style={
            **CARD_STYLE,
            "borderTop": f"3px solid {borde}",
            "height": "100%",
            "minHeight": "0",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "flex-start",
            "padding": "12px 16px",
        },
    )


def tarjeta_kpi(titulo, valor, texto, color, acento):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        titulo,
                        style={
                            "fontSize": "11px",
                            "fontWeight": "800",
                            "letterSpacing": "0.10em",
                            "textTransform": "uppercase",
                            "color": COLORS["muted"],
                        },
                    ),
                    html.Span(
                        acento,
                        style={
                            "display": "inline-flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "minWidth": "32px",
                            "height": "32px",
                            "borderRadius": "9px",
                            "background": f"linear-gradient(135deg, {color} 0%, {COLORS['primary']} 100%)",
                            "color": "white",
                            "fontSize": "14px",
                            "fontWeight": "800",
                            "boxShadow": "0 6px 14px rgba(0, 56, 118, 0.14)",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "gap": "12px",
                    "marginBottom": "8px",
                },
            ),
            html.Div(
                valor,
                style={
                    "fontSize": "36px",
                    "fontWeight": "900",
                    "lineHeight": "1",
                    "color": color,
                    "marginBottom": "6px",
                },
            ),
            html.P(
                texto,
                style={
                    "margin": "0",
                    "color": COLORS["text"],
                    "fontSize": "13px",
                    "lineHeight": "1.45",
                },
            ),
        ],
        className="kpi-card",
        style={
            **CARD_STYLE,
            "borderTop": f"4px solid {color}",
            "minHeight": "110px",
            "padding": "14px 16px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
        },
    )


def campo_dropdown(label, options, placeholder, component_id=None, default_value=None):
    dropdown_kwargs = {
        "options": [{"label": option, "value": option} for option in options],
        "placeholder": placeholder,
        "clearable": False,
        "style": INPUT_STYLE,
    }
    if placeholder is None:
        dropdown_kwargs.pop("placeholder", None)
    if component_id is not None:
        dropdown_kwargs["id"] = component_id
    if default_value is not None:
        dropdown_kwargs["value"] = default_value
    return html.Div(
        [
            html.Label(label, style=LABEL_STYLE),
            dcc.Dropdown(**dropdown_kwargs),
        ]
    )


def campo_formulario(field):
    if isinstance(field, dict):
        tipo = field.get("tipo", "dropdown")
        label = field["label"]
        component_id = field.get("id")

        if tipo == "radio":
            radio_kwargs = {
                "options": field["options"],
                "value": field.get("value"),
                "className": field.get("className", "radio-choice-group"),
                "inline": field.get("inline", True),
            }
            if component_id is not None:
                radio_kwargs["id"] = component_id
            return html.Div(
                [
                    html.Label(label, style=LABEL_STYLE),
                    dcc.RadioItems(**radio_kwargs),
                ]
            )

        if tipo == "slider":
            slider_kwargs = {
                "min": field.get("min", 1),
                "max": field.get("max", 10),
                "step": field.get("step", 1),
                "value": field.get("value", 5),
                "marks": field.get("marks"),
                "tooltip": {"placement": "bottom", "always_visible": True},
                "className": field.get("className", "numeric-slider"),
            }
            if component_id is not None:
                slider_kwargs["id"] = component_id
            return html.Div(
                [
                    html.Label(label, style=LABEL_STYLE),
                    html.Div(
                        [
                            dcc.Slider(**slider_kwargs)
                        ],
                        className="slider-shell",
                    ),
                ]
            )

        if tipo == "icon_scale":
            icon_scale_kwargs = {
                "options": field["options"],
                "value": field.get("value"),
                "className": field.get("className", "icon-scale-group"),
                "inputClassName": "segmented-control-input",
                "labelClassName": "segmented-control-label",
                "inline": field.get("inline", True),
            }
            if component_id is not None:
                icon_scale_kwargs["id"] = component_id
            return html.Div(
                [
                    html.Label(label, style=LABEL_STYLE),
                    dcc.RadioItems(**icon_scale_kwargs),
                ]
            )

        if tipo == "dual_icon_scale":
            first_kwargs = {
                "options": field["first_options"],
                "value": field.get("first_value"),
                "className": field.get("first_className", "icon-scale-group"),
                "inputClassName": "segmented-control-input",
                "labelClassName": "segmented-control-label",
                "inline": True,
            }
            second_kwargs = {
                "options": field["second_options"],
                "value": field.get("second_value"),
                "className": field.get("second_className", "icon-scale-group"),
                "inputClassName": "segmented-control-input",
                "labelClassName": "segmented-control-label",
                "inline": True,
            }
            if field.get("first_id") is not None:
                first_kwargs["id"] = field.get("first_id")
            if field.get("second_id") is not None:
                second_kwargs["id"] = field.get("second_id")
            return html.Div(
                [
                    html.Label(label, style=LABEL_STYLE),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(field["first_label"], className="dual-scale-subtitle"),
                                    dcc.RadioItems(**first_kwargs),
                                ],
                                className="dual-scale-block",
                            ),
                            html.Div(
                                [
                                    html.Div(field["second_label"], className="dual-scale-subtitle"),
                                    dcc.RadioItems(**second_kwargs),
                                ],
                                className="dual-scale-block",
                            ),
                        ],
                        className="dual-scale-card",
                    ),
                ]
            )

        return campo_dropdown(
            label,
            field["options"],
            field.get("placeholder", "Seleccione una opcion"),
            component_id,
            field.get("value"),
        )

    label, options, placeholder = field
    return campo_dropdown(label, options, placeholder)


def grupo_formulario(titulo, color, campos, descripcion=None, class_name=""):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        titulo,
                        className="form-section-title",
                        style={"color": color},
                    ),
                    html.P(descripcion, className="form-section-description") if descripcion else None,
                ],
                style={"marginBottom": "16px"},
            ),
            html.Div(
                [campo_formulario(field) for field in campos],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                    "gap": "14px",
                },
            ),
        ],
        className=f"form-group-card {class_name}".strip(),
        style={
            **CARD_STYLE,
            "borderLeft": f"5px solid {color}",
            "height": "100%",
        },
    )


def grupo_formulario_columnas(titulo, color, campos, columnas=3, descripcion=None, class_name=""):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        titulo,
                        className="form-section-title",
                        style={"color": color},
                    ),
                    html.P(descripcion, className="form-section-description") if descripcion else None,
                ],
                style={"marginBottom": "16px"},
            ),
            html.Div(
                [campo_formulario(field) for field in campos],
                style={
                    "display": "grid",
                    "gridTemplateColumns": f"repeat({columnas}, minmax(0, 1fr))",
                    "gap": "14px",
                },
            ),
        ],
        className=f"form-group-card {class_name}".strip(),
        style={
            **CARD_STYLE,
            "borderLeft": f"5px solid {color}",
            "height": "100%",
        },
    )


def secciones_formulario_renderizadas(config):
    if "form_sections" in config:
        sections = config["form_sections"]
    else:
        sections = [
            ("Perfil del estudiante", config["student_fields"]),
            ("Condiciones del hogar", config["home_fields"]),
            ("Características institucionales", config["school_fields"]),
            ("Variables académicas disponibles", config["academic_fields"]),
        ]

    rendered = []
    for section in sections:
        if isinstance(section, dict):
            if section["campos"]:
                rendered.append(
                    grupo_formulario_columnas(
                        section["titulo"],
                        config["color"],
                        section["campos"],
                        section.get("columnas", 3),
                        section.get("descripcion"),
                        section.get("className", ""),
                    )
                )
        else:
            titulo, campos = section
            if campos:
                rendered.append(grupo_formulario(titulo, config["color"], campos))

    return rendered


def tarjeta_resultado(titulo, valor, detalle, color, grande=False, value_id=None, detail_id=None):
    value_kwargs = {
        "style": {
            "fontSize": "40px" if grande else "24px",
            "fontWeight": "800",
            "lineHeight": "1.05",
            "color": color,
            "marginBottom": "12px",
        }
    }
    detail_kwargs = {
        "style": {
            "margin": "0",
            "color": COLORS["text"],
            "fontSize": "14px",
            "lineHeight": "1.6",
        }
    }
    if value_id is not None:
        value_kwargs["id"] = value_id
    if detail_id is not None:
        detail_kwargs["id"] = detail_id
    return html.Div(
        [
            html.Div(
                titulo,
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "letterSpacing": "0.08em",
                    "textTransform": "uppercase",
                    "color": COLORS["muted"],
                    "marginBottom": "10px",
                },
            ),
            html.Div(valor, **value_kwargs),
            html.Div(detalle, **detail_kwargs),
        ],
        style={
            **CARD_STYLE,
            "borderTop": f"4px solid {color}",
            "height": "100%",
            "background": "linear-gradient(180deg, #FFFFFF 0%, #F9FBFD 100%)",
        },
    )


def tarjeta_lista(titulo, items, color):
    return html.Div(
        [
            html.Div(
                titulo,
                style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "letterSpacing": "0.08em",
                    "textTransform": "uppercase",
                    "color": COLORS["muted"],
                    "marginBottom": "12px",
                },
            ),
            html.Ul(
                [html.Li(item, style={"marginBottom": "10px"}) for item in items],
                style={
                    "margin": "0",
                    "paddingLeft": "18px",
                    "color": COLORS["text"],
                    "fontSize": "15px",
                    "lineHeight": "1.7",
                },
            ),
        ],
        style={
            **CARD_STYLE,
            "borderTop": f"4px solid {color}",
            "height": "100%",
        },
    )


def boton_prediccion(color, button_id=None):
    button_kwargs = {
        "style": {
            "background": f"linear-gradient(135deg, {COLORS['primary']} 0%, {color} 100%)",
            "color": "white",
            "fontSize": "15px",
            "fontWeight": "700",
            "border": "none",
            "borderRadius": "12px",
            "padding": "16px 24px",
            "cursor": "pointer",
            "boxShadow": "0 8px 20px rgba(0, 56, 118, 0.18)",
            "width": "100%",
            "maxWidth": "320px",
        }
    }
    if button_id is not None:
        button_kwargs["id"] = button_id
    return html.Button("Calcular predicción", **button_kwargs)


def boton_secundario(texto, button_id=None):
    button_kwargs = {
        "style": {
            "background": "#FFFFFF",
            "color": COLORS["primary"],
            "fontSize": "15px",
            "fontWeight": "700",
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "12px",
            "padding": "16px 24px",
            "cursor": "pointer",
            "boxShadow": "0 4px 10px rgba(0, 56, 118, 0.08)",
            "width": "100%",
            "maxWidth": "320px",
        }
    }
    if button_id is not None:
        button_kwargs["id"] = button_id
    return html.Button(texto, **button_kwargs)


def visual_binario_ingles():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        "Visual de clasificación",
                        style={
                            "fontSize": "12px",
                            "fontWeight": "800",
                            "letterSpacing": "0.08em",
                            "textTransform": "uppercase",
                            "color": COLORS["green"],
                            "marginBottom": "10px",
                        },
                    ),
                    html.H3(
                        "Umbral de desempeño en Inglés",
                        style={
                            "margin": "0 0 10px",
                            "fontSize": "24px",
                            "fontWeight": "800",
                            "color": COLORS["primary"],
                        },
                    ),
                    html.P(
                        "El modelo se evalúa como clasificación binaria. Los perfiles con resultado "
                        "menor o igual a 58 quedan en la zona izquierda y los mayores a 58 se "
                        "ubican en la zona derecha.",
                        style={
                            "margin": "0",
                            "color": COLORS["text"],
                            "fontSize": "15px",
                            "lineHeight": "1.7",
                        },
                    ),
                ],
                style={"marginBottom": "18px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("No alcanza el nivel de desempeño", className="binary-level-title"),
                            html.Div("Nivel Inglés menor que A2", className="binary-level-range"),
                            html.Div("<A2", className="binary-level-class"),
                        ],
                        className="binary-level-card binary-left",
                    ),
                    html.Div(
                        [
                            html.Div("Puntaje", className="binary-threshold-label"),
                            html.Div("58", className="binary-threshold-value"),
                        ],
                        className="binary-threshold-card",
                    ),
                    html.Div(
                        [
                            html.Div("Supera nivel de desempeño", className="binary-level-title"),
                            html.Div("Nivel Inglés mayor o igual a A2", className="binary-level-range"),
                            html.Div("A2>", className="binary-level-class"),
                        ],
                        className="binary-level-card binary-right",
                    ),
                    html.Div(
                        [
                            html.Div("Resultado del modelo", className="binary-indicator-label"),
                            html.Div("Pendiente", id="tab2-binary-indicator-value", className="binary-indicator-value"),
                        ],
                        id="tab2-binary-indicator",
                        className="binary-indicator binary-indicator-center",
                        style={
                            "background": "linear-gradient(135deg, #8a94a6 0%, #64748b 100%)",
                            "left": "50%",
                        },
                    ),
                ],
                className="binary-scale-wrapper",
            ),
            html.Div(
                [
                    html.Div(
                        "Cuando el modelo esté conectado, este marcador se moverá automáticamente "
                        "hacia la izquierda o hacia la derecha según la clase predicha.",
                        style={
                            "fontSize": "14px",
                            "color": COLORS["muted"],
                            "lineHeight": "1.6",
                        },
                    )
                ],
                style={"marginTop": "18px"},
            ),
        ],
        className="binary-visual-card",
        style={
            **CARD_STYLE,
            "marginBottom": "22px",
            "background": "linear-gradient(135deg, #FFFFFF 0%, #F7FBFF 100%)",
        },
    )


def barra_estado_tab2():
    return html.Div(
        [
            html.Div(
                "Modelo listo para una nueva consulta",
                id="tab2-status-text",
                style={
                    "fontSize": "13px",
                    "fontWeight": "700",
                    "color": COLORS["primary"],
                    "marginBottom": "10px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        id="tab2-status-fill",
                        style={
                            "width": "18%",
                            "height": "100%",
                            "borderRadius": "999px",
                            "background": "linear-gradient(90deg, #8a94a6 0%, #64748b 100%)",
                            "transition": "width 0.35s ease, background 0.35s ease",
                        },
                    )
                ],
                style={
                    "width": "100%",
                    "height": "12px",
                    "borderRadius": "999px",
                    "overflow": "hidden",
                    "background": "#E2E8F0",
                    "border": f"1px solid {COLORS['border']}",
                },
            ),
        ],
        style={
            **CARD_STYLE,
            "padding": "16px 18px",
            "marginBottom": "22px",
            "background": "linear-gradient(180deg, #FFFFFF 0%, #F8FBFE 100%)",
        },
    )


def bloque_pregunta(config):
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            etiqueta(config["badge"], config["color"]),
                            etiqueta(config["modelo"], COLORS["primary"]),
                        ],
                        style={"marginBottom": "8px"},
                    ),
                    html.Div(
                        "Pregunta de negocio",
                        style={
                            "color": config["color"],
                            "fontSize": "12px",
                            "fontWeight": "800",
                            "letterSpacing": "0.08em",
                            "textTransform": "uppercase",
                            "marginBottom": "8px",
                        },
                    ),
                    html.H2(
                        config["question"],
                        style={
                            "color": COLORS["primary"],
                            "fontSize": "24px",
                            "fontWeight": "800",
                            "margin": "0 0 10px",
                            "lineHeight": "1.35",
                        },
                    ),
                    html.P(
                        config["purpose"],
                        style={
                            "margin": "0",
                            "color": COLORS["muted"],
                            "fontSize": "14px",
                            "lineHeight": "1.6",
                            "maxWidth": "1100px",
                        },
                    ),
                ],
                className="question-hero-card",
                style={
                    **CARD_STYLE,
                    "borderLeft": f"6px solid {config['color']}",
                    "marginBottom": "16px",
                    "padding": "18px 22px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        tarjeta_texto(
                            "Objetivo analítico",
                            config["objective"],
                            config["color"],
                            class_name="summary-objective",
                        ),
                        style={"flex": "1"},
                    ),
                    html.Div(
                        tarjeta_texto(
                            "Decisión que apoya",
                            config["decision"],
                            COLORS["primary"],
                            class_name="summary-decision",
                        ),
                        style={"flex": "1"},
                    ),
                    html.Div(
                        tarjeta_texto(
                            "Salida principal",
                            config["output"],
                            COLORS["accent"],
                            class_name="summary-output",
                        ),
                        style={"flex": "1"},
                    ),
                ],
                className="tab-summary-grid tab-summary-section",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                    "gap": "12px",
                    "marginBottom": "0",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Cómo usar esta pestaña", className="usage-title"),
                            html.Span("1", className="usage-step"),
                            html.Span("Complete el formulario", className="usage-chip"),
                            html.Span("2", className="usage-step"),
                            html.Span("Calcule la predicción", className="usage-chip"),
                            html.Span("3", className="usage-step"),
                            html.Span("Lea el resultado e interpretación", className="usage-chip"),
                        ],
                        className="usage-row",
                    ),
                    html.P(
                        "Ingrese las características del estudiante, del hogar y de la institución educativa. "
                        "Luego presione 'Calcular predicción' para obtener una estimación, una interpretación breve "
                        "y una recomendación orientada a la toma de decisiones.",
                        style={
                            "margin": "0",
                            "color": COLORS["muted"],
                            "fontSize": "13px",
                            "lineHeight": "1.55",
                        },
                    ),
                ],
                className="tab-usage-card tab-usage-section",
                style={
                    "--usage-accent": config["color"],
                    "--usage-accent-soft": rgba_from_hex(config["color"], 0.10),
                    "--usage-accent-mid": rgba_from_hex(config["color"], 0.16),
                    "--usage-accent-line": rgba_from_hex(config["color"], 0.26),
                    "--usage-accent-shadow": rgba_from_hex(config["color"], 0.14),
                    "marginBottom": "30px",
                    "padding": "16px 18px",
                },
            ),
            html.Div(
                secciones_formulario_renderizadas(config),
                className="form-sections-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                    "gap": "18px",
                    "marginBottom": "22px",
                },
            ),
            html.Div(
                [
                    boton_prediccion(config["color"], config.get("button_id")),
                    boton_secundario("Realizar nueva consulta", config.get("reset_button_id"))
                    if config.get("reset_button_id")
                    else None,
                ],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "gap": "14px",
                    "flexWrap": "wrap",
                    "marginBottom": "24px",
                },
            ),
            barra_estado_tab2() if config.get("show_status_bar") else html.Div(),
            visual_binario_ingles() if config.get("show_binary_visual") else html.Div(),
            panel_visual_tab2() if config.get("show_visual_panel") else html.Div(),
            (
                html.Div(
                    [
                        html.Div(
                            tarjeta_resultado(
                                config["result_cards"][0]["title"],
                                config["result_cards"][0]["value"],
                                config["result_cards"][0]["detail"],
                                config["color"],
                                grande=True,
                                value_id=config["result_cards"][0].get("value_id"),
                                detail_id=config["result_cards"][0].get("detail_id"),
                            ),
                            style={"height": "100%"},
                        ),
                        html.Div(
                            tarjeta_resultado(
                                config["result_cards"][1]["title"],
                                config["result_cards"][1]["value"],
                                config["result_cards"][1]["detail"],
                                COLORS["primary"],
                                value_id=config["result_cards"][1].get("value_id"),
                                detail_id=config["result_cards"][1].get("detail_id"),
                            ),
                            style={"height": "100%"},
                        ),
                        html.Div(
                            tarjeta_resultado(
                                config["result_cards"][2]["title"],
                                config["result_cards"][2]["value"],
                                config["result_cards"][2]["detail"],
                                COLORS["accent"],
                                value_id=config["result_cards"][2].get("value_id"),
                                detail_id=config["result_cards"][2].get("detail_id"),
                            ),
                            style={"height": "100%"},
                        ),
                        html.Div(
                            tarjeta_resultado(
                                config["result_cards"][3]["title"],
                                config["result_cards"][3]["value"],
                                config["result_cards"][3]["detail"],
                                COLORS["green"],
                                value_id=config["result_cards"][3].get("value_id"),
                                detail_id=config["result_cards"][3].get("detail_id"),
                            ),
                            style={"height": "100%"},
                        ),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                        "gap": "18px",
                        "marginBottom": "22px",
                    },
                )
                if config.get("show_result_cards", True)
                else html.Div()
            ),
            html.Div(
                [
                    html.Div(
                        tarjeta_lista("Factores relevantes", config["factors"], config["color"]),
                        style={"flex": "1"},
                    ),
                    html.Div(
                        tarjeta_texto(
                            "Recomendación para decisión",
                            config["recommendation"],
                            COLORS["primary"],
                            subtitulo="Uso sugerido",
                        ),
                        style={"flex": "1"},
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                    "gap": "18px",
                },
            ),
        ]
    )


# ── Campos reutilizables simplificados ──────────────────────────────────────

def _radio_field(label, options, value, css_class="radio-choice-group"):
    return {
        "label": label,
        "tipo": "radio",
        "className": css_class,
        "options": options,
        "value": value,
        "inline": True,
    }


def _slider_field(label, min_value, max_value, value, marks=None):
    return {
        "label": label,
        "tipo": "slider",
        "min": min_value,
        "max": max_value,
        "step": 1,
        "value": value,
        "marks": marks,
    }


EDUCACION_OPCIONES = ["Ninguno","Primaria incompleta","Primaria completa","Secundaria (Bachillerato) incompleta","Secundaria (Bachillerato) completa","Técnica o tecnológica incompleta","Técnica o tecnológica completa","Educación profesional incompleta","Educación profesional completa","Postgrado"]
JORNADA_OPCIONES = ["Mañana", "Tarde", "Noche", "Única", "Completa", "Sabatina"]
CARACTER_OPCIONES = ["Académico", "Técnico","Técnico/Académico","No Aplica"]
try:
    MUNICIPIO_OPCIONES = sorted(load_tab2_municipality_summary()["display_name"].dropna().unique().tolist())
except Exception:
    MUNICIPIO_OPCIONES = ["Tunja", "Duitama", "Sogamoso", "Chiquinquira", "Paipa"]


secciones_comunes = [
    {
        "titulo": "Perfil del estudiante",
        "descripcion": "Información general del estudiante",
        "campos": [
            ("Municipio", MUNICIPIO_OPCIONES, "Seleccione un municipio"),
            ("Jornada escolar", JORNADA_OPCIONES, "Seleccione una opción"),
        ],
        "columnas": 1,
    },
    {
        "titulo": "Capital educativo familiar",
        "descripcion": "Nivel educativo del hogar",
        "campos": [
            ("Educación de la madre", EDUCACION_OPCIONES, "Seleccione una opción"),
            ("Educación del padre", EDUCACION_OPCIONES, "Seleccione una opción"),
        ],
        "columnas": 1,
    },
    {
        "titulo": "Características institucionales",
        "descripcion": "Rasgos estructurales del colegio",
        "campos": [
            ("Carácter", CARACTER_OPCIONES, "Seleccione una opción"),
            ("Municipio del colegio", MUNICIPIO_OPCIONES, "Seleccione un municipio"),
        ],
        "columnas": 1,
    },
    {
        "titulo": "Recursos del hogar",
        "descripcion": "Disponibilidad de servicios y bienes que facilitan el estudio fuera del colegio.",
        "campos": [
            _radio_field(
                "Internet en el hogar",
                [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}],
                "Si",
            ),
            _radio_field(
                "Computador en el hogar",
                [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}],
                "Si",
            ),
        ],
        "columnas": 1,
    },
    {
        "titulo": "Contexto territorial e institucional",
        "descripcion": "Ubicación y naturaleza del entorno educativo en el que estudia el caso analizado.",
        "campos": [
            _radio_field(
                "Zona",
                [{"label": "Urbana", "value": "Urbana"}, {"label": "Rural", "value": "Rural"}],
                "Urbana",
            ),
            _radio_field(
                "Naturaleza",
                [{"label": "Oficial", "value": "Oficial"}, {"label": "No oficial", "value": "No oficial"}],
                "Oficial",
            ),
            _radio_field(
                "Sector",
                [{"label": "Publico", "value": "Publico"}, {"label": "Privado", "value": "Privado"}],
                "Publico",
            ),
            _radio_field(
                "Área del colegio",
                [{"label": "Urbana", "value": "Urbana"}, {"label": "Rural", "value": "Rural"}],
                "Urbana",
            ),
        ],
        "columnas": 1,
    },
    {
        "titulo": "Condiciones del hogar",
        "descripcion": "Indicadores de composición familiar y nivel socioeconómico del hogar.",
        "campos": [
            _slider_field("Estrato de vivienda", 1, 6, 2, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6"}),
            _slider_field("Personas en el hogar", 1, 12, 4, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6",7:"7",8:"8",9:"9",10:"10",11:"11",12:"12"}),
        ],
        "columnas": 1,
    },
]


tab_1_model_fields = [
    _radio_field(
        "Área de ubicación del colegio",
        [{"label": "Urbana", "value": "Urbana"}, {"label": "Rural", "value": "Rural"}],
        "Urbana",
    ),
    _radio_field(
        "Colegio bilingüe",
        [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}],
        "No",
    ),
    ("Jornada", JORNADA_OPCIONES, "Seleccione una opción"),
    _radio_field(
        "Naturaleza",
        [{"label": "Oficial", "value": "Oficial"}, {"label": "No oficial", "value": "No oficial"}],
        "Oficial",
    ),
    _radio_field(
        "Género",
        [{"label": "Masculino", "value": "Masculino"}, {"label": "Femenino", "value": "Femenino"}],
        "Masculino",
    ),
    _slider_field("Cuartos del hogar", 1, 10, 3, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6",7:"7",8:"8",9:"9",10:"10"}),
    ("Educación de la madre", EDUCACION_OPCIONES, "Seleccione una opción"),
    ("Educación del padre", EDUCACION_OPCIONES, "Seleccione una opción"),
    _slider_field("Estrato de vivienda", 1, 6, 2, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6"}),
    _slider_field("Personas en el hogar", 1, 12, 4, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6",7:"7",8:"8",9:"9",10:"10",11:"11",12:"12"}),
    _radio_field(
        "Tiene computador",
        [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}],
        "Si",
    ),
    _radio_field(
        "Tiene internet",
        [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}],
        "Si",
    ),
    _radio_field(
        "Tiene lavadora",
        [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}],
        "Si",
    ),
]


tab_2_model_fields = [
    {
        **_radio_field(
            "Colegio bilingüe",
            [{"label": "Si", "value": 1}, {"label": "No", "value": 0}],
            0,
        ),
        "id": "tab2-cole-bilingue",
    },
    {
        "label": "Jornada",
        "options": JORNADA_OPCIONES,
        "placeholder": "Seleccione una opción",
        "id": "tab2-cole-jornada",
        "value": "Mañana",
    },
    {
        **_radio_field(
            "Área de ubicación",
            [{"label": "Urbana", "value": "Urbana"}, {"label": "Rural", "value": "Rural"}],
            "Urbana",
        ),
        "id": "tab2-cole-area",
    },
    {
        **_radio_field(
            "Naturaleza",
            [{"label": "Oficial", "value": "Oficial"}, {"label": "No oficial", "value": "No oficial"}],
            "Oficial",
        ),
        "id": "tab2-cole-naturaleza",
    },
    {
        "label": "Carácter",
        "options": CARACTER_OPCIONES,
        "placeholder": "Seleccione una opción",
        "id": "tab2-cole-caracter",
        "value": "Académico",
    },
    {
        "label": "Municipio de ubicación",
        "options": MUNICIPIO_OPCIONES,
        "placeholder": "Seleccione una opción",
        "id": "tab2-cole-mcpio",
        "value": "Tunja",
    },
    {
        **_radio_field(
            "Tiene computador",
            [{"label": "Si", "value": 1}, {"label": "No", "value": 0}],
            1,
        ),
        "id": "tab2-fami-computador",
    },
    {
        **_radio_field(
            "Tiene internet",
            [{"label": "Si", "value": 1}, {"label": "No", "value": 0}],
            1,
        ),
        "id": "tab2-fami-internet",
    },
    {
        **_slider_field("Estrato de vivienda", 1, 6, 2, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6"}),
        "id": "tab2-fami-estrato",
    },
    {
        "label": "Educación de la madre",
        "options": EDUCACION_OPCIONES,
        "placeholder": "Seleccione una opción",
        "id": "tab2-fami-educacionmadre",
        "value": "Secundaria (Bachillerato) completa",
    },
    {
        "label": "Educación del padre",
        "options": EDUCACION_OPCIONES,
        "placeholder": "Seleccione una opción",
        "id": "tab2-fami-educacionpadre",
        "value": "Secundaria (Bachillerato) completa",
    },
    {
        **_slider_field("Personas en el hogar", 1, 12, 4, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6",7:"7",8:"8",9:"9",10:"10",11:"11",12:"12"}),
        "id": "tab2-fami-personas",
    },
    {
        **_slider_field("Cuartos del hogar", 1, 10, 3, {1:"1",2:"2", 3: "3",4:"4",5:"5",6: "6",7:"7",8:"8",9:"9",10:"10"}),
        "id": "tab2-fami-cuartos",
    },
]


def _base_graph_layout(height=320):
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Segoe UI, sans-serif", "color": COLORS["text"]},
        "title_font": {"family": "Segoe UI, sans-serif", "size": 20, "color": COLORS["primary"]},
        "margin": {"l": 24, "r": 24, "t": 48, "b": 24},
        "height": height,
    }


def _build_gauge_figure(probability=None):
    value = 0 if probability is None else probability * 100
    bar_color = "#8A94A6" if probability is None else (COLORS["green"] if probability >= 0.5 else COLORS["red"])
    title = "Probabilidad estimada"
    suffix = "Sin cálculo" if probability is None else ("Supera" if probability >= 0.5 else "No supera")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            number={"suffix": "%", "font": {"size": 35, "family": "Segoe UI, sans-serif"}},
            delta={"reference": 50, "increasing": {"color": COLORS["green"]}, "decreasing": {"color": COLORS["red"]}},
            title={"text": f"{title}<br><span style='font-size:13px;color:#6B7C93'>{suffix}</span>"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": COLORS["muted"]},
                "bar": {"color": bar_color, "thickness": 0.34},
                "bgcolor": "#EDF2F7",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(201, 76, 76, 0.16)"},
                    {"range": [50, 100], "color": "rgba(12, 139, 95, 0.16)"},
                ],
                "threshold": {
                    "line": {"color": COLORS["primary"], "width": 5},
                    "thickness": 0.8,
                    "value": 50,
                },
            },
        )
    )
    fig.update_layout(**_base_graph_layout(height=300))
    return fig


def _build_donut_figure(percentile=None):
    value = 0 if percentile is None else percentile
    fig = go.Figure()

    segments = [
        (0, 20, "#FCA5A5"),
        (20, 40, "#FDBA74"),
        (40, 60, "#FDE68A"),
        (60, 80, "#86EFAC"),
        (80, 100, "#34D399"),
    ]

    for start, end, color in segments:
        fig.add_trace(
            go.Bar(
                x=[end - start],
                y=["percentil"],
                base=[start],
                orientation="h",
                marker={"color": color, "line": {"width": 0}},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.add_vline(x=value, line_width=5, line_color=COLORS["primary"])
    fig.add_trace(
        go.Scatter(
            x=[value],
            y=["percentil"],
            mode="markers",
            marker={
                "size": 18,
                "color": COLORS["primary"],
                "symbol": "diamond",
                "line": {"width": 2, "color": "white"},
            },
            hovertemplate="Percentil %{x:.1f}<extra></extra>",
            showlegend=False,
        )
    )

    layout = _base_graph_layout(height=300)
    layout["margin"] = {"l": 30, "r": 30, "t": 70, "b": 35}
    fig.update_layout(
        **layout,
        title={"text": "Percentil del estudiante dentro de Boyacá", "x": 0.03},
        barmode="stack",
        xaxis={
            "range": [0, 100],
            "showgrid": False,
            "zeroline": False,
            "tickvals": [0, 20, 40, 60, 80, 100],
            "tickfont": {"family": "Segoe UI, sans-serif", "size": 12, "color": COLORS["muted"]},
        },
        yaxis={"showticklabels": False, "showgrid": False, "zeroline": False},
        annotations=[
            {
                "text": (
                    f"<b style='font-size:34px'>P{value:.1f}</b>"
                    "<br><span style='font-size:14px;color:#6B7C93'>Percentil Boyacá</span>"
                ),
                "x": 0.5,
                "y": 1.24,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"family": "Segoe UI, sans-serif", "color": COLORS["text"]},
            }
        ],
    )
    return fig


def _build_factors_figure(favorable_items=None, risk_items=None):
    favorable_items = favorable_items or []
    risk_items = risk_items or []

    if not favorable_items and not risk_items:
        favorable_items = [("Sin datos favorables", 0.0)]
        risk_items = [("Sin datos de riesgo", 0.0)]

    risk_labels = [label for label, _ in reversed(risk_items)]
    risk_values = [-(score * 100) for _, score in reversed(risk_items)]
    favorable_labels = [label for label, _ in favorable_items]
    favorable_values = [score * 100 for _, score in favorable_items]

    labels = risk_labels + favorable_labels
    values = risk_values + favorable_values
    colors = [COLORS["red"]] * len(risk_labels) + [COLORS["green"]] * len(favorable_labels)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker={"color": colors},
            text=[f"{abs(v):.0f}%" for v in values],
            textposition="outside",
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_width=1.5, line_dash="dash", line_color=COLORS["muted"])
    fig.update_layout(
        **_base_graph_layout(height=320),
        title={"text": "Factores protectores y de riesgo", "x": 0.03},
        xaxis={"title": "Intensidad relativa", "ticksuffix": "%", "title_font": {"family": "Segoe UI, sans-serif"}},
        yaxis={"title": "", "tickfont": {"family": "Segoe UI, sans-serif"}},
        showlegend=False,
    )
    return fig


def _build_map_figure(selected_municipality=None):
    summary = load_tab2_municipality_summary()
    geojson = load_boyaca_geojson()
    norm_selected = normalize_municipality_name(selected_municipality)

    fig = go.Figure()
    fig.add_trace(
        go.Choropleth(
            geojson=geojson,
            featureidkey="properties.MUNICIPIO_NORM",
            locations=summary["municipio_normalizado"],
            z=summary["promedio_ingles"],
            text=summary["display_name"],
            colorscale=[
                [0.0, "#fee2e2"],
                [0.25, "#fecaca"],
                [0.5, "#fde68a"],
                [0.75, "#bbf7d0"],
                [1.0, "#34d399"],
            ],
            marker_line_color="white",
            marker_line_width=0.5,
            colorbar={"title": "Promedio inglés", "thickness": 12},
            hovertemplate="<b>%{text}</b><br>Promedio: %{z:.1f}<extra></extra>",
        )
    )

    if norm_selected:
        selected_row = summary.loc[summary["municipio_normalizado"] == norm_selected]
        if not selected_row.empty:
            row = selected_row.iloc[0]
            fig.add_trace(
                go.Scattergeo(
                    lon=[row["lon"]],
                    lat=[row["lat"]],
                    text=[f"Estudiante: {row['display_name']}"],
                    mode="markers+text",
                    textposition="top center",
                    marker={
                        "size": 14,
                        "color": COLORS["primary"],
                        "line": {"width": 2, "color": "white"},
                    },
                    hovertemplate="<b>%{text}</b><br>Promedio municipal: "
                    + f"{row['promedio_ingles']:.1f}"
                    + "<extra></extra>",
                    showlegend=False,
                )
            )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcountries=False,
        showcoastlines=False,
        showland=True,
        landcolor="#F8FAFC",
        bgcolor="rgba(0,0,0,0)",
    )
    layout = _base_graph_layout(height=420)
    layout["margin"] = {"l": 0, "r": 0, "t": 48, "b": 0}
    fig.update_layout(
        **layout,
        title={"text": "Mapa de calor por municipio de Boyacá", "x": 0.03},
    )
    return fig


def panel_visual_tab2():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="tab2-gauge-graph", figure=_build_gauge_figure(None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                    html.Div(
                        dcc.Graph(id="tab2-donut-graph", figure=_build_donut_figure(None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "18px", "marginBottom": "18px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(id="tab2-factors-graph", figure=_build_factors_figure(), config={"displayModeBar": False}),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div("Lectura favorable", style={"fontSize": "12px", "fontWeight": "800", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["accent"], "marginBottom": "8px"}),
                                            html.Div("Sin cálculo", id="tab2-favorable-summary", style={"fontSize": "22px", "fontWeight": "800", "color": COLORS["accent"], "marginBottom": "8px"}),
                                            html.Div("La explicación favorable aparecerá aquí.", id="tab2-favorable-detail", style={"fontSize": "14px", "lineHeight": "1.6", "color": COLORS["text"]}),
                                        ],
                                        style={**CARD_STYLE, "padding": "16px", "borderTop": f"4px solid {COLORS['accent']}"},
                                    ),
                                    html.Div(
                                        [
                                            html.Div("Lectura de riesgo", style={"fontSize": "12px", "fontWeight": "800", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["red"], "marginBottom": "8px"}),
                                            html.Div("Sin cálculo", id="tab2-risk-summary", style={"fontSize": "22px", "fontWeight": "800", "color": COLORS["red"], "marginBottom": "8px"}),
                                            html.Div("La explicación de riesgo aparecerá aquí.", id="tab2-risk-detail", style={"fontSize": "14px", "lineHeight": "1.6", "color": COLORS["text"]}),
                                        ],
                                        style={**CARD_STYLE, "padding": "16px", "borderTop": f"4px solid {COLORS['red']}"},
                                    ),
                                ],
                                style={"display": "grid", "gridTemplateColumns": "repeat(2, minmax(0, 1fr))", "gap": "14px", "marginTop": "14px"},
                            ),
                        ],
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                    html.Div(
                        dcc.Graph(id="tab2-map-graph", figure=_build_map_figure(None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "minmax(320px, 0.95fr) minmax(360px, 1.05fr)", "gap": "18px"},
            ),
        ],
        style={"marginBottom": "22px"},
    )


# ── Tabs ───────────────────────────────────────────────────────────────────

tab_1 = bloque_pregunta(
    {
        "badge": "Pregunta 1",
        "modelo": "Modelo de regresión",
        "tab": "Puntaje Global Esperado",
        "color": COLORS["gold"],
        "question": "¿Cuál es el puntaje global esperado de un estudiante de Boyacá en las pruebas Saber 11 según sus condiciones familiares, socioeconómicas e institucionales, y qué factores permiten identificar estudiantes o colegios con mayor riesgo de bajo desempeño académico?",
       "purpose": "",
        "objective": "Predecir el puntaje global esperado en Saber 11 para estudiantes de Boyacá y analizar qué variables se asocian con mejores o peores resultados.",
        "decision": "Apoya decisiones de focalización de tutorías, refuerzos académicos y acompañamiento institucional.",
        "output": "Puntaje global estimado, nivel de riesgo académico asociado e interpretación de los factores familiares, socioeconómicos e institucionales que influyen en la predicción.",
        "form_sections": [
            {
                "titulo": "Contexto institucional",
                "descripcion": "Características del colegio",
                "campos": [
                    tab_1_model_fields[0],
                    tab_1_model_fields[1],
                    tab_1_model_fields[2],
                    tab_1_model_fields[3],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Perfil del estudiante",
                "descripcion": "Rasgos personales y contexto inmediato del caso analizado.",
                "campos": [
                    tab_1_model_fields[4],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Capital educativo familiar",
                "descripcion": "Nivel educativo de los padres",
                "campos": [
                    tab_1_model_fields[6],
                    tab_1_model_fields[7],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Recursos del hogar",
                "descripcion": "Acceso a recursos materiales y nivel socioeconómico del hogar.",
                "campos": [
                    tab_1_model_fields[8],
                    tab_1_model_fields[10],
                    tab_1_model_fields[11],
                    tab_1_model_fields[12],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Composición del hogar",
                "descripcion": "Tamaño del hogar y disponibilidad de espacio residencial.",
                "campos": [
                    tab_1_model_fields[5],
                    tab_1_model_fields[9],
                ],
                "columnas": 1,
            },
        ],
        "result_cards": [
            {"title": "Puntaje global estimado", "value": "XXX pts", "detail": "Estimación principal del puntaje global esperado para el perfil seleccionado."},
            {"title": "Nivel de riesgo", "value": "Medio", "detail": "Clasificación referencial del riesgo académico esperado a partir de la predicción."},
            {"title": "Interpretación", "value": "Desempeño esperado", "detail": "Resumen corto del nivel de desempeño proyectado según el contexto familiar e institucional."},
            {"title": "Factor clave", "value": "Contexto del hogar", "detail": "Variable o grupo de variables con mayor incidencia esperada en el resultado del modelo."},
        ],
        "factors": [
            "Acceso a internet, computador y lavadora como aproximación a condiciones del hogar.",
            "Nivel educativo de madre y padre como capital educativo familiar.",
            "Características institucionales: jornada, área, bilingüismo y naturaleza del colegio.",
            "Composición del hogar, estrato y género del estudiante.",
        ],
        "recommendation": "Usar la predicción para priorizar tutorías, acompañamiento y seguimiento "
        "a estudiantes o instituciones con mayor riesgo de bajo desempeño esperado en el puntaje global.",
    }
)


tab_2 = bloque_pregunta(
    {
        "badge": "Pregunta 2",
        "modelo": "Modelo de clasificación",
        "tab": "Competencia en Inglés",
        "color": COLORS["green"],
        "button_id": "tab2-predict-button",
        "reset_button_id": "tab2-reset-button",
        "question": "¿Qué perfil combinado de características familiares e institucionales predice si un estudiante de Boyacá alcanzará un nivel A2 o superior en la prueba de inglés Saber 11, y qué factores escolares pueden compensar condiciones socioeconómicas desfavorables para lograr este desempeño?",
        "purpose": "",
        "objective": "Clasificar la probabilidad de alcanzar B1 o superior a partir de variables familiares, institucionales y académicas.",
        "decision": "Apoya decisiones de fortalecimiento curricular, asignación de apoyos en inglés y focalización de estrategias institucionales.",
        "output": "Probabilidad esperada de alcanzar nivel A2 o superior.",
        "show_status_bar": True,
        "show_binary_visual": True,
        "show_visual_panel": True,
        "show_result_cards": False,
        "form_sections": [
            {
                "titulo": "Contexto institucional",
                "descripcion": "Cracterísticas del colegio .",
                "campos": [
                    tab_2_model_fields[0],
                    tab_2_model_fields[1],
                    tab_2_model_fields[2],
                    tab_2_model_fields[3],
                    tab_2_model_fields[4],
                    tab_2_model_fields[5],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Recursos del hogar",
                "descripcion": "Acceso a recursos materiales y nivel socioeconómico del hogar.",
                "campos": [
                    tab_2_model_fields[6],
                    tab_2_model_fields[7],
                    tab_2_model_fields[8],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Capital educativo familiar",
                "descripcion": "Nivel educativo de los padres",
                "campos": [
                    tab_2_model_fields[9],
                    tab_2_model_fields[10],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Composición del hogar",
                "descripcion": "Tamaño del hogar y disponibilidad de espacio residencial.",
                "campos": [
                    tab_2_model_fields[11],
                    tab_2_model_fields[12],
                ],
                "columnas": 1,
            },
        ],
        "result_cards": [
            {
                "title": "Probabilidad de superar 58",
                "value": "XX %",
                "detail": "Estimación de la probabilidad de quedar en la clase mayor a 58 en la prueba de inglés.",
                "value_id": "tab2-result-probability",
                "detail_id": "tab2-result-probability-detail",
            },
            {
                "title": "Clasificación esperada",
                "value": "<=58 / >58",
                "detail": "Resultado binario de referencia según el punto de corte definido para el modelo.",
                "value_id": "tab2-result-class",
                "detail_id": "tab2-result-class-detail",
            },
            {
                "title": "Factores favorables",
                "value": "Jornada + acceso",
                "detail": "Resumen breve de variables escolares y tecnológicas que empujan la predicción al alza.",
                "value_id": "tab2-result-positive",
                "detail_id": "tab2-result-positive-detail",
            },
            {
                "title": "Factores de riesgo",
                "value": "Contexto vulnerable",
                "detail": "Variables de contexto que reducen la probabilidad esperada de competencia en inglés.",
                "value_id": "tab2-result-risk",
                "detail_id": "tab2-result-risk-detail",
            },
        ],
        "factors": [
            "Acceso tecnológico y exposición a recursos digitales en el hogar.",
            "Condiciones institucionales: jornada, área y naturaleza del colegio.",
            "Capital educativo familiar asociado al acompañamiento del proceso formativo.",
            "Variables académicas previas con relación esperada al aprendizaje de idiomas.",
        ],
        "recommendation": "Usar la clasificación para priorizar estudiantes e instituciones que "
        "requieren refuerzo en inglés, acompañamiento intensivo o ajustes en la oferta de apoyo escolar y digital.",
    }
)


def _tab2_factor_messages(payload):
    positives = []
    risks = []

    if payload["cole_bilingue"] in (1, "Si", "S"):
        positives.append("Colegio bilingüe")
    if payload["cole_jornada"] in ("Mañana", "Única", "Completa"):
        positives.append(f"Jornada {payload['cole_jornada']}")
    if payload["fami_tieneinternet"] in (1, "Si"):
        positives.append("Acceso a internet")
    if payload["fami_tienecomputador"] in (1, "Si"):
        positives.append("Computador en el hogar")
    if payload["fami_estratovivienda"] >= 3:
        positives.append(f"Estrato {payload['fami_estratovivienda']}")

    if payload["cole_area_ubicacion"] == "Rural":
        risks.append("Ubicación rural")
    if payload["fami_tieneinternet"] in (0, "No"):
        risks.append("Sin internet")
    if payload["fami_tienecomputador"] in (0, "No"):
        risks.append("Sin computador")
    if payload["fami_estratovivienda"] <= 2:
        risks.append(f"Estrato {payload['fami_estratovivienda']}")
    if payload["fami_personashogar"] >= 6:
        risks.append("Hogar numeroso")

    positive_value = ", ".join(positives[:2]) if positives else "Perfil equilibrado"
    positive_detail = (
        "Las condiciones seleccionadas sugieren un entorno más favorable para superar el umbral."
        if positives
        else "No aparecen impulsores claros por encima del resto de variables del perfil."
    )
    risk_value = ", ".join(risks[:2]) if risks else "Riesgo acotado"
    risk_detail = (
        "Estas condiciones del contexto podrían reducir la probabilidad estimada del modelo."
        if risks
        else "No se observan factores de riesgo marcados en las variables diligenciadas."
    )
    return positive_value, positive_detail, risk_value, risk_detail


def _tab2_factor_rankings(payload):
    favorable = []
    risk = []

    if payload["cole_bilingue"] in (1, "Si", "S"):
        favorable.append(("Colegio bilingüe", 0.92))
    else:
        risk.append(("Colegio no bilingüe", 0.66))

    jornada_scores = {
        "Mañana": 0.78,
        "Única": 0.84,
        "Completa": 0.8,
        "Tarde": 0.46,
        "Noche": 0.74,
        "Sabatina": 0.58,
    }
    jornada = payload["cole_jornada"]
    favorable.append((f"Jornada {jornada}", jornada_scores.get(jornada, 0.52)))
    if jornada in ("Tarde", "Sabatina"):
        risk.append((f"Jornada {jornada}", 0.52))

    if payload["cole_area_ubicacion"] == "Urbana":
        favorable.append(("Entorno urbano", 0.62))
    else:
        risk.append(("Entorno rural", 0.78))

    if payload["fami_tieneinternet"] in (1, "Si"):
        favorable.append(("Internet en casa", 0.86))
    else:
        risk.append(("Sin internet en casa", 0.93))

    if payload["fami_tienecomputador"] in (1, "Si"):
        favorable.append(("Computador en el hogar", 0.8))
    else:
        risk.append(("Sin computador", 0.82))

    estrato = payload["fami_estratovivienda"]
    favorable.append((f"Estrato {estrato}", min(0.42 + estrato * 0.08, 0.9)))
    if estrato <= 2:
        risk.append((f"Estrato {estrato}", 0.79 if estrato == 1 else 0.68))

    avg_parent_edu = (
        EDUCACION_OPCIONES.index(payload["fami_educacionmadre"])
        + EDUCACION_OPCIONES.index(payload["fami_educacionpadre"])
    ) / 2
    favorable.append(("Capital educativo familiar", min(0.35 + avg_parent_edu * 0.06, 0.88)))
    if avg_parent_edu <= 2:
        risk.append(("Bajo capital educativo", 0.76))

    hacinamiento = payload["fami_personashogar"] / max(payload["fami_cuartoshogar"], 1)
    favorable.append(("Espacio del hogar", max(0.2, 0.82 - hacinamiento * 0.11)))
    if hacinamiento >= 2.5:
        risk.append(("Hacinamiento", min(0.55 + hacinamiento * 0.1, 0.92)))

    favorable = sorted(favorable, key=lambda item: item[1], reverse=True)[:3]
    risk = sorted(risk, key=lambda item: item[1], reverse=True)[:3]
    return favorable, risk


def _metric_bar_rows(items, accent_color, empty_message):
    if not items:
        return html.Div(
            empty_message,
            style={"fontSize": "13px", "color": COLORS["muted"], "lineHeight": "1.5"},
        )

    rows = []
    for label, score in items:
        pct = round(float(score) * 100)
        rows.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(label, style={"fontWeight": "700", "color": COLORS["text"]}),
                            html.Span(f"{pct}%", style={"fontWeight": "800", "color": accent_color}),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "gap": "12px",
                            "fontSize": "13px",
                            "marginBottom": "6px",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                style={
                                    "width": f"{pct}%",
                                    "height": "100%",
                                    "borderRadius": "999px",
                                    "background": f"linear-gradient(90deg, {accent_color} 0%, {accent_color}CC 100%)",
                                }
                            )
                        ],
                        style={
                            "height": "10px",
                            "borderRadius": "999px",
                            "overflow": "hidden",
                            "background": "#E2E8F0",
                            "border": f"1px solid {COLORS['border']}",
                        },
                    ),
                ],
                style={"marginBottom": "12px"},
            )
        )
    return html.Div(rows)


def _percentile_detail(percentile):
    fill_color = COLORS["green"] if percentile >= 50 else COLORS["red"]
    return html.Div(
        [
            html.Div(
                f"Percentil estimado dentro de Boyacá: {percentile:.1f}",
                style={
                    "fontSize": "13px",
                    "fontWeight": "700",
                    "color": COLORS["text"],
                    "marginBottom": "10px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        style={
                            "width": f"{max(2, min(percentile, 100))}%",
                            "height": "100%",
                            "borderRadius": "999px",
                            "background": f"linear-gradient(90deg, {fill_color} 0%, {fill_color}CC 100%)",
                            "transition": "width 0.35s ease",
                        }
                    )
                ],
                style={
                    "height": "14px",
                    "borderRadius": "999px",
                    "overflow": "hidden",
                    "background": "#E2E8F0",
                    "border": f"1px solid {COLORS['border']}",
                    "marginBottom": "8px",
                },
            ),
            html.Div(
                [
                    html.Span("0", style={"fontSize": "12px", "color": COLORS["muted"]}),
                    html.Span("50", style={"fontSize": "12px", "color": COLORS["muted"]}),
                    html.Span("100", style={"fontSize": "12px", "color": COLORS["muted"]}),
                ],
                style={"display": "flex", "justifyContent": "space-between"},
            ),
        ]
    )


tab_3 = bloque_pregunta(
    {
        "badge": "Pregunta 3",
        "modelo": "Modelo de regresión",
        "tab": "Resiliencia Académica",
        "color": COLORS["blue"],
        "question": "¿Cuál es el puntaje global esperado de un estudiante de Boyacá en las pruebas Saber 11 según sus condiciones familiares, socioeconómicas e institucionales, y qué factores permiten identificar estudiantes o colegios con mayor riesgo de bajo desempeño académico?",
        "purpose": "",
        "objective": "Estimar la magnitud y dirección esperada de la brecha Matemáticas - Lectura Crítica para un perfil estudiantil e institucional dado.",
        "decision": "Apoya decisiones de refuerzo focalizado por área, acompañamiento académico y seguimiento institucional por perfiles de riesgo.",
        "output": "Brecha esperada entre puntaje de Matemáticas y Lectura Crítica.",
        "form_sections": secciones_comunes + [
            {
                "titulo": "Variables académicas",
                "campos": [
                    ("Puntaje global previo o estimado", ["Sin dato", "Bajo", "Medio", "Alto"], "Seleccione una opción"),
                    ("Nivel de desempeño integral", ["Básico", "Intermedio", "Alto"], "Seleccione una opción"),
                    ("Participación en apoyos", ["No registra", "Sí"], "Seleccione una opción"),
                    ("Capital educativo familiar", ["Bajo", "Medio", "Alto"], "Seleccione una opción"),
                ],
                "columnas": 1,
            }
        ],
        "result_cards": [
            {"title": "Probabilidad de superar el percentil 75", "value": "XX %", "detail": "Estimación del potencial de alto desempeño para el perfil seleccionado."},
            {"title": "Clasificación esperada", "value": "Alto potencial", "detail": "Lectura rápida para priorizar seguimiento o fortalecimiento del caso."},
            {"title": "Factores de resiliencia", "value": "Institución protectora", "detail": "Características institucionales que incrementan la probabilidad de alto desempeño."},
            {"title": "Mensaje para decisión", "value": "Priorizar apoyos", "detail": "Sugerencia operativa de becas, tutorías o seguimiento según el perfil predicho."},
        ],
        "factors": [
            "Condiciones institucionales que amortiguan desventajas de capital educativo familiar.",
            "Patrones de resiliencia asociados a jornada, sector y entorno escolar.",
            "Combinación de desempeño académico e indicadores de apoyo institucional.",
            "Variables territoriales que ayudan a priorizar municipios y perfiles de intervención.",
        ],
        "recommendation": "Usar este resultado para identificar estudiantes con alto potencial en "
        "contextos vulnerables, orientar becas o tutorías y reconocer instituciones que operan como "
        "factores de resiliencia académica.",
    }
)


# ── Layout ─────────────────────────────────────────────────────────────────

app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Img(
                                    src="/assets/gb.png",
                                    alt="Imagen institucional del dashboard",
                                    style={
                                        "width": "100%",
                                        "maxWidth": "360px",
                                        "display": "block",
                                        "margin": "0 auto",
                                    },
                                ),
                            ],
                            style={
                                "flex": "0 0 340px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "padding": "8px 12px 8px 0",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    "Dashboard predictivo · Pruebas Saber 11 · Boyacá",
                                    style={
                                        "fontSize": "12px",
                                        "fontWeight": "700",
                                        "letterSpacing": "0.10em",
                                        "textTransform": "uppercase",
                                        "color": COLORS["secondary"],
                                        "marginBottom": "10px",
                                    },
                                ),
                                html.H1(
                                    "Saber 11 Boyacá: Brechas, Competencias y Resiliencia Académica",
                                    style={
                                        "margin": "0 0 14px",
                                        "color": COLORS["primary"],
                                        "fontSize": "38px",
                                        "fontWeight": "800",
                                        "lineHeight": "1.15",
                                    },
                                ),
                                html.P(
                                    "Herramienta predictiva para apoyar la focalización de estrategias "
                                    "educativas en estudiantes e instituciones de Boyacá.",
                                    style={
                                        "margin": "0 0 16px",
                                        "color": COLORS["text"],
                                        "fontSize": "16px",
                                        "lineHeight": "1.8",
                                        "maxWidth": "860px",
                                    },
                                ),
                                html.Div(
                                    [
                                        etiqueta("Secretaría de Educación", COLORS["primary"]),
                                        etiqueta("Colegios y rectorías", COLORS["secondary"]),
                                        etiqueta("Toma de decisiones", COLORS["accent"]),
                                    ]
                                ),
                            ],
                            style={"flex": "1", "minWidth": "280px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexWrap": "wrap",
                        "alignItems": "center",
                        "gap": "24px",
                    },
                )
            ],
            style={
                **CARD_STYLE,
                "background": "linear-gradient(135deg, #FFFFFF 0%, #F7FBFF 60%, #EEF6F1 100%)",
                "marginBottom": "24px",
            },
        ),
        # KPI cards
        html.Div(
            [
                html.Div(tarjeta_kpi("Modelos desplegados", "3", "1 regresión y 2 clasificaciones activas en el tablero.", COLORS["blue"], "M"), style={"flex": "1"}),
                html.Div(tarjeta_kpi("Tipos de salida", "2", "Predicción numérica y clasificación binaria para lectura rápida.", COLORS["green"], "S"), style={"flex": "1"}),
                html.Div(tarjeta_kpi("Decisiones apoyadas", "3", "Focalización, acompañamiento y priorización de intervenciones.", COLORS["gold"], "D"), style={"flex": "1"}),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                "gap": "16px",
                "marginBottom": "28px",
            },
        ),
        # Tabs
        dcc.Tabs(
            [
                dcc.Tab(label="Puntaje Global Esperado", children=[tab_1], style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Competencia en Inglés", children=[tab_2], style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
                dcc.Tab(label="Resiliencia Académica", children=[tab_3], style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
            ],
            style={"backgroundColor": "transparent", "border": "none", "marginTop": "8px"},
        ),
    ],
    style={
        "backgroundColor": COLORS["background"],
        "minHeight": "100vh",
        "padding": "32px",
        "fontFamily": '"Segoe UI", sans-serif',
    },
)


@app.callback(
    Output("tab2-favorable-summary", "children"),
    Output("tab2-favorable-detail", "children"),
    Output("tab2-risk-summary", "children"),
    Output("tab2-risk-detail", "children"),
    Output("tab2-binary-indicator-value", "children"),
    Output("tab2-binary-indicator", "style"),
    Output("tab2-gauge-graph", "figure"),
    Output("tab2-donut-graph", "figure"),
    Output("tab2-factors-graph", "figure"),
    Output("tab2-map-graph", "figure"),
    Input("tab2-predict-button", "n_clicks"),
    Input("tab2-reset-button", "n_clicks"),
    State("tab2-cole-bilingue", "value"),
    State("tab2-cole-jornada", "value"),
    State("tab2-cole-area", "value"),
    State("tab2-cole-naturaleza", "value"),
    State("tab2-cole-caracter", "value"),
    State("tab2-cole-mcpio", "value"),
    State("tab2-fami-computador", "value"),
    State("tab2-fami-internet", "value"),
    State("tab2-fami-estrato", "value"),
    State("tab2-fami-educacionmadre", "value"),
    State("tab2-fami-educacionpadre", "value"),
    State("tab2-fami-personas", "value"),
    State("tab2-fami-cuartos", "value"),
    prevent_initial_call=True,
    running=[
        (
            Output("tab2-status-text", "children"),
            "Calculando predicción con el modelo...",
            "Modelo listo para una nueva consulta",
        ),
        (
            Output("tab2-status-fill", "style"),
            {
                "width": "72%",
                "height": "100%",
                "borderRadius": "999px",
                "background": "linear-gradient(90deg, #1D5AA6 0%, #009640 100%)",
                "transition": "width 0.35s ease, background 0.35s ease",
            },
            {
                "width": "18%",
                "height": "100%",
                "borderRadius": "999px",
                "background": "linear-gradient(90deg, #8a94a6 0%, #64748b 100%)",
                "transition": "width 0.35s ease, background 0.35s ease",
            },
        ),
        (
            Output("tab2-predict-button", "disabled"),
            True,
            False,
        ),
        (
            Output("tab2-reset-button", "disabled"),
            True,
            False,
        ),
    ],
)
def run_tab2_prediction(
    n_clicks,
    reset_clicks,
    cole_bilingue,
    cole_jornada,
    cole_area,
    cole_naturaleza,
    cole_caracter,
    cole_mcpio,
    fami_computador,
    fami_internet,
    fami_estrato,
    fami_educacionmadre,
    fami_educacionpadre,
    fami_personas,
    fami_cuartos,
):
    if not n_clicks and not reset_clicks:
        return (no_update,) * 10

    try:
        triggered_id = ctx.triggered_id
    except Exception:
        triggered_id = "tab2-reset-button" if reset_clicks else "tab2-predict-button"

    if triggered_id == "tab2-reset-button":
        return (
            "Sin cálculo",
            "La lectura favorable aparecerá aquí cuando ejecutes una nueva consulta.",
            "Sin cálculo",
            "La lectura de riesgo aparecerá aquí cuando ejecutes una nueva consulta.",
            "Pendiente",
            {
                "background": "linear-gradient(135deg, #8a94a6 0%, #64748b 100%)",
                "left": "50%",
            },
            _build_gauge_figure(None),
            _build_donut_figure(None),
            _build_factors_figure(),
            _build_map_figure(None),
        )

    payload = {
        "cole_bilingue": "Si" if cole_bilingue == 1 else "No",
        "cole_jornada": cole_jornada,
        "cole_area_ubicacion": cole_area,
        "cole_naturaleza": cole_naturaleza,
        "cole_caracter": cole_caracter,
        "cole_mcpio_ubicacion": cole_mcpio,
        "fami_tienecomputador": "Si" if fami_computador == 1 else "No",
        "fami_tieneinternet": "Si" if fami_internet == 1 else "No",
        "fami_estratovivienda": int(fami_estrato) if fami_estrato is not None else None,
        "fami_educacionmadre": fami_educacionmadre,
        "fami_educacionpadre": fami_educacionpadre,
        "fami_personashogar": fami_personas,
        "fami_cuartoshogar": fami_cuartos,
    }

    try:
        probability = predict_tab2_probability(payload)
        bundle = Tab2Bundle.from_path()
        percentile = probability_to_percentile(probability, bundle.probability_reference)
    except Exception as exc:
        message = f"Error: {exc}"
        return (
            "Sin cálculo",
            message,
            "Revisar insumos",
            "La predicción no pudo calcularse con el entorno actual.",
            "Error",
            {
                "background": "linear-gradient(135deg, #8a94a6 0%, #64748b 100%)",
                "left": "50%",
            },
            _build_gauge_figure(None),
            _build_donut_figure(None),
            _build_factors_figure(),
            _build_map_figure(payload.get("cole_mcpio_ubicacion")),
        )

    predicted_class = 1 if probability > 0.5 else 0
    positive_value, positive_detail, risk_value, risk_detail = _tab2_factor_messages(payload)
    favorable_items, risk_items = _tab2_factor_rankings(payload)
    indicator_value = ">58" if predicted_class == 1 else "<=58"
    indicator_style = {
        "background": (
            "linear-gradient(135deg, #0c8b5f 0%, #18a66d 100%)"
            if predicted_class == 1
            else "linear-gradient(135deg, #c94c4c 0%, #dd6b6b 100%)"
        ),
        "left": "81%" if predicted_class == 1 else "19%",
    }

    return (
        positive_value,
        positive_detail,
        risk_value,
        risk_detail,
        indicator_value,
        indicator_style,
        _build_gauge_figure(probability),
        _build_donut_figure(percentile),
        _build_factors_figure(favorable_items, risk_items),
        _build_map_figure(payload["cole_mcpio_ubicacion"]),
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
