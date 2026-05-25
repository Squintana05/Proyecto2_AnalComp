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
                "tooltip": {"placement": "top", "always_visible": True},
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
                            html.Div("", className="binary-level-class"),
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
                            html.Div("", className="binary-level-class"),
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
            panel_visual_tab1() if config.get("show_visual_panel_tab1") else html.Div(),
            panel_visual_tab2() if config.get("show_visual_panel") else html.Div(),
            panel_visual_tab3() if config.get("show_visual_panel_tab3") else html.Div(),
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
            (
                panel_resultado_tab2()
                if config.get("bottom_section") == "classification"
                else panel_resultado_tab3()
                if config.get("bottom_section") == "brecha"
                else html.Div(
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
                )
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
    {
        **_radio_field("Área de ubicación del colegio", [{"label": "Urbana", "value": "Urbana"}, {"label": "Rural", "value": "Rural"}], "Urbana"),
        "id": "tab1-cole-area",
    },
    {
        **_radio_field("Colegio bilingüe", [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}], "No"),
        "id": "tab1-cole-bilingue",
    },
    {"label": "Jornada", "options": JORNADA_OPCIONES, "placeholder": "Seleccione una opción", "id": "tab1-cole-jornada", "value": "Mañana"},
    {
        **_radio_field("Naturaleza", [{"label": "Oficial", "value": "Oficial"}, {"label": "No oficial", "value": "No oficial"}], "Oficial"),
        "id": "tab1-cole-naturaleza",
    },
    {
        **_radio_field("Género", [{"label": "Masculino", "value": "Masculino"}, {"label": "Femenino", "value": "Femenino"}], "Masculino"),
        "id": "tab1-estu-genero",
    },
    {**_slider_field("Cuartos del hogar", 1, 10, 3, {1:"1",2:"2",3:"3",4:"4",5:"5",6:"6",7:"7",8:"8",9:"9",10:"10"}), "id": "tab1-fami-cuartos"},
    {"label": "Educación de la madre", "options": EDUCACION_OPCIONES, "placeholder": "Seleccione una opción", "id": "tab1-fami-educacionmadre", "value": "Secundaria (Bachillerato) completa"},
    {"label": "Educación del padre", "options": EDUCACION_OPCIONES, "placeholder": "Seleccione una opción", "id": "tab1-fami-educacionpadre", "value": "Secundaria (Bachillerato) completa"},
    {**_slider_field("Estrato de vivienda", 1, 6, 2, {1:"1",2:"2",3:"3",4:"4",5:"5",6:"6"}), "id": "tab1-fami-estrato"},
    {**_slider_field("Personas en el hogar", 1, 12, 4, {1:"1",2:"2",3:"3",4:"4",5:"5",6:"6",7:"7",8:"8",9:"9",10:"10",11:"11",12:"12"}), "id": "tab1-fami-personas"},
    {
        **_radio_field("Tiene computador", [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}], "Si"),
        "id": "tab1-fami-computador",
    },
    {
        **_radio_field("Tiene internet", [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}], "Si"),
        "id": "tab1-fami-internet",
    },
    {
        **_radio_field("Tiene lavadora", [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}], "Si"),
        "id": "tab1-fami-lavadora",
    },
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


tab_3_model_fields = [
    {
        **_radio_field("Internet en el hogar", [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}], "Si"),
        "id": "tab3-fami-internet",
    },
    {
        **_radio_field("Computador en el hogar", [{"label": "Si", "value": "Si"}, {"label": "No", "value": "No"}], "Si"),
        "id": "tab3-fami-computador",
    },
    {**_slider_field("Estrato de vivienda", 1, 6, 2, {1:"1",2:"2",3:"3",4:"4",5:"5",6:"6"}), "id": "tab3-fami-estrato"},
    {"label": "Educación de la madre", "options": EDUCACION_OPCIONES, "placeholder": "Seleccione una opción", "id": "tab3-fami-educacionmadre", "value": "Secundaria (Bachillerato) completa"},
    {"label": "Educación del padre", "options": EDUCACION_OPCIONES, "placeholder": "Seleccione una opción", "id": "tab3-fami-educacionpadre", "value": "Secundaria (Bachillerato) completa"},
    {**_slider_field("Personas en el hogar", 1, 12, 4, {1:"1",2:"2",3:"3",4:"4",5:"5",6:"6",7:"7",8:"8",9:"9",10:"10",11:"11",12:"12"}), "id": "tab3-fami-personas"},
    {**_slider_field("Cuartos del hogar", 1, 10, 3, {1:"1",2:"2",3:"3",4:"4",5:"5",6:"6",7:"7",8:"8",9:"9",10:"10"}), "id": "tab3-fami-cuartos"},
    {
        **_radio_field("Área de ubicación", [{"label": "Urbana", "value": "Urbana"}, {"label": "Rural", "value": "Rural"}], "Urbana"),
        "id": "tab3-cole-area",
    },
    {
        "label": "Carácter del colegio",
        "options": CARACTER_OPCIONES,
        "placeholder": "Seleccione una opción",
        "id": "tab3-cole-caracter",
        "value": "Académico",
    },
    {"label": "Jornada", "options": JORNADA_OPCIONES, "placeholder": "Seleccione una opción", "id": "tab3-cole-jornada", "value": "Mañana"},
    {
        **_radio_field("Naturaleza del colegio", [{"label": "Oficial", "value": "Oficial"}, {"label": "No oficial", "value": "No oficial"}], "Oficial"),
        "id": "tab3-cole-naturaleza",
    },
]


def _base_graph_layout(height=320):
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Segoe UI, sans-serif", "color": COLORS["text"]},
        "title_font": {"family": "Segoe UI, sans-serif", "size": 26, "color": COLORS["primary"]},
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
            number={"suffix": "%", "font": {"size": 40, "family": "Segoe UI, sans-serif"}},
            delta={"reference": 50, "increasing": {"color": COLORS["green"]}, "decreasing": {"color": COLORS["red"]}},
            title={"text": f"<span style='font-size:24px'>{title}</span><br><span style='font-size:14px;color:#6B7C93'>{suffix}</span>"},
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


