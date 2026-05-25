from dash import Dash, dcc, html


app = Dash(__name__)
app.title = "Saber 11 Boyaca"


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
                "fontSize": "12px",
                "fontWeight": "700",
                "letterSpacing": "0.08em",
                "textTransform": "uppercase",
                "color": COLORS["muted"],
                "marginBottom": "10px",
            },
        )
    ]

    if subtitulo:
        children.append(
            html.Div(
                subtitulo,
                style={
                    "fontSize": "28px",
                    "fontWeight": "800",
                    "color": borde,
                    "lineHeight": "1",
                    "marginBottom": "12px",
                },
            )
        )

    children.append(
        html.P(
            texto,
            style={
                "margin": "0",
                "color": COLORS["text"],
                "fontSize": "15px",
                "lineHeight": "1.7",
            },
        )
    )

    return html.Div(
        children,
        className=f"tab-summary-card {class_name}".strip(),
        style={
            **CARD_STYLE,
            "borderTop": f"4px solid {borde}",
            "height": "100%",
            "minHeight": "132px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "flex-start",
            "padding": "18px 20px",
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


def campo_dropdown(label, options, placeholder):
    return html.Div(
        [
            html.Label(label, style=LABEL_STYLE),
            dcc.Dropdown(
                options=[{"label": option, "value": option} for option in options],
                placeholder=placeholder,
                clearable=False,
                style=INPUT_STYLE,
            ),
        ]
    )


def campo_formulario(field):
    if isinstance(field, dict):
        tipo = field.get("tipo", "dropdown")
        label = field["label"]

        if tipo == "radio":
            return html.Div(
                [
                    html.Label(label, style=LABEL_STYLE),
                    dcc.RadioItems(
                        options=field["options"],
                        value=field.get("value"),
                        className=field.get("className", "segmented-control"),
                        inputClassName="segmented-control-input",
                        labelClassName="segmented-control-label",
                        inline=field.get("inline", True),
                    ),
                ]
            )

        if tipo == "slider":
            return html.Div(
                [
                    html.Label(label, style=LABEL_STYLE),
                    html.Div(
                        [
                            dcc.Slider(
                                min=field.get("min", 1),
                                max=field.get("max", 10),
                                step=field.get("step", 1),
                                value=field.get("value", 5),
                                marks=field.get("marks"),
                                tooltip={"placement": "bottom", "always_visible": True},
                                className=field.get("className", "numeric-slider"),
                            )
                        ],
                        className="slider-shell",
                    ),
                ]
            )

        if tipo == "icon_scale":
            return html.Div(
                [
                    html.Label(label, style=LABEL_STYLE),
                    dcc.RadioItems(
                        options=field["options"],
                        value=field.get("value"),
                        className=field.get("className", "icon-scale-group"),
                        inputClassName="segmented-control-input",
                        labelClassName="segmented-control-label",
                        inline=field.get("inline", True),
                    ),
                ]
            )

        return campo_dropdown(label, field["options"], field.get("placeholder", "Seleccione una opcion"))

    label, options, placeholder = field
    return campo_dropdown(label, options, placeholder)


def grupo_formulario(titulo, color, campos):
    return html.Div(
        [
            html.Div(
                titulo,
                style={
                    "fontSize": "13px",
                    "fontWeight": "800",
                    "letterSpacing": "0.06em",
                    "textTransform": "uppercase",
                    "color": color,
                    "marginBottom": "14px",
                },
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
        style={
            **CARD_STYLE,
            "borderLeft": f"5px solid {color}",
            "height": "100%",
        },
    )


def grupo_formulario_columnas(titulo, color, campos, columnas=3):
    return html.Div(
        [
            html.Div(
                titulo,
                style={
                    "fontSize": "13px",
                    "fontWeight": "800",
                    "letterSpacing": "0.06em",
                    "textTransform": "uppercase",
                    "color": color,
                    "marginBottom": "14px",
                },
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
                    )
                )
        else:
            titulo, campos = section
            if campos:
                rendered.append(grupo_formulario(titulo, config["color"], campos))

    return rendered


def tarjeta_resultado(titulo, valor, detalle, color, grande=False):
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
            html.Div(
                valor,
                style={
                    "fontSize": "40px" if grande else "24px",
                    "fontWeight": "800",
                    "lineHeight": "1.05",
                    "color": color,
                    "marginBottom": "12px",
                },
            ),
            html.P(
                detalle,
                style={
                    "margin": "0",
                    "color": COLORS["text"],
                    "fontSize": "14px",
                    "lineHeight": "1.6",
                },
            ),
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


def boton_prediccion(color):
    return html.Button(
        "Calcular predicción",
        style={
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
        },
    )


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
                            html.Div("No alcanza el umbral", className="binary-level-title"),
                            html.Div("0 a 58", className="binary-level-range"),
                            html.Div("Clase 0", className="binary-level-class"),
                        ],
                        className="binary-level-card binary-left",
                    ),
                    html.Div(
                        [
                            html.Div("Punto de corte", className="binary-threshold-label"),
                            html.Div("58", className="binary-threshold-value"),
                        ],
                        className="binary-threshold-card",
                    ),
                    html.Div(
                        [
                            html.Div("Supera el umbral", className="binary-level-title"),
                            html.Div("59 a 100", className="binary-level-range"),
                            html.Div("Clase 1", className="binary-level-class"),
                        ],
                        className="binary-level-card binary-right",
                    ),
                    html.Div(
                        [
                            html.Div("Resultado del modelo", className="binary-indicator-label"),
                            html.Div("Pendiente", className="binary-indicator-value"),
                        ],
                        className="binary-indicator binary-indicator-center",
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
                className="tab-summary-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                    "gap": "16px",
                    "marginBottom": "12px",
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
                className="tab-usage-card",
                style={
                    "marginBottom": "18px",
                    "padding": "8px 0 10px",
                },
            ),
            html.Div(
                secciones_formulario_renderizadas(config),
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                    "gap": "18px",
                    "marginBottom": "22px",
                },
            ),
            html.Div(
                [boton_prediccion(config["color"])],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "marginBottom": "24px",
                },
            ),
            visual_binario_ingles() if config.get("show_binary_visual") else html.Div(),
            html.Div(
                [
                    html.Div(
                        tarjeta_resultado(
                            config["result_cards"][0]["title"],
                            config["result_cards"][0]["value"],
                            config["result_cards"][0]["detail"],
                            config["color"],
                            grande=True,
                        ),
                        style={"height": "100%"},
                    ),
                    html.Div(
                        tarjeta_resultado(
                            config["result_cards"][1]["title"],
                            config["result_cards"][1]["value"],
                            config["result_cards"][1]["detail"],
                            COLORS["primary"],
                        ),
                        style={"height": "100%"},
                    ),
                    html.Div(
                        tarjeta_resultado(
                            config["result_cards"][2]["title"],
                            config["result_cards"][2]["value"],
                            config["result_cards"][2]["detail"],
                            COLORS["accent"],
                        ),
                        style={"height": "100%"},
                    ),
                    html.Div(
                        tarjeta_resultado(
                            config["result_cards"][3]["title"],
                            config["result_cards"][3]["value"],
                            config["result_cards"][3]["detail"],
                            COLORS["green"],
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


shared_student_fields = [
    ("Municipio", ["Tunja", "Duitama", "Sogamoso", "Chiquinquira", "Otro municipio"], "Seleccione un municipio"),
    ("Zona", ["Urbana", "Rural"], "Seleccione la zona"),
]


shared_home_fields = [
    ("Estrato", ["1", "2", "3", "4", "5", "6"], "Seleccione el estrato"),
    ("Internet en el hogar", ["Si", "No"], "Seleccione una opcion"),
    ("Computador en el hogar", ["Si", "No"], "Seleccione una opcion"),
    ("Personas en el hogar", ["1 a 3", "4 a 5", "6 o mas"], "Seleccione un rango"),
    ("Educacion de la madre", ["Primaria", "Secundaria", "Tecnica", "Universitaria"], "Seleccione una opcion"),
    ("Educacion del padre", ["Primaria", "Secundaria", "Tecnica", "Universitaria"], "Seleccione una opcion"),
]


shared_school_fields = [
    ("Naturaleza", ["Oficial", "No oficial"], "Seleccione una opcion"),
    ("Caracter", ["Academico", "Tecnico", "Normalista"], "Seleccione una opcion"),
    ("Area", ["Urbana", "Rural"], "Seleccione una opcion"),
    ("Jornada", ["Manana", "Tarde", "Noche", "Completa", "Sabatina"], "Seleccione una opcion"),
    ("Sector", ["Publico", "Privado"], "Seleccione una opcion"),
    ("Municipio del colegio", ["Tunja", "Duitama", "Sogamoso", "Chiquinquira", "Otro municipio"], "Seleccione una opcion"),
]


tab_2_school_fields = [
    {
        "label": "Colegio bilingüe",
        "tipo": "radio",
        "className": "toggle-switch-group yes-no-switch",
        "options": [
            {"label": "Sí", "value": 1},
            {"label": "No", "value": 0},
        ],
        "value": 0,
    },
    {
        "label": "Jornada",
        "tipo": "radio",
        "className": "jornada-meter",
        "options": [
            {"label": "Mañana", "value": "Manana"},
            {"label": "Tarde", "value": "Tarde"},
            {"label": "Noche", "value": "Noche"},
            {"label": "Completa", "value": "Completa"},
            {"label": "Sabatina", "value": "Sabatina"},
        ],
        "value": "Manana",
        "inline": True,
    },
    ("Area de ubicacion", ["Urbana", "Rural"], "Seleccione una opcion"),
    ("Naturaleza", ["Oficial", "No oficial"], "Seleccione una opcion"),
    ("Caracter", ["Academico", "Tecnico", "Normalista"], "Seleccione una opcion"),
    ("Municipio de ubicacion", ["Tunja", "Duitama", "Sogamoso", "Chiquinquira", "Otro municipio"], "Seleccione una opcion"),
]


tab_2_home_fields = [
    {
        "label": "Tiene computador",
        "tipo": "radio",
        "className": "toggle-switch-group resource-switch",
        "options": [
            {"label": "On", "value": 1},
            {"label": "Off", "value": 0},
        ],
        "value": 1,
    },
    {
        "label": "Tiene internet",
        "tipo": "radio",
        "className": "toggle-switch-group resource-switch",
        "options": [
            {"label": "On", "value": 1},
            {"label": "Off", "value": 0},
        ],
        "value": 1,
    },
    ("Estrato de vivienda", ["1", "2", "3", "4", "5", "6"], "Seleccione una opcion"),
    ("Educacion de la madre", ["Primaria", "Secundaria", "Tecnica", "Universitaria"], "Seleccione una opcion"),
    ("Educacion del padre", ["Primaria", "Secundaria", "Tecnica", "Universitaria"], "Seleccione una opcion"),
    {
        "label": "Personas en el hogar",
        "tipo": "icon_scale",
        "className": "icon-scale-group people-scale",
        "options": [
            {
                "label": html.Div(
                    [
                        html.Span("👤", className="icon-scale-symbol"),
                        html.Span(str(i), className="icon-scale-value"),
                    ],
                    className="icon-scale-content",
                ),
                "value": i,
            }
            for i in range(1, 11)
        ],
        "value": 4,
        "inline": True,
    },
    {
        "label": "Cuartos del hogar",
        "tipo": "icon_scale",
        "className": "icon-scale-group room-scale",
        "options": [
            {
                "label": html.Div(
                    [
                        html.Span("▣", className="icon-scale-symbol room-symbol"),
                        html.Span(str(i), className="icon-scale-value"),
                    ],
                    className="icon-scale-content",
                ),
                "value": i,
            }
            for i in range(1, 11)
        ],
        "value": 3,
        "inline": True,
    },
]


tab_1 = bloque_pregunta(
    
    {
        "badge": "Pregunta 1",
        "modelo": "Modelo de regresión",
        "tab": "Puntaje Global Esperado",
        "color": COLORS["gold"],
        "question": "¿Cuál es el puntaje global esperado de un estudiante de Boyacá en las pruebas Saber 11 según sus condiciones familiares, socioeconómicas e institucionales, y qué factores permiten identificar estudiantes o colegios con mayor riesgo de bajo desempeño académico?",
        "purpose": "Estimación del puntaje global esperado de un estudiante a partir de sus condiciones familiares, socioeconómicas e institucionales, permitiendo identificar perfiles con posible riesgo de bajo desempeño académico",
        "objective": "Predecir el puntaje global esperado en Saber 11 para estudiantes de Boyacá y analizar qué variables se asocian con mejores o peores resultados.",
        "decision": "Apoya decisiones de focalización de tutorías, refuerzos académicos acompañamiento institucional",
        "output": "Puntaje global estimado, nivel de riesgo académico asociado e interpretación de los factores familiares, socioeconómicos e institucionales que influyen en la predicción.",  
        
        "student_fields": shared_student_fields,
        "home_fields": shared_home_fields,
        "school_fields": shared_school_fields,
        "academic_fields": [
            ("Acceso tecnologico", ["Bajo", "Medio", "Alto"], "Seleccione un nivel"),
            ("Promedio academico previo", ["Bajo", "Medio", "Alto"], "Seleccione un rango"),
            ("Antecedente de lectura", ["Sin dato", "Basico", "Intermedio", "Alto"], "Seleccione una opcion"),
            ("Antecedente de matematicas", ["Sin dato", "Basico", "Intermedio", "Alto"], "Seleccione una opcion"),
        ],
        "result_cards": [
            {
                "title": "Brecha estimada",
                "value": "XX pts",
                "detail": "Diferencia esperada entre Matemáticas y Lectura Crítica para el perfil seleccionado.",
            },
            {
                "title": "Magnitud de la brecha",
                "value": "Media",
                "detail": "Clasificación referencial de la separación esperada entre ambas áreas.",
            },
            {
                "title": "Interpretación",
                "value": "Fortaleza relativa",
                "detail": "El perfil analizado sugiere mayor fortaleza en una de las dos competencias evaluadas.",
            },
            {
                "title": "Factor moderador",
                "value": "Tecnología media",
                "detail": "El acceso tecnológico del hogar se interpreta como modulador del tamaño de la brecha.",
            },
        ],
        "factors": [
            "Acceso a internet y computador en el hogar.",
            "Nivel educativo de madre y padre como capital educativo familiar.",
            "Características del colegio como jornada, área y naturaleza institucional.",
            "Condiciones académicas previas disponibles para el estudiante.",
        ],
        "recommendation": "Usar la predicción para priorizar refuerzos diferenciados en matemáticas "
        "o lectura crítica, ajustar estrategias pedagógicas y focalizar seguimiento en estudiantes "
        "con mayor desequilibrio esperado entre áreas.",
    }
)


tab_2 = bloque_pregunta(
    {
        "badge": "Pregunta 2",
        "modelo": "Modelo de clasificacion",
        "tab": "Competencia en Inglés",
        "color": COLORS["green"],
        "question": "Qué perfil combinado de características familiares e institucionales predice si un estudiante de Boyacá alcanzará un nivel A2 o superior en la prueba de inglés Saber 11, y qué factores"
        " escolares pueden compensar condiciones socioeconómicas desfavorables para lograr este desempeño?",
        "purpose": "Esta pestaña estima la probabilidad de alcanzar el nivel esperado en inglés y "
        "resalta condiciones que pueden compensar desventajas de contexto.",
        "objective": "Clasificar la probabilidad de alcanzar B1 o superior a partir de variables "
        "familiares, institucionales y académicas.",
        "decision": "Apoya decisiones de fortalecimiento curricular, asignación de apoyos en inglés "
        "y focalización de estrategias institucionales.",
        "output": "Probabilidad esperada de alcanzar nivel B1/B+ o superior.",
        "show_binary_visual": True,
        "form_sections": [
            {
                "titulo": "Perfil institucional",
                "campos": tab_2_school_fields[:3],
                "columnas": 1,
            },
            {
                "titulo": "Contexto del colegio",
                "campos": tab_2_school_fields[3:],
                "columnas": 1,
            },
            {
                "titulo": "Recursos del hogar",
                "campos": tab_2_home_fields[:3],
                "columnas": 1,
            },
            {
                "titulo": "Educación familiar",
                "campos": tab_2_home_fields[3:5],
                "columnas": 1,
            },
            {
                "titulo": "Composición del hogar",
                "campos": tab_2_home_fields[5:],
                "columnas": 1,
            },
        ],
        "result_cards": [
            {
                "title": "Probabilidad de superar 58",
                "value": "XX %",
                "detail": "Estimación de la probabilidad de quedar en la clase mayor a 58 en la prueba de inglés.",
            },
            {
                "title": "Clasificación esperada",
                "value": "<=58 / >58",
                "detail": "Resultado binario de referencia según el punto de corte definido para el modelo.",
            },
            {
                "title": "Factores favorables",
                "value": "Jornada + acceso",
                "detail": "Resumen breve de variables escolares y tecnológicas que empujan la predicción al alza.",
            },
            {
                "title": "Factores de riesgo",
                "value": "Contexto vulnerable",
                "detail": "Variables de contexto que reducen la probabilidad esperada de competencia en inglés.",
            },
        ],
        "factors": [
            "Acceso tecnológico y exposición a recursos digitales en el hogar.",
            "Condiciones institucionales como jornada, área y naturaleza del colegio.",
            "Capital educativo familiar asociado al acompañamiento del proceso formativo.",
            "Variables académicas previas con relación esperada al aprendizaje de idiomas.",
        ],
        "recommendation": "Usar la clasificación para priorizar estudiantes e instituciones que "
        "requieren refuerzo en inglés, acompañamiento intensivo o ajustes en la oferta de apoyo "
        "escolar y digital.",
    }
)


tab_3 = bloque_pregunta(
    {
        "badge": "Pregunta 1",
        "modelo": "Modelo de regresión",
        "tab": "Predicción Puntaje Global",
        "color": COLORS["blue"],
        "question": "¿Cuál es el puntaje global esperado de un estudiante de Boyacá en las pruebas Saber 11 según sus condiciones familiares, socioeconómicas e institucionales, y qué factores permiten identificar estudiantes o colegios con mayor riesgo de bajo desempeño académico?",
        "purpose": "Esta pestaña estima la diferencia esperada entre dos áreas clave y ayuda a "
        "identificar perfiles con fortalezas o rezagos relativos.",
        "objective": "Estimar la magnitud y dirección esperada de la brecha Matemáticas - Lectura "
        "Crítica para un perfil estudiantil e institucional dado.",
        "decision": "Apoya decisiones de refuerzo focalizado por área, acompañamiento académico y "
        "seguimiento institucional por perfiles de riesgo.",
        "output": "Brecha esperada entre puntaje de Matemáticas y Lectura Crítica.",
        
        
        "student_fields": shared_student_fields,
        "home_fields": shared_home_fields,
        "school_fields": shared_school_fields,
        "academic_fields": [
            ("Puntaje global previo o estimado", ["Sin dato", "Bajo", "Medio", "Alto"], "Seleccione una opcion"),
            ("Nivel de desempeno integral", ["Basico", "Intermedio", "Alto"], "Seleccione una opcion"),
            ("Participacion en apoyos", ["No registra", "Si"], "Seleccione una opcion"),
            ("Capital educativo familiar", ["Bajo", "Medio", "Alto"], "Seleccione una opcion"),
        ],
        "result_cards": [
            {
                "title": "Probabilidad de superar el percentil 75",
                "value": "XX %",
                "detail": "Estimación del potencial de alto desempeño para el perfil seleccionado.",
            },
            {
                "title": "Clasificación esperada",
                "value": "Alto potencial",
                "detail": "Lectura rápida para priorizar seguimiento o fortalecimiento del caso.",
            },
            {
                "title": "Factores de resiliencia",
                "value": "Institución protectora",
                "detail": "Características institucionales que incrementan la probabilidad de alto desempeño.",
            },
            {
                "title": "Mensaje para decisión",
                "value": "Priorizar apoyos",
                "detail": "Sugerencia operativa de becas, tutorías o seguimiento según el perfil predicho.",
            },
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


app.layout = html.Div(
    [
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
        html.Div(
            [
                html.Div(
                    tarjeta_kpi(
                        "Modelos desplegados",
                        "3",
                        "1 regresión y 2 clasificaciones activas en el tablero.",
                        COLORS["blue"],
                        "M",
                    ),
                    style={"flex": "1"},
                ),
                html.Div(
                    tarjeta_kpi(
                        "Tipos de salida",
                        "2",
                        "Predicción numérica y clasificación binaria para lectura rápida.",
                        COLORS["green"],
                        "S",
                    ),
                    style={"flex": "1"},
                ),
                html.Div(
                    tarjeta_kpi(
                        "Decisiones apoyadas",
                        "3",
                        "Focalización, acompañamiento y priorización de intervenciones.",
                        COLORS["gold"],
                        "D",
                    ),
                    style={"flex": "1"},
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                "gap": "16px",
                "marginBottom": "28px",
            },
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Puntaje Global Esperado",
                    children=[tab_1],
                    style=TAB_STYLE,
                    selected_style=TAB_SELECTED_STYLE,
                ),
                dcc.Tab(
                    label="Competencia en Inglés",
                    children=[tab_2],
                    style=TAB_STYLE,
                    selected_style=TAB_SELECTED_STYLE,
                ),
                dcc.Tab(
                    label="Resiliencia Académica",
                    children=[tab_3],
                    style=TAB_STYLE,
                    selected_style=TAB_SELECTED_STYLE,
                ),
            ],
            style={
                "backgroundColor": "transparent",
                "border": "none",
                "marginTop": "8px",
            },
        ),
    ],
    style={
        "backgroundColor": COLORS["background"],
        "minHeight": "100vh",
        "padding": "32px",
        "fontFamily": '"Segoe UI", sans-serif',
    },
)


if __name__ == "__main__":
    app.run(debug=True, port=8050)
