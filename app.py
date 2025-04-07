from shiny import App, render, ui, reactive
import pandas as pd
from datetime import datetime
from db import insertar_reporte  # Importar la función para guardar en la base de datos

# Cargar datos desde archivos CSV
df_tiendas = pd.read_csv("data/tiendas.csv")
df_cajas = pd.read_csv("data/cajas.csv")
clases_gasto = pd.read_csv("data/clases_gasto.csv")["clase"].tolist()
otros_medios_pago = pd.read_csv("data/otros_medios_pago.csv")["medio"].tolist()

claves_correctas = dict(zip(df_tiendas["tienda"], df_tiendas["clave"].astype(str)))
caja_ids = df_cajas["id"].tolist()

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.column(12,
            ui.input_select("tienda", "Tienda", {tienda: tienda for tienda in df_tiendas["tienda"]}),
            ui.input_select("clave_tienda", "", {
                "Clave de la tienda": "Clave de la tienda",
                **{clave: clave for clave in df_tiendas["clave"].astype(str)}
            }),
            ui.output_ui("validacion_tienda"),

            ui.accordion(
                ui.accordion_panel("Gastos", 
                    *[item for i in range(1, 8) for item in (
                        ui.input_numeric(f"valor_Gasto{i}", f"Gasto {i}", value=0),
                        ui.input_select(f"clase_de_gasto{i}", "", {
                            "seleccionar_gasto": "Clase de Gasto",
                            **{g: g for g in clases_gasto}
                        }),
                        ui.input_text(f"descripcion_Gasto{i}", "", placeholder=f"Descripción del gasto {i}")
                    )]
                ),
                ui.accordion_panel("Otros medios de pagos",
                    *[item for i in range(1, 8) for item in (
                        ui.input_numeric(f"valor_otros_medios_pagos{i}", f"Medio de pago {i}", value=0),
                        ui.input_select(f"otro_pago{i}", "", {
                            "seleccionar_medio_de_pago": "medio de pago",
                            **{m: m for m in otros_medios_pago}
                        }),
                        ui.input_text(f"descripcion_otro_pago{i}", "", placeholder=f"Descripción del otro pago {i}")
                    )]
                ),
                ui.accordion_panel("Efectivo y Datáfono",
                    ui.input_numeric("efectivo", "Efectivo", value=0),
                    ui.input_numeric("datafono", "Datáfono", value=0)
                ),
                ui.accordion_panel("Cajas",
                    *[
                        ui.input_numeric(f"caja{row.id}", row.nombre, value=0)
                        for row in df_cajas.itertuples(index=False)
                    ]
                ),
                open=False,
                multiple=False
            )
        ),
        ui.column(12,
            ui.panel_well(
                ui.h1("Reporte de Cierre"),
                ui.output_text("fecha_resumen"),
                ui.output_text("tienda_seleccionada"),
                ui.hr(),
                ui.p(ui.output_ui("total_gastos")),
                ui.p(ui.output_ui("total_otros_pagos")),
                ui.p(ui.output_ui("total_efectivo")),
                ui.p(ui.output_ui("total_datafono")),
                ui.hr(),
                ui.p(ui.strong(ui.output_ui("total_gastos_pagos"))),
                ui.p(ui.strong(ui.output_ui("total_cajas"))),
                ui.p(ui.strong(ui.output_ui("sobrante"))),
                ui.hr(),
                ui.p(ui.strong(ui.output_ui("ventas_dia"))),
                ui.input_action_button("guardar", "Guardar cierre", class_="btn-primary"),
                ui.output_text("mensaje_guardado")
            )
        )
    )
)

def safe(input_value):
    return input_value if input_value is not None else 0