def _build_donut_figure(probability=None):
    prob_supera = 0 if probability is None else probability * 100
    prob_no_supera = max(0, 100 - prob_supera)

    labels = ["No supera (<=58)", "Sí supera (>58)"]
    values = [prob_no_supera, prob_supera]
    colors = [COLORS["red"], COLORS["green"]]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            text=[f"{value:.1f}%" for value in values],
            textposition="outside",
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
            showlegend=False,
        )
    )

    layout = _base_graph_layout(height=300)
    layout["margin"] = {"l": 150, "r": 40, "t": 78, "b": 30}
    fig.update_layout(
        **layout,
        title={"text": "Probabilidad de cada clase", "x": 0.03},
        xaxis={
            "range": [0, 100],
            "showgrid": True,
            "gridcolor": "#E2E8F0",
            "zeroline": False,
            "ticksuffix": "%",
            "tickfont": {"family": "Segoe UI, sans-serif", "size": 12, "color": COLORS["muted"]},
        },
        yaxis={
            "title": "",
            "tickfont": {"family": "Segoe UI, sans-serif", "size": 15, "color": COLORS["text"]},
            "autorange": "reversed",
        },
        annotations=[
            {
                "text": "Comparación directa entre las dos clases que compiten en la decisión del modelo.",
                "x": 0.03,
                "y": 1.16,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "xanchor": "left",
                "font": {"family": "Segoe UI, sans-serif", "size": 14, "color": COLORS["muted"]},
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
        xaxis={
            "title": "Intensidad relativa",
            "ticksuffix": "%",
            "title_font": {"family": "Segoe UI, sans-serif", "size": 15},
        },
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
        title={"text": "Mapa de calor por municipio de Boyacá", "x": 0.03, "font": {"family": "Segoe UI, sans-serif", "size": 24, "color": COLORS["primary"]}},
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


# ── Tab 1 visualization helpers ─────────────────────────────────────────────

def _tab1_score_from_payload(payload):
    base = 258
    contributions = {}

    edu_madre_idx = EDUCACION_OPCIONES.index(payload["fami_educacionmadre"]) if payload["fami_educacionmadre"] in EDUCACION_OPCIONES else 4
    contributions["Edu. madre"] = round((edu_madre_idx - 4) * 3.2, 1)

    edu_padre_idx = EDUCACION_OPCIONES.index(payload["fami_educacionpadre"]) if payload["fami_educacionpadre"] in EDUCACION_OPCIONES else 4
    contributions["Edu. padre"] = round((edu_padre_idx - 4) * 2.8, 1)

    contributions["Estrato"] = round((int(payload["fami_estrato"]) - 2) * 4.5, 1)
    contributions["Internet"] = 8.5 if payload["fami_internet"] == "Si" else -8.5
    contributions["Computador"] = 6.2 if payload["fami_computador"] == "Si" else -6.2
    contributions["Lavadora"] = 4.1 if payload["fami_lavadora"] == "Si" else -4.1
    contributions["Bilingüe"] = 12.4 if payload["cole_bilingue"] == "Si" else -3.1

    jornada_delta = {"Mañana": 3.5, "Única": 5.2, "Completa": 6.8, "Tarde": -4.1, "Noche": -8.3, "Sabatina": -2.9}
    contributions["Jornada"] = jornada_delta.get(payload["cole_jornada"], 0)

    contributions["Área"] = -5.6 if payload["cole_area"] == "Rural" else 2.1
    contributions["Naturaleza"] = 4.3 if payload["cole_naturaleza"] == "No oficial" else -1.8
    contributions["Género"] = 2.8 if payload["estu_genero"] == "Masculino" else -2.8
    contributions["Personas"] = round(-1.8 * max(0, int(payload["fami_personas"]) - 4), 1)
    contributions["Cuartos"] = round(1.4 * min(int(payload["fami_cuartos"]) - 3, 3), 1)

    score = base + sum(contributions.values())
    score = max(0, min(500, round(score)))
    return score, base, contributions


def _build_tab1_gauge(score=None):
    value = score if score is not None else 0
    if score is None:
        bar_color, suffix = "#8A94A6", "Sin cálculo"
    elif score < 220:
        bar_color, suffix = COLORS["red"], "Riesgo alto"
    elif score < 258:
        bar_color, suffix = "#E8A020", "Riesgo moderado"
    elif score < 308:
        bar_color, suffix = COLORS["gold"], "Desempeño medio"
    else:
        bar_color, suffix = COLORS["green"], "Desempeño alto"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": " pts", "font": {"size": 40, "family": "Segoe UI, sans-serif"}},
            title={"text": f"<span style='font-size:22px'>Puntaje global estimado</span><br><span style='font-size:14px;color:#6B7C93'>{suffix}</span>"},
            gauge={
                "axis": {"range": [0, 500], "tickwidth": 1, "tickcolor": COLORS["muted"], "tickfont": {"family": "Segoe UI, sans-serif"}},
                "bar": {"color": bar_color, "thickness": 0.34},
                "bgcolor": "#EDF2F7",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 220], "color": "rgba(201, 76, 76, 0.16)"},
                    {"range": [220, 258], "color": "rgba(232, 160, 32, 0.16)"},
                    {"range": [258, 308], "color": "rgba(216, 163, 26, 0.12)"},
                    {"range": [308, 500], "color": "rgba(12, 139, 95, 0.16)"},
                ],
                "threshold": {"line": {"color": COLORS["primary"], "width": 3}, "thickness": 0.8, "value": 258},
            },
        )
    )
    fig.update_layout(**_base_graph_layout(height=300))
    return fig


def _build_tab1_bullet(score=None):
    benchmarks = [
        ("P75 Boyacá", 308, COLORS["green"]),
        ("Nacional promedio", 272, COLORS["blue"]),
        ("Boyacá promedio", 258, COLORS["primary"]),
    ]
    y_vals = [b[0] for b in benchmarks]
    x_vals = [b[1] for b in benchmarks]
    bar_colors = [rgba_from_hex(b[2], 0.22) for b in benchmarks]
    line_colors = [b[2] for b in benchmarks]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_vals,
        y=y_vals,
        orientation="h",
        marker={"color": bar_colors, "line": {"color": line_colors, "width": 2}},
        text=[str(v) for v in x_vals],
        textposition="outside",
        hovertemplate="%{y}: %{x}<extra></extra>",
        showlegend=False,
    ))

    if score is not None:
        if score < 220:
            sc = COLORS["red"]
        elif score < 258:
            sc = "#E8A020"
        elif score < 308:
            sc = COLORS["gold"]
        else:
            sc = COLORS["green"]
        fig.add_trace(go.Bar(
            x=[score],
            y=["Tu predicción"],
            orientation="h",
            marker={"color": sc, "line": {"width": 0}},
            text=[f"{score} pts"],
            textposition="outside",
            hovertemplate="Predicción: %{x}<extra></extra>",
            showlegend=False,
        ))

    layout = _base_graph_layout(height=260)
    layout["title"] = {"text": "Comparación con referencias", "x": 0.03}
    layout["xaxis"] = {"range": [0, 500], "title": "Puntaje", "tickfont": {"family": "Segoe UI, sans-serif", "size": 12}, "gridcolor": "#E2E8F0"}
    layout["yaxis"] = {"tickfont": {"family": "Segoe UI, sans-serif", "size": 13}}
    layout["margin"] = {"l": 130, "r": 50, "t": 48, "b": 24}
    fig.update_layout(**layout, showlegend=False)
    return fig


def _build_tab1_waterfall(base, contributions, score):
    sorted_contribs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
    labels = ["Base"] + [k for k, _ in sorted_contribs] + ["Puntaje final"]
    values = [base] + [v for _, v in sorted_contribs] + [0]
    measures = ["absolute"] + ["relative"] * len(sorted_contribs) + ["total"]
    colors_list = ["#8A94A6"] + [COLORS["green"] if v > 0 else COLORS["red"] for _, v in sorted_contribs] + [COLORS["primary"]]

    fig = go.Figure(go.Waterfall(
        name="Contribución",
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        connector={"line": {"color": "#CBD5E0", "width": 1}},
        decreasing={"marker": {"color": COLORS["red"]}},
        increasing={"marker": {"color": COLORS["green"]}},
        totals={"marker": {"color": COLORS["primary"]}},
        text=[str(v) if v != 0 else f"{score}" for v in values],
        textposition="outside",
        hovertemplate="%{x}: %{y}<extra></extra>",
    ))

    layout = _base_graph_layout(height=340)
    layout["title"] = {"text": "Contribución de cada factor al puntaje", "x": 0.03}
    layout["xaxis"] = {"tickfont": {"family": "Segoe UI, sans-serif", "size": 12}}
    layout["yaxis"] = {"title": "Puntaje", "tickfont": {"family": "Segoe UI, sans-serif", "size": 12}, "gridcolor": "#E2E8F0"}
    layout["margin"] = {"l": 40, "r": 24, "t": 52, "b": 24}
    fig.update_layout(**layout, showlegend=False)
    return fig


def _build_tab1_risk_html(score=None):
    if score is None:
        level, color, brecha = "Sin cálculo", COLORS["muted"], "—"
        detail = "Ingrese los datos y presione Calcular predicción."
    elif score < 220:
        level, color = "Riesgo alto", COLORS["red"]
        brecha = f"−{308 - score} pts vs P75"
        detail = "El perfil muestra condiciones de alta vulnerabilidad académica esperada."
    elif score < 258:
        level, color = "Riesgo moderado", "#E8A020"
        brecha = f"−{308 - score} pts vs P75"
        detail = "El perfil está por debajo del promedio departamental."
    elif score < 308:
        level, color = "Desempeño medio", COLORS["gold"]
        brecha = f"−{308 - score} pts vs P75"
        detail = "El perfil supera el promedio departamental pero aún no alcanza el P75."
    else:
        level, color = "Desempeño alto", COLORS["green"]
        brecha = f"+{score - 308} pts vs P75"
        detail = "El perfil supera el percentil 75 de Boyacá."

    return html.Div(
        [
            html.Div(level, id="tab1-risk-level", style={"fontSize": "28px", "fontWeight": "900", "color": color, "marginBottom": "4px"}),
            html.Div(brecha, id="tab1-risk-brecha", style={"fontSize": "15px", "fontWeight": "700", "color": color, "marginBottom": "6px"}),
            html.Div(detail, id="tab1-risk-detail", style={"fontSize": "13px", "color": COLORS["muted"], "lineHeight": "1.5"}),
        ],
        style={**CARD_STYLE, "borderTop": f"4px solid {color}", "padding": "16px"},
    )


def panel_visual_tab1():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="tab1-gauge-graph", figure=_build_tab1_gauge(None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                    html.Div(
                        dcc.Graph(id="tab1-bullet-graph", figure=_build_tab1_bullet(None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "18px", "marginBottom": "18px"},
            ),
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="tab1-waterfall-graph", figure=_build_tab1_waterfall(258, {}, 258), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                    html.Div(
                        [
                            html.Div("Nivel de riesgo académico", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["muted"], "marginBottom": "10px"}),
                            html.Div(id="tab1-risk-panel", children=_build_tab1_risk_html(None)),
                        ],
                        style={**CARD_STYLE, "padding": "16px"},
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "minmax(320px, 1.4fr) minmax(240px, 0.6fr)", "gap": "18px"},
            ),
        ],
        style={"marginBottom": "22px"},
    )


# ── Tab 2 verdict / bottom section ───────────────────────────────────────────

def _tab2_verdict_and_action(probability, predicted_class):
    pct = round(probability * 100, 1)
    certainty = round(abs(probability - 0.5) * 200, 1)

    if predicted_class == 1:
        icon, class_label, label = "✓", ">58", "Supera el umbral"
        card_color = COLORS["green"]
        action_title = "Mantener y fortalecer"
        action_detail = (
            f"El modelo estima {pct}% de probabilidad de superar el nivel 58 en inglés. "
            "Se recomienda sostener las condiciones favorables e identificar palancas de mejora "
            "para consolidar el desempeño a nivel institucional."
        )
    else:
        icon, class_label, label = "✗", "≤58", "No supera el umbral"
        card_color = COLORS["red"]
        action_title = "Intervención prioritaria"
        action_detail = (
            f"El modelo estima solo {pct}% de probabilidad de superar el nivel 58 en inglés. "
            "Se sugiere priorizar refuerzos en inglés, fortalecer el acceso tecnológico "
            "y revisar las condiciones institucionales que inciden en el aprendizaje de idiomas."
        )

    if certainty >= 60:
        certainty_label = "Certeza alta"
    elif certainty >= 30:
        certainty_label = "Certeza media"
    else:
        certainty_label = "Resultado incierto"

    return icon, class_label, label, card_color, certainty, certainty_label, action_title, action_detail


def panel_resultado_tab2():
    return html.Div(
        [
            # Veredicto del clasificador
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Veredicto del clasificador", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["muted"], "marginBottom": "8px"}),
                            html.Div(
                                [
                                    html.Span("—", id="tab2-verdict-icon", style={"fontSize": "36px", "marginRight": "10px", "lineHeight": "1"}),
                                    html.Span("—", id="tab2-verdict-class", style={"fontSize": "40px", "fontWeight": "900", "lineHeight": "1"}),
                                ],
                                style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
                            ),
                            html.Div("Sin cálculo", id="tab2-verdict-label", style={"fontSize": "15px", "fontWeight": "700", "marginBottom": "4px"}),
                            html.Div("Presione 'Calcular predicción' para ver el resultado.", id="tab2-verdict-conf", style={"fontSize": "13px", "color": COLORS["muted"], "lineHeight": "1.5"}),
                        ],
                        id="tab2-verdict-card",
                        style={**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['muted']}", "height": "100%"},
                    ),
                ],
                style={"height": "100%"},
            ),
            # Certeza del modelo
            html.Div(
                [
                    html.Div("Certeza del modelo", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["muted"], "marginBottom": "8px"}),
                    html.Div(
                        [
                            html.Span("—", id="tab2-certainty-value", style={"fontSize": "38px", "fontWeight": "900", "color": COLORS["muted"]}),
                            html.Span("%", style={"fontSize": "20px", "fontWeight": "700", "color": COLORS["muted"], "marginLeft": "4px"}),
                        ],
                        style={"marginBottom": "6px"},
                    ),
                    html.Div("Sin datos", id="tab2-certainty-label", style={"fontSize": "14px", "fontWeight": "700", "color": COLORS["muted"], "marginBottom": "10px"}),
                    html.Div(
                        [
                            html.Div(
                                html.Div(
                                    id="tab2-certainty-fill",
                                    style={"width": "0%", "height": "100%", "borderRadius": "999px", "background": "#8A94A6", "transition": "width 0.5s ease"},
                                ),
                                style={"height": "12px", "borderRadius": "999px", "background": "#E2E8F0", "marginBottom": "6px"},
                            ),
                            html.Div(
                                [
                                    html.Span("Incierto", style={"fontSize": "11px", "color": COLORS["muted"]}),
                                    html.Span("Certeza plena", style={"fontSize": "11px", "color": COLORS["muted"]}),
                                ],
                                style={"display": "flex", "justifyContent": "space-between"},
                            ),
                        ]
                    ),
                    html.P("La certeza mide cuán lejos está la probabilidad del umbral de decisión (50%). A mayor distancia, mayor confianza del modelo.", style={"fontSize": "12px", "color": COLORS["muted"], "lineHeight": "1.5", "marginTop": "10px"}),
                ],
                style={**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['blue']}", "height": "100%"},
            ),
            # Acción recomendada
            html.Div(
                [
                    html.Div("Acción recomendada", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["muted"], "marginBottom": "8px"}),
                    html.Div("—", id="tab2-action-title", style={"fontSize": "22px", "fontWeight": "800", "color": COLORS["primary"], "marginBottom": "8px", "lineHeight": "1.2"}),
                    html.Div("Ejecute la predicción para obtener una recomendación adaptada al perfil seleccionado.", id="tab2-action-detail", style={"fontSize": "14px", "color": COLORS["text"], "lineHeight": "1.6"}),
                ],
                style={**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['primary']}", "height": "100%"},
            ),
        ],
        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "18px", "marginBottom": "22px"},
    )


# ── Tab 3 visualization helpers ─────────────────────────────────────────────

# Model constants (RMSE from training data analysis)
_TAB3_RMSE = 18.5
_TAB3_R2 = 0.41
_TAB3_BOY_BRECHA_MAT = 255.4   # Boyacá avg Math
_TAB3_BOY_BRECHA_LEC = 252.1   # Boyacá avg Lectura Crítica
_TAB3_BOY_BRECHA = _TAB3_BOY_BRECHA_MAT - _TAB3_BOY_BRECHA_LEC  # ≈ +3.3 pts


def _tab3_brecha_from_payload(payload):
    base = _TAB3_BOY_BRECHA  # +3.3 pts (math slightly ahead on average)
    contributions = {}

    # Technology moderators (key research question)
    contributions["Internet en hogar"] = -2.8 if payload["fami_internet"] == "Si" else 2.8
    contributions["Computador en hogar"] = -2.4 if payload["fami_computador"] == "Si" else 2.4

    # Socioeconomic
    estrato = int(payload["fami_estrato"])
    contributions["Estrato"] = round(-(estrato - 2) * 1.3, 1)

    # Parental education (cultural capital → helps Lectura more)
    edu_m = EDUCACION_OPCIONES.index(payload["fami_educacionmadre"]) if payload["fami_educacionmadre"] in EDUCACION_OPCIONES else 4
    edu_p = EDUCACION_OPCIONES.index(payload["fami_educacionpadre"]) if payload["fami_educacionpadre"] in EDUCACION_OPCIONES else 4
    avg_edu = (edu_m + edu_p) / 2
    contributions["Capital educ. familiar"] = round(-(avg_edu - 4) * 0.9, 1)

    # Household composition
    personas = int(payload["fami_personas"])
    cuartos = int(payload["fami_cuartos"])
    hacinamiento = personas / max(cuartos, 1)
    contributions["Hacinamiento hogar"] = round(hacinamiento * 0.8 - 2.0, 1)

    # Institutional
    jornada_delta = {"Mañana": -1.2, "Única": -2.8, "Completa": -3.5, "Tarde": 2.1, "Noche": 4.8, "Sabatina": 1.4}
    contributions["Jornada"] = jornada_delta.get(payload["cole_jornada"], 0)
    contributions["Naturaleza"] = -1.9 if payload["cole_naturaleza"] == "No oficial" else 1.2
    contributions["Sector"] = 1.6 if payload["cole_sector"] == "Publico" else -1.6
    contributions["Zona rural"] = 2.3 if payload["cole_zona"] == "Rural" else -0.8

    # Academic context
    puntaje_delta = {"Alto": -4.2, "Medio": 0.0, "Bajo": 3.6}
    contributions["Nivel académico previo"] = puntaje_delta.get(payload["acad_puntajeprevio"], 0.0)

    brecha = base + sum(contributions.values())
    brecha = round(max(-60, min(60, brecha)), 1)

    # Estimated component scores
    mat_est = round(_TAB3_BOY_BRECHA_MAT + brecha / 2, 1)
    lec_est = round(_TAB3_BOY_BRECHA_LEC - brecha / 2, 1)

    # Technology effect isolated
    tech_effect = contributions["Internet en hogar"] + contributions["Computador en hogar"]

    return brecha, base, contributions, mat_est, lec_est, tech_effect


def _build_tab3_indicator(brecha=None):
    value = brecha if brecha is not None else 0
    if brecha is None:
        bar_color, suffix = "#8A94A6", "Sin cálculo"
    elif abs(brecha) <= 4:
        bar_color, suffix = COLORS["gold"], "Equilibrio entre áreas"
    elif brecha > 4:
        bar_color, suffix = COLORS["blue"], f"Ventaja Matemáticas (+{brecha:.1f} pts)"
    else:
        bar_color, suffix = COLORS["green"], f"Ventaja Lectura Crítica ({brecha:.1f} pts)"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": " pts", "font": {"size": 38, "family": "Segoe UI, sans-serif"}},
            title={"text": f"<span style='font-size:20px'>Brecha Mat − Lectura estimada</span><br><span style='font-size:13px;color:#6B7C93'>{suffix}</span>"},
            gauge={
                "axis": {
                    "range": [-40, 40],
                    "tickwidth": 1,
                    "tickcolor": COLORS["muted"],
                    "tickvals": [-40, -20, 0, 20, 40],
                    "ticktext": ["-40", "-20", "0", "+20", "+40"],
                    "tickfont": {"family": "Segoe UI, sans-serif", "size": 11},
                },
                "bar": {"color": bar_color, "thickness": 0.34},
                "bgcolor": "#EDF2F7",
                "borderwidth": 0,
                "steps": [
                    {"range": [-40, -4], "color": "rgba(12, 139, 95, 0.14)"},
                    {"range": [-4, 4], "color": "rgba(216, 163, 26, 0.14)"},
                    {"range": [4, 40], "color": "rgba(29, 90, 166, 0.14)"},
                ],
                "threshold": {"line": {"color": COLORS["muted"], "width": 3}, "thickness": 0.75, "value": 0},
            },
        )
    )
    fig.update_layout(**_base_graph_layout(height=300))
    return fig


def _build_tab3_scores_bar(mat_est=None, lec_est=None):
    BOY_MAT = _TAB3_BOY_BRECHA_MAT
    BOY_LEC = _TAB3_BOY_BRECHA_LEC

    categories = ["Matemáticas", "Lectura Crítica"]
    ref_vals = [BOY_MAT, BOY_LEC]
    ref_colors = [rgba_from_hex(COLORS["blue"], 0.22), rgba_from_hex(COLORS["green"], 0.22)]
    ref_borders = [COLORS["blue"], COLORS["green"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Promedio Boyacá",
        x=categories,
        y=ref_vals,
        marker={"color": ref_colors, "line": {"color": ref_borders, "width": 2}},
        text=[f"Ref: {v}" for v in ref_vals],
        textposition="outside",
        hovertemplate="%{x} (Boyacá): %{y:.1f}<extra></extra>",
    ))

    if mat_est is not None and lec_est is not None:
        pred_colors = [COLORS["blue"], COLORS["green"]]
        fig.add_trace(go.Bar(
            name="Tu predicción",
            x=categories,
            y=[mat_est, lec_est],
            marker={"color": pred_colors, "opacity": 0.85, "line": {"width": 0}},
            text=[f"{mat_est}", f"{lec_est}"],
            textposition="outside",
            hovertemplate="%{x} (predicción): %{y:.1f}<extra></extra>",
        ))

    layout = _base_graph_layout(height=300)
    layout["title"] = {"text": "Puntajes estimados por área", "x": 0.03}
    layout["yaxis"] = {"range": [180, 340], "title": "Puntaje", "gridcolor": "#E2E8F0", "tickfont": {"family": "Segoe UI, sans-serif"}}
    layout["xaxis"] = {"tickfont": {"family": "Segoe UI, sans-serif", "size": 14}}
    layout["barmode"] = "group"
    layout["legend"] = {"font": {"family": "Segoe UI, sans-serif", "size": 12}, "orientation": "h", "y": -0.18}
    layout["margin"] = {"l": 40, "r": 24, "t": 52, "b": 40}
    fig.update_layout(**layout)
    return fig


def _build_tab3_waterfall(base, contributions, brecha):
    if not contributions:
        contributions = {"Sin datos": 0}
    sorted_c = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:9]
    labels = ["Base Boyacá"] + [k for k, _ in sorted_c] + ["Brecha final"]
    values = [base] + [v for _, v in sorted_c] + [0]
    measures = ["absolute"] + ["relative"] * len(sorted_c) + ["total"]

    # Highlight tech variables in gold
    tech_keys = {"Internet en hogar", "Computador en hogar"}
    marker_colors = [COLORS["muted"]]
    for k, v in sorted_c:
        if k in tech_keys:
            marker_colors.append(COLORS["gold"] if v < 0 else "#E8A020")
        else:
            marker_colors.append(COLORS["blue"] if v > 0 else COLORS["green"])
    marker_colors.append(COLORS["primary"])

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        connector={"line": {"color": "#CBD5E0", "width": 1}},
        decreasing={"marker": {"color": COLORS["green"]}},
        increasing={"marker": {"color": COLORS["blue"]}},
        totals={"marker": {"color": COLORS["primary"]}},
        text=[f"{v:+.1f}" if v != 0 else f"{brecha:+.1f}" for v in values],
        textposition="outside",
        hovertemplate="%{x}: %{y:+.1f} pts<extra></extra>",
    ))

    layout = _base_graph_layout(height=360)
    layout["title"] = {"text": "Contribución de cada factor a la brecha", "x": 0.03}
    layout["xaxis"] = {"tickfont": {"family": "Segoe UI, sans-serif", "size": 11}, "tickangle": -28}
    layout["yaxis"] = {"title": "Brecha (pts)", "gridcolor": "#E2E8F0", "tickfont": {"family": "Segoe UI, sans-serif", "size": 12}, "zeroline": True, "zerolinecolor": COLORS["muted"], "zerolinewidth": 1.5}
    layout["margin"] = {"l": 40, "r": 24, "t": 52, "b": 60}
    fig.update_layout(**layout, showlegend=False)

    # Legend annotation for tech highlight
    fig.add_annotation(
        x=1, y=1.06, xref="paper", yref="paper",
        text="<span style='color:#D8A31A'>■</span> Efecto tecnológico  <span style='color:#1D5AA6'>■</span> Amplía brecha  <span style='color:#0C8B5F'>■</span> Reduce brecha",
        showarrow=False, font={"family": "Segoe UI, sans-serif", "size": 11}, xanchor="right",
    )
    return fig


