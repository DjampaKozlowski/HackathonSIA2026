import reflex as rx
from visualisation_analyse_flux.states.flow_state import FlowState
from visualisation_analyse_flux.components.flow_chart import flow_chart
from visualisation_analyse_flux.components.details_panel import details_panel


def stat_card(label: str, value: str, icon_name: str, color_class: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon_name, class_name=f"h-5 w-5 {color_class}"),
            class_name=f"p-2 rounded-lg bg-opacity-10 mb-3 w-fit {color_class.replace('text-', 'bg-')}",
        ),
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-gray-500 mb-1"),
            rx.el.h3(value, class_name="text-2xl font-bold text-gray-900"),
        ),
        class_name="bg-white p-5 rounded-xl border border-gray-100 shadow-sm flex flex-col",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.nav(
            rx.el.div(
                rx.el.div(
                    rx.icon("git-branch", class_name="h-6 w-6 text-blue-600"),
                    rx.el.span(
                        "DataFlux Manager",
                        class_name="text-xl font-bold text-gray-900 tracking-tight",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.el.button(
                        "Exporter PDF",
                        class_name="px-4 py-2 bg-gray-900 text-white text-sm font-semibold rounded-lg hover:bg-gray-800 transition-colors",
                    ),
                    class_name="hidden sm:block",
                ),
                class_name="max-w-7xl mx-auto flex justify-between items-center",
            ),
            class_name="bg-white/80 backdrop-blur-md border-b border-gray-100 py-4 px-6 sticky top-0 z-10",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Rapprochement de Variables",
                        class_name="text-3xl font-extrabold text-gray-900 sm:text-4xl tracking-tight mb-2",
                    ),
                    rx.el.p(
                        "Visualisez le mapping entre les variables sources et le référentiel cible.",
                        class_name="text-lg text-gray-500 font-medium",
                    ),
                    class_name="mb-8",
                ),
                rx.el.div(
                    stat_card(
                        "Variables totales",
                        FlowState.total_variables.to_string(),
                        "layers",
                        "text-blue-600",
                    ),
                    stat_card(
                        "Rapprochées",
                        FlowState.matched_count.to_string(),
                        "circle_check",
                        "text-green-600",
                    ),
                    stat_card(
                        "Nouvelles variables",
                        FlowState.new_variables_count.to_string(),
                        "circle_plus",
                        "text-red-500",
                    ),
                    stat_card(
                        "Confiance moyenne",
                        f"{FlowState.avg_confidence.to(int)}%",
                        "percent",
                        "text-amber-500",
                    ),
                    class_name="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "Flux de Rapprochement",
                            class_name="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4",
                        ),
                        flow_chart(),
                        class_name="sticky top-24",
                    ),
                    class_name="lg:col-span-2",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "Détails des Variables",
                            class_name="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4",
                        ),
                        details_panel(),
                    ),
                    class_name="lg:col-span-3",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-5 gap-8",
            ),
            class_name="max-w-7xl mx-auto px-6 py-10",
        ),
        class_name="min-h-screen bg-[#fcfcfd] font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Roboto:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/", on_load=FlowState.load_data)