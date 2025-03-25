from shiny import App, render, ui, reactive

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.column(12,
            ui.input_date("fecha", "Fecha"),  
            ui.input_select("tienda", "", {
                "seleccionar_tienda":  "Tienda",
                "Mayorca": "Mayorca", 
                "La Central": "La Central", 
                "San Diego": "San Diego",
                "Molinos": "Molinos",
                "Puerta del Norte": "Puerta del Norte",
                "Oficina": "Oficina"
            }),

            ui.accordion(
                ui.accordion_panel("Gastos", 
                    *[item for i in range(1, 8) for item in (
                        ui.input_numeric(f"valor_Gasto{i}", f"Gasto {i}", value=0),
                        ui.input_select(f"clase_de_gasto{i}", "", {
                            "seleccionar_gasto": "Clase de Gasto",
                            "Aseo": "Aseo",
                            "Comida": "Comida",
                            "Dominical y Festivo": "Dominical y Festivo",
                            "Horas Extras": "Horas Extras",
                            "Papelería": "Papelería",
                            "Servicios públicos e Impuestos": "Servicios públicos e Impuestos",
                            "Transporte": "Transporte",
                            "Repuestos": "Repuestos",
                            "Otros Gastos": "Otros Gastos"
                        }),
                        ui.input_text(f"descripcion_Gasto{i}", "", placeholder=f"Descripción del gasto {i}")
                    )]
                ),
                ui.accordion_panel("Otros Pagos",
                    *[item for i in range(1, 8) for item in (
                        ui.input_numeric(f"valor_Otros_Pagos{i}", f"Medio de pago {i}", value=0),
                        ui.input_select(f"otro_pago{i}", "", {
                            "seleccionar_medio_de_pago": "medio de pago",
                            "Tansferencia o consignación Bancolombia Ahorros": "Tansferencia o consignación Bancolombia Ahorros",
                            "Tansferencia o consignación Bancolombia Corriente": "Tansferencia o consignación Bancolombia Corriente",
                            "Tansferencia o consignación Davivienda Corriente": "Tansferencia o consignación Davivienda Corriente",
                            "Rappi": "Rappi",
                            "Mercado Libre": "Mercado Libre",
                            "Sistecrédito": "Sistecrédito",
                            "Tienda Online": "Tienda Online",
                            "Otra forma de pago": "Otra forma de pago"
                        }),
                        ui.input_text(f"descripcion_otro_pago{i}", "", placeholder=f"Descripción del otro pago {i}")
                    )]
                ),
                ui.accordion_panel("Medios de Pago",
                    ui.input_numeric("efectivo", "Efectivo", value=0),
                    ui.input_numeric("datafono", "Datáfono", value=0)
                ),
                ui.accordion_panel("Cajas",
                    ui.input_numeric("caja1", "Caja 1: Siigo POS", value=0),
                    ui.input_numeric("caja2", "Caja 2: Reparaciones", value=0),
                    ui.input_numeric("caja3", "Caja 3: Megared", value=0),
                    ui.input_numeric("caja4", "Caja 4: Abonos Sistecrédito", value=0),
                    ui.input_numeric("caja5", "Caja 5: Facturas Electrónicas", value=0)
                ),
                open=False
            )
        ),
        ui.column(12,
            ui.panel_well(
                ui.h3("Totales"),
                ui.p(ui.strong("Fecha:"), ui.output_text("fecha_resumen")),
                ui.p(ui.strong("Tienda:"), ui.output_text("tienda_seleccionada")),
                ui.hr(),
                ui.p(ui.output_ui("total_gastos")),
                ui.p(ui.output_ui("total_otros_pagos")),
                ui.p(ui.output_ui("total_efectivo")),
                ui.p(ui.output_ui("total_datafono")),
                ui.p(ui.strong(ui.output_ui("total_gastos_pagos"))),
                ui.hr(),
                ui.p(ui.strong(ui.output_ui("total_cajas"))),
                ui.hr(),
                ui.p(ui.strong(ui.output_ui("sobrante")))
            )
        )
    )
)

def server(input, output, session):
    @render.text
    def fecha_resumen():
        return f"{input.fecha()}"

    @render.text
    def tienda_seleccionada():
        return f"{input.tienda()}"

    @render.ui
    def total_gastos():
        total = sum(input[f"valor_Gasto{i}"]() for i in range(1, 8))
        return ui.HTML(f"Gastos: ${total:,.0f}")

    @render.ui
    def total_otros_pagos():
        total = sum(input[f"valor_Otros_Pagos{i}"]() for i in range(1, 8))
        return ui.HTML(f"Otros medios de pago: ${total:,.0f}")

    @render.ui
    def total_efectivo():
        efectivo = input.efectivo()
        return ui.HTML(f"Efectivo: ${efectivo:,.0f}")

    @render.ui
    def total_datafono():
        datafono = input.datafono()
        return ui.HTML(f"Datáfono: ${datafono:,.0f}")

    @render.ui
    def total_cajas():
        total = sum(input[f"caja{i}"]() for i in range(1, 6))
        return ui.HTML(f"Total Cajas: ${total:,.0f}")

    @render.ui
    def total_gastos_pagos():
        total_gastos = sum(input[f"valor_Gasto{i}"]() for i in range(1, 8))
        total_otros = sum(input[f"valor_Otros_Pagos{i}"]() for i in range(1, 8))
        efectivo = input.efectivo()
        datafono = input.datafono()
        total = total_gastos + total_otros + efectivo + datafono
        return ui.HTML(f"Total Pagos y Gastos: ${total:,.0f}")

    @render.ui
    def sobrante():
        total_gastos = sum(input[f"valor_Gasto{i}"]() for i in range(1, 8))
        total_otros = sum(input[f"valor_Otros_Pagos{i}"]() for i in range(1, 8))
        efectivo = input.efectivo()
        datafono = input.datafono()
        total_pagos = total_gastos + total_otros + efectivo + datafono
        total_cajas = sum(input[f"caja{i}"]() for i in range(1, 6))
        sobrante = total_cajas - total_pagos
        return ui.HTML(f"Sobrante: ${sobrante:,.0f}")

app = App(app_ui, server)