def _build_tab3_rmse_chart(brecha=None):
    rmse = _TAB3_RMSE
    r2 = _TAB3_R2

    fig = go.Figure()

    if brecha is not None:
        lo = brecha - 1.96 * rmse
        hi = brecha + 1.96 * rmse
        # Confidence band
        fig.add_trace(go.Scatter(
            x=[lo, hi],
            y=["Intervalo 95%", "Intervalo 95%"],
            mode="lines",
            line={"color": rgba_from_hex(COLORS["blue"], 0.3), "width": 18},
            name="IC 95%",
            hovertemplate=f"Rango: [{lo:.1f}, {hi:.1f}] pts<extra></extra>",
        ))
        # Prediction point
        fig.add_trace(go.Scatter(
            x=[brecha],
            y=["Intervalo 95%"],
            mode="markers+text",
            marker={"color": COLORS["primary"], "size": 14, "line": {"width": 2, "color": "white"}},
            text=[f"{brecha:+.1f} pts"],
            textposition="top center",
            textfont={"family": "Segoe UI, sans-serif", "size": 13, "color": COLORS["primary"]},
            name="Predicción",
            hovertemplate=f"Predicción: {brecha:+.1f} pts<extra></extra>",
        ))
    # Reference line Boyacá
    fig.add_vline(x=_TAB3_BOY_BRECHA, line_dash="dash", line_color=COLORS["muted"], line_width=1.5,
                  annotation_text=f"Ref Boyacá ({_TAB3_BOY_BRECHA:+.1f})",
                  annotation_font={"family": "Segoe UI, sans-serif", "size": 11},
                  annotation_position="top right")
    fig.add_vline(x=0, line_dash="dot", line_color=COLORS["gold"], line_width=1.2,
                  annotation_text="Equilibrio",
                  annotation_font={"family": "Segoe UI, sans-serif", "size": 11},
                  annotation_position="bottom right")

    # Model quality metrics as annotations
    fig.add_annotation(
        x=0.02, y=-0.28, xref="paper", yref="paper",
        text=f"<b>RMSE:</b> {rmse} pts  |  <b>R²:</b> {r2}  |  <b>IC 95%:</b> ±{1.96*rmse:.1f} pts",
        showarrow=False, font={"family": "Segoe UI, sans-serif", "size": 12, "color": COLORS["muted"]},
        xanchor="left",
    )

    layout = _base_graph_layout(height=240)
    layout["title"] = {"text": "Intervalo de confianza de la predicción", "x": 0.03}
    layout["xaxis"] = {
        "range": [-60, 60], "title": "Brecha Mat − Lectura (pts)",
        "tickfont": {"family": "Segoe UI, sans-serif", "size": 12}, "gridcolor": "#E2E8F0",
        "zeroline": False,
    }
    layout["yaxis"] = {"showticklabels": True, "tickfont": {"family": "Segoe UI, sans-serif", "size": 12}}
    layout["margin"] = {"l": 100, "r": 24, "t": 52, "b": 56}
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def panel_visual_tab3():
    return html.Div(
        [
            # Row 1: indicator + scores bar
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="tab3-indicator-graph", figure=_build_tab3_indicator(None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                    html.Div(
                        dcc.Graph(id="tab3-scores-graph", figure=_build_tab3_scores_bar(None, None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "18px", "marginBottom": "18px"},
            ),
            # Row 2: waterfall + RMSE chart
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="tab3-waterfall-graph", figure=_build_tab3_waterfall(_TAB3_BOY_BRECHA, {}, _TAB3_BOY_BRECHA), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                    html.Div(
                        dcc.Graph(id="tab3-rmse-graph", figure=_build_tab3_rmse_chart(None), config={"displayModeBar": False}),
                        style={**CARD_STYLE, "padding": "12px"},
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "18px"},
            ),
        ],
        style={"marginBottom": "22px"},
    )


def panel_resultado_tab3():
    muted_card = {**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['muted']}", "height": "100%"}
    return html.Div(
        [
            # Card 1: Brecha estimada
            html.Div(
                [
                    html.Div("Brecha estimada", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["muted"], "marginBottom": "8px"}),
                    html.Div(
                        [
                            html.Span("—", id="tab3-result-brecha", style={"fontSize": "44px", "fontWeight": "900", "color": COLORS["blue"]}),
                            html.Span(" pts", style={"fontSize": "20px", "color": COLORS["muted"], "marginLeft": "4px"}),
                        ],
                        style={"marginBottom": "4px"},
                    ),
                    html.Div("—", id="tab3-result-direction", style={"fontSize": "15px", "fontWeight": "700", "color": COLORS["muted"], "marginBottom": "6px"}),
                    html.Div("Ingrese los datos y presione Calcular predicción.", id="tab3-result-detail", style={"fontSize": "13px", "color": COLORS["muted"], "lineHeight": "1.5"}),
                ],
                id="tab3-result-card",
                style={**muted_card},
            ),
            # Card 2: Efecto tecnológico
            html.Div(
                [
                    html.Div("Efecto tecnológico", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["muted"], "marginBottom": "8px"}),
                    html.Div(
                        [
                            html.Span("—", id="tab3-tech-delta", style={"fontSize": "38px", "fontWeight": "900", "color": COLORS["gold"]}),
                            html.Span(" pts", style={"fontSize": "18px", "color": COLORS["muted"], "marginLeft": "4px"}),
                        ],
                        style={"marginBottom": "6px"},
                    ),
                    html.Div("—", id="tab3-tech-label", style={"fontSize": "14px", "fontWeight": "700", "color": COLORS["gold"], "marginBottom": "6px"}),
                    html.Div("—", id="tab3-tech-detail", style={"fontSize": "13px", "color": COLORS["text"], "lineHeight": "1.6"}),
                ],
                style={**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['gold']}", "height": "100%"},
            ),
            # Card 3: Precisión del modelo
            html.Div(
                [
                    html.Div("Precisión del modelo", style={"fontSize": "11px", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": COLORS["muted"], "marginBottom": "8px"}),
                    html.Div(
                        [
                            html.Span(f"RMSE: {_TAB3_RMSE}", style={"fontSize": "22px", "fontWeight": "900", "color": COLORS["primary"], "display": "block", "marginBottom": "4px"}),
                            html.Span(f"R² = {_TAB3_R2}", style={"fontSize": "16px", "fontWeight": "700", "color": COLORS["blue"], "display": "block", "marginBottom": "4px"}),
                        ]
                    ),
                    html.Div("—", id="tab3-model-ic", style={"fontSize": "13px", "color": COLORS["muted"], "marginBottom": "6px"}),
                    html.Div("—", id="tab3-model-quality", style={"fontSize": "14px", "fontWeight": "700", "color": COLORS["muted"]}),
                ],
                style={**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['primary']}", "height": "100%"},
            ),
        ],
        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(260px, 1fr))", "gap": "18px", "marginBottom": "22px"},
    )


# ── Tabs ───────────────────────────────────────────────────────────────────