def server(input, output, session):
    @render.text
    def fecha_resumen():
        import locale
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'es_CO.utf8')
            except:
                locale.setlocale(locale.LC_TIME, '')

        fecha_hoy = datetime.today()
        return fecha_hoy.strftime('%A %d de %B del %Y').capitalize()

    @render.text
    def tienda_seleccionada():
        return f"{input.tienda()}" if input.tienda() else ""

    @render.ui
    def validacion_tienda():
        tienda = input.tienda()
        clave = input.clave_tienda()
        if tienda in claves_correctas and clave != "Clave de la tienda":
            if claves_correctas[tienda] != clave:
                return ui.HTML("<span style='color: red; font-weight: bold;'>⚠️ Tienda y clave no coinciden</span>")
        return ui.HTML("")

    @render.ui
    def total_gastos():
        tienda = input.tienda()
        clave = input.clave_tienda()
        if tienda in claves_correctas and clave != claves_correctas[tienda]:
            return ui.HTML("")
        total = sum(safe(input[f"valor_Gasto{i}"]()) for i in range(1, 8))
        return ui.HTML(f"Gastos: ${total:,.0f}")

    @render.ui
    def total_otros_pagos():
        tienda = input.tienda()
        clave = input.clave_tienda()
        if tienda in claves_correctas and clave != claves_correctas[tienda]:
            return ui.HTML("")
        total = sum(safe(input[f"valor_otros_medios_pagos{i}"]()) for i in range(1, 8))
        return ui.HTML(f"Otros medios de pago: ${total:,.0f}")

    @render.ui
    def total_efectivo():
        tienda = input.tienda()
        clave = input.clave_tienda()
        if tienda in claves_correctas and clave != claves_correctas[tienda]:
            return ui.HTML("")
        efectivo = safe(input.efectivo())
        return ui.HTML(f"Efectivo: ${efectivo:,.0f}")

    @render.ui
    def total_datafono():
        tienda = input.tienda()
        clave = input.clave_tienda()
        if tienda in claves_correctas and clave != claves_correctas[tienda]:
            return ui.HTML("")
        datafono = safe(input.datafono())
        return ui.HTML(f"Datáfono: ${datafono:,.0f}")

    @render.ui
    def total_cajas():
        total = sum(safe(input[f"caja{id}"]()) for id in caja_ids)
        return ui.HTML(f"Total Cajas: ${total:,.0f}")

    @render.ui
    def ventas_dia():
        total = sum(
            safe(input[f"caja{row.id}"]())
            for row in df_cajas.itertuples(index=False)
            if "abonos" not in row.nombre.lower()
        )
        return ui.HTML(f"<strong>Ventas del día:</strong> ${total:,.0f}")

    @render.ui
    def total_gastos_pagos():
        tienda = input.tienda()
        clave = input.clave_tienda()
        if tienda in claves_correctas and clave != claves_correctas[tienda]:
            return ui.HTML("")
        total_gastos = sum(safe(input[f"valor_Gasto{i}"]()) for i in range(1, 8))
        total_otros = sum(safe(input[f"valor_otros_medios_pagos{i}"]()) for i in range(1, 8))
        efectivo = safe(input.efectivo())
        datafono = safe(input.datafono())
        total = total_gastos + total_otros + efectivo + datafono
        return ui.HTML(f"Total Pagos y Gastos: ${total:,.0f}")

    @render.ui
    def sobrante():
        tienda = input.tienda()
        clave = input.clave_tienda()
        if tienda in claves_correctas and clave != claves_correctas[tienda]:
            return ui.HTML("")
        total_gastos = sum(safe(input[f"valor_Gasto{i}"]()) for i in range(1, 8))
        total_otros = sum(safe(input[f"valor_otros_medios_pagos{i}"]()) for i in range(1, 8))
        efectivo = safe(input.efectivo())
        datafono = safe(input.datafono())
        total_pagos = total_gastos + total_otros + efectivo + datafono
        total_cajas_valor = sum(safe(input[f"caja{id}"]()) for id in caja_ids)
        diferencia = total_cajas_valor - total_pagos
        etiqueta = "Faltante" if diferencia >= 0 else "Sobrante"
        color = "black" if diferencia == 0 else "red"
        return ui.HTML(f"<span style='color: {color}; font-weight: bold;'>{etiqueta}: ${abs(diferencia):,.0f}</span>")

    def recolectar_datos():
        return {
            "tienda": input.tienda(),
            "clave": input.clave_tienda(),
            "efectivo": safe(input.efectivo()),
            "datafono": safe(input.datafono()),
            "gastos": [
                {
                    "valor": safe(input[f"valor_Gasto{i}"]()),
                    "clase": input[f"clase_de_gasto{i}"](),
                    "descripcion": input[f"descripcion_Gasto{i}"]()
                }
                for i in range(1, 8)
                if safe(input[f"valor_Gasto{i}"]()) > 0
            ],
            "otros_pagos": [
                {
                    "valor": safe(input[f"valor_otros_medios_pagos{i}"]()),
                    "medio": input[f"otro_pago{i}"](),
                    "descripcion": input[f"descripcion_otro_pago{i}"]()
                }
                for i in range(1, 8)
                if safe(input[f"valor_otros_medios_pagos{i}"]()) > 0
            ],
            "cajas": [
                {
                    "id": row.id,
                    "valor": safe(input[f"caja{row.id}"]())
                }
                for row in df_cajas.itertuples(index=False)
                if safe(input[f"caja{row.id}"]()) > 0
            ]
        }

    @render.text
    def mensaje_guardado():
        return ""

    @reactive.event(input.guardar)
    def guardar_en_db():
        tienda = input.tienda()
        clave = input.clave_tienda()

        if tienda not in claves_correctas or claves_correctas[tienda] != clave:
            output.mensaje_guardado.set("❌ Tienda y clave no coinciden. No se guardó.")
            return

        data = recolectar_datos()
        insertar_reporte(data)
        output.mensaje_guardado.set("✅ Datos guardados exitosamente.")

app = App(app_ui, server)