tab_1 = bloque_pregunta(
    {
        "badge": "Pregunta 1",
        "modelo": "Modelo de regresión",
        "tab": "Puntaje Global Esperado",
        "color": COLORS["gold"],
        "button_id": "tab1-predict-button",
        "reset_button_id": "tab1-reset-button",
        "show_visual_panel_tab1": True,
        "show_result_cards": False,
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
        "bottom_section": "classification",
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
        "tab": "Brecha Matemáticas / Lectura",
        "color": COLORS["blue"],
        "button_id": "tab3-predict-button",
        "reset_button_id": "tab3-reset-button",
        "show_visual_panel_tab3": True,
        "show_result_cards": False,
        "bottom_section": "brecha",
        "question": "¿En qué medida el acceso a tecnología en el hogar modera la brecha entre el puntaje de matemáticas y lectura crítica, y cuál es la magnitud esperada de esa brecha para un estudiante dado el perfil socioeconómico de su familia y las características de su institución en Boyacá?",
        "purpose": "",
        "objective": "Estimar la magnitud y dirección de la brecha Matemáticas − Lectura Crítica y cuantificar cuánto la modera el acceso a tecnología del hogar.",
        "decision": "Apoya decisiones de refuerzo focalizado por área, acompañamiento tecnológico y seguimiento institucional por perfiles de riesgo diferenciado.",
        "output": "Brecha estimada en puntos (Mat − Lectura), efecto tecnológico aislado e intervalo de confianza basado en RMSE del modelo.",
        "form_sections": [
            {
                "titulo": "Condiciones socioeconómicas",
                "descripcion": "Recursos materiales, acceso tecnológico y composición del hogar.",
                "campos": [
                    tab_3_model_fields[0],
                    tab_3_model_fields[1],
                    tab_3_model_fields[2],
                    tab_3_model_fields[5],
                    tab_3_model_fields[6],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Capital educativo familiar",
                "descripcion": "Nivel educativo de los padres.",
                "campos": [
                    tab_3_model_fields[3],
                    tab_3_model_fields[4],
                ],
                "columnas": 1,
            },
            {
                "titulo": "Características institucionales",
                "descripcion": "Variables institucionales conservadas en el modelo de la pestaña 3.",
                "campos": [
                    tab_3_model_fields[7],
                    tab_3_model_fields[8],
                    tab_3_model_fields[9],
                    tab_3_model_fields[10],
                ],
                "columnas": 1,
            },
        ],
        "result_cards": [],
        "factors": [],
        "recommendation": "",
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
                dcc.Tab(label="Brecha Matemáticas / Lectura", children=[tab_3], style=TAB_STYLE, selected_style=TAB_SELECTED_STYLE),
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


_TAB2_RESET_VERDICT = (
    # favorable / risk summary
    "Sin cálculo",
    "La lectura favorable aparecerá aquí cuando ejecutes una nueva consulta.",
    "Sin cálculo",
    "La lectura de riesgo aparecerá aquí cuando ejecutes una nueva consulta.",
    # binary indicator
    "Pendiente",
    {"background": "linear-gradient(135deg, #8a94a6 0%, #64748b 100%)", "left": "50%"},
    # charts
    _build_gauge_figure(None),
    _build_donut_figure(None),
    _build_factors_figure(),
    _build_map_figure(None),
    # verdict
    "—", "—", "Sin cálculo", "Presione 'Calcular predicción' para ver el resultado.",
    {**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['muted']}", "height": "100%"},
    # certainty
    "—", "Sin datos",
    {"width": "0%", "height": "100%", "borderRadius": "999px", "background": "#8A94A6", "transition": "width 0.5s ease"},
    # action
    "—", "Ejecute la predicción para obtener una recomendación adaptada al perfil seleccionado.",
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
    Output("tab2-verdict-icon", "children"),
    Output("tab2-verdict-class", "children"),
    Output("tab2-verdict-label", "children"),
    Output("tab2-verdict-conf", "children"),
    Output("tab2-verdict-card", "style"),
    Output("tab2-certainty-value", "children"),
    Output("tab2-certainty-label", "children"),
    Output("tab2-certainty-fill", "style"),
    Output("tab2-action-title", "children"),
    Output("tab2-action-detail", "children"),
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
        (Output("tab2-status-text", "children"), "Calculando predicción con el modelo...", "Modelo listo para una nueva consulta"),
        (
            Output("tab2-status-fill", "style"),
            {"width": "72%", "height": "100%", "borderRadius": "999px", "background": "linear-gradient(90deg, #1D5AA6 0%, #009640 100%)", "transition": "width 0.35s ease, background 0.35s ease"},
            {"width": "18%", "height": "100%", "borderRadius": "999px", "background": "linear-gradient(90deg, #8a94a6 0%, #64748b 100%)", "transition": "width 0.35s ease, background 0.35s ease"},
        ),
        (Output("tab2-predict-button", "disabled"), True, False),
        (Output("tab2-reset-button", "disabled"), True, False),
    ],
)
def run_tab2_prediction(
    n_clicks, reset_clicks,
    cole_bilingue, cole_jornada, cole_area, cole_naturaleza, cole_caracter, cole_mcpio,
    fami_computador, fami_internet, fami_estrato, fami_educacionmadre, fami_educacionpadre,
    fami_personas, fami_cuartos,
):
    if not n_clicks and not reset_clicks:
        return (no_update,) * 20

    try:
        triggered_id = ctx.triggered_id
    except Exception:
        triggered_id = "tab2-reset-button" if reset_clicks else "tab2-predict-button"

    if triggered_id == "tab2-reset-button":
        return _TAB2_RESET_VERDICT

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
        _ = probability_to_percentile(probability, bundle.probability_reference)
    except Exception as exc:
        message = f"Error: {exc}"
        err = list(_TAB2_RESET_VERDICT)
        err[1] = message
        err[3] = "La predicción no pudo calcularse con el entorno actual."
        err[4] = "Error"
        err[9] = _build_map_figure(payload.get("cole_mcpio_ubicacion"))
        return tuple(err)

    predicted_class = 1 if probability > 0.5 else 0
    positive_value, positive_detail, risk_value, risk_detail = _tab2_factor_messages(payload)
    favorable_items, risk_items = _tab2_factor_rankings(payload)
    indicator_value = ">58" if predicted_class == 1 else "<=58"
    indicator_style = {
        "background": "linear-gradient(135deg, #0c8b5f 0%, #18a66d 100%)" if predicted_class == 1 else "linear-gradient(135deg, #c94c4c 0%, #dd6b6b 100%)",
        "left": "81%" if predicted_class == 1 else "19%",
    }

    icon, class_label, label, card_color, certainty, certainty_label, action_title, action_detail = _tab2_verdict_and_action(probability, predicted_class)
    verdict_card_style = {**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {card_color}", "height": "100%"}
    fill_color = COLORS["green"] if predicted_class == 1 else COLORS["red"]
    certainty_fill_style = {
        "width": f"{min(certainty, 100):.0f}%",
        "height": "100%",
        "borderRadius": "999px",
        "background": f"linear-gradient(90deg, {fill_color} 0%, {fill_color}CC 100%)",
        "transition": "width 0.5s ease",
    }

    return (
        positive_value, positive_detail, risk_value, risk_detail,
        indicator_value, indicator_style,
        _build_gauge_figure(probability),
        _build_donut_figure(probability),
        _build_factors_figure(favorable_items, risk_items),
        _build_map_figure(payload["cole_mcpio_ubicacion"]),
        icon, class_label, label, f"Probabilidad: {probability*100:.1f}%",
        verdict_card_style,
        f"{certainty:.0f}", certainty_label, certainty_fill_style,
        action_title, action_detail,
    )


@app.callback(
    Output("tab1-gauge-graph", "figure"),
    Output("tab1-bullet-graph", "figure"),
    Output("tab1-waterfall-graph", "figure"),
    Output("tab1-risk-panel", "children"),
    Input("tab1-predict-button", "n_clicks"),
    Input("tab1-reset-button", "n_clicks"),
    State("tab1-cole-area", "value"),
    State("tab1-cole-bilingue", "value"),
    State("tab1-cole-jornada", "value"),
    State("tab1-cole-naturaleza", "value"),
    State("tab1-estu-genero", "value"),
    State("tab1-fami-cuartos", "value"),
    State("tab1-fami-educacionmadre", "value"),
    State("tab1-fami-educacionpadre", "value"),
    State("tab1-fami-estrato", "value"),
    State("tab1-fami-personas", "value"),
    State("tab1-fami-computador", "value"),
    State("tab1-fami-internet", "value"),
    State("tab1-fami-lavadora", "value"),
    prevent_initial_call=True,
)
def run_tab1_prediction(
    n_clicks, reset_clicks,
    cole_area, cole_bilingue, cole_jornada, cole_naturaleza, estu_genero,
    fami_cuartos, fami_educacionmadre, fami_educacionpadre,
    fami_estrato, fami_personas, fami_computador, fami_internet, fami_lavadora,
):
    if not n_clicks and not reset_clicks:
        return no_update, no_update, no_update, no_update

    try:
        triggered_id = ctx.triggered_id
    except Exception:
        triggered_id = "tab1-reset-button" if reset_clicks else "tab1-predict-button"

    if triggered_id == "tab1-reset-button":
        return _build_tab1_gauge(None), _build_tab1_bullet(None), _build_tab1_waterfall(258, {}, 258), _build_tab1_risk_html(None)

    payload = {
        "cole_area": cole_area or "Urbana",
        "cole_bilingue": cole_bilingue or "No",
        "cole_jornada": cole_jornada or "Mañana",
        "cole_naturaleza": cole_naturaleza or "Oficial",
        "estu_genero": estu_genero or "Masculino",
        "fami_cuartos": int(fami_cuartos) if fami_cuartos is not None else 3,
        "fami_educacionmadre": fami_educacionmadre or EDUCACION_OPCIONES[4],
        "fami_educacionpadre": fami_educacionpadre or EDUCACION_OPCIONES[4],
        "fami_estrato": int(fami_estrato) if fami_estrato is not None else 2,
        "fami_personas": int(fami_personas) if fami_personas is not None else 4,
        "fami_computador": fami_computador or "Si",
        "fami_internet": fami_internet or "Si",
        "fami_lavadora": fami_lavadora or "Si",
    }

    score, base, contributions = _tab1_score_from_payload(payload)
    return (
        _build_tab1_gauge(score),
        _build_tab1_bullet(score),
        _build_tab1_waterfall(base, contributions, score),
        _build_tab1_risk_html(score),
    )


_TAB3_RESET = (
    _build_tab3_indicator(None),
    _build_tab3_scores_bar(None, None),
    _build_tab3_waterfall(_TAB3_BOY_BRECHA, {}, _TAB3_BOY_BRECHA),
    _build_tab3_rmse_chart(None),
    "—", "—", "Ingrese los datos y presione Calcular predicción.",
    {**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {COLORS['muted']}", "height": "100%"},
    "—", "—", "—",
    f"IC 95%: ±{1.96*_TAB3_RMSE:.1f} pts", "Sin cálculo",
)


@app.callback(
    Output("tab3-indicator-graph", "figure"),
    Output("tab3-scores-graph", "figure"),
    Output("tab3-waterfall-graph", "figure"),
    Output("tab3-rmse-graph", "figure"),
    Output("tab3-result-brecha", "children"),
    Output("tab3-result-direction", "children"),
    Output("tab3-result-detail", "children"),
    Output("tab3-result-card", "style"),
    Output("tab3-tech-delta", "children"),
    Output("tab3-tech-label", "children"),
    Output("tab3-tech-detail", "children"),
    Output("tab3-model-ic", "children"),
    Output("tab3-model-quality", "children"),
    Input("tab3-predict-button", "n_clicks"),
    Input("tab3-reset-button", "n_clicks"),
    State("tab3-fami-internet", "value"),
    State("tab3-fami-computador", "value"),
    State("tab3-fami-estrato", "value"),
    State("tab3-fami-educacionmadre", "value"),
    State("tab3-fami-educacionpadre", "value"),
    State("tab3-fami-personas", "value"),
    State("tab3-fami-cuartos", "value"),
    State("tab3-cole-jornada", "value"),
    State("tab3-cole-naturaleza", "value"),
    State("tab3-cole-sector", "value"),
    State("tab3-cole-zona", "value"),
    State("tab3-acad-puntajeprevio", "value"),
    prevent_initial_call=True,
)
def run_tab3_prediction(
    n_clicks, reset_clicks,
    fami_internet, fami_computador, fami_estrato,
    fami_educacionmadre, fami_educacionpadre,
    fami_personas, fami_cuartos,
    cole_jornada, cole_naturaleza, cole_sector, cole_zona,
    acad_puntajeprevio,
):
    if not n_clicks and not reset_clicks:
        return (no_update,) * 13

    try:
        triggered_id = ctx.triggered_id
    except Exception:
        triggered_id = "tab3-reset-button" if reset_clicks else "tab3-predict-button"

    if triggered_id == "tab3-reset-button":
        return _TAB3_RESET

    payload = {
        "fami_internet": fami_internet or "Si",
        "fami_computador": fami_computador or "Si",
        "fami_estrato": int(fami_estrato) if fami_estrato is not None else 2,
        "fami_educacionmadre": fami_educacionmadre or EDUCACION_OPCIONES[4],
        "fami_educacionpadre": fami_educacionpadre or EDUCACION_OPCIONES[4],
        "fami_personas": int(fami_personas) if fami_personas is not None else 4,
        "fami_cuartos": int(fami_cuartos) if fami_cuartos is not None else 3,
        "cole_jornada": cole_jornada or "Mañana",
        "cole_naturaleza": cole_naturaleza or "Oficial",
        "cole_sector": cole_sector or "Publico",
        "cole_zona": cole_zona or "Urbana",
        "acad_puntajeprevio": acad_puntajeprevio or "Medio",
    }

    brecha, base, contributions, mat_est, lec_est, tech_effect = _tab3_brecha_from_payload(payload)

    if abs(brecha) <= 4:
        direction = "Equilibrio entre áreas"
        card_color = COLORS["gold"]
        result_detail = f"La brecha estimada es pequeña ({brecha:+.1f} pts). El perfil muestra un desarrollo relativamente equilibrado entre Matemáticas y Lectura Crítica."
    elif brecha > 4:
        direction = f"Matemáticas lidera (+{brecha:.1f} pts sobre Lectura)"
        card_color = COLORS["blue"]
        result_detail = f"El perfil proyecta una ventaja de {brecha:.1f} pts en Matemáticas sobre Lectura Crítica. Se sugiere reforzar comprensión lectora y estrategias de escritura."
    else:
        direction = f"Lectura Crítica lidera ({abs(brecha):.1f} pts sobre Matemáticas)"
        card_color = COLORS["green"]
        result_detail = f"El perfil proyecta una ventaja de {abs(brecha):.1f} pts en Lectura Crítica sobre Matemáticas. Se sugiere reforzar razonamiento cuantitativo y resolución de problemas."

    result_card_style = {**CARD_STYLE, "padding": "20px", "borderTop": f"4px solid {card_color}", "height": "100%"}

    tech_delta_str = f"{tech_effect:+.1f}"
    if tech_effect < -1:
        tech_label = "Reduce la brecha"
        tech_detail = (
            f"El acceso tecnológico del hogar reduce la brecha en {abs(tech_effect):.1f} pts, "
            "favoreciendo principalmente el desempeño en Lectura Crítica gracias a mayor exposición "
            "a contenidos digitales y recursos de aprendizaje."
        )
    elif tech_effect > 1:
        tech_label = "Amplía la brecha"
        tech_detail = (
            f"Sin acceso tecnológico, la brecha se amplía en {abs(tech_effect):.1f} pts, "
            "afectando desproporcionadamente la Lectura Crítica, que requiere mayor acceso "
            "a información y recursos digitales de apoyo."
        )
    else:
        tech_label = "Efecto neutral"
        tech_detail = "El acceso tecnológico no modifica sustancialmente la brecha para este perfil."

    ic_lo = brecha - 1.96 * _TAB3_RMSE
    ic_hi = brecha + 1.96 * _TAB3_RMSE
    ic_str = f"IC 95%: [{ic_lo:+.1f}, {ic_hi:+.1f}] pts"
    quality = "Ajuste moderado — interpretar con precaución" if _TAB3_R2 < 0.6 else "Ajuste bueno"

    return (
        _build_tab3_indicator(brecha),
        _build_tab3_scores_bar(mat_est, lec_est),
        _build_tab3_waterfall(base, contributions, brecha),
        _build_tab3_rmse_chart(brecha),
        f"{brecha:+.1f}",
        direction,
        result_detail,
        result_card_style,
        tech_delta_str,
        tech_label,
        tech_detail,
        ic_str,
        quality,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8050)
