import reflex as rx
from visualisation_analyse_flux.states.flow_state import FlowState


def confidence_badge(confidence: int) -> rx.Component:
    return rx.cond(
        confidence >= 95,
        rx.el.span(
            f"{confidence}%",
            class_name="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700 border border-green-200 w-fit",
        ),
        rx.cond(
            confidence >= 80,
            rx.el.span(
                f"{confidence}%",
                class_name="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200 w-fit",
            ),
            rx.el.span(
                "Création",
                class_name="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 border border-red-200 w-fit",
            ),
        ),
    )


def table_header(label: str, column: str) -> rx.Component:
    return rx.el.th(
        rx.el.div(
            rx.el.span(label, class_name="mr-2 font-bold"),
            rx.cond(
                FlowState.sort_column == column,
                rx.cond(
                    FlowState.sort_ascending,
                    rx.icon("chevron-up", class_name="h-4 w-4 text-blue-600"),
                    rx.icon("chevron-down", class_name="h-4 w-4 text-blue-600"),
                ),
                rx.icon("chevrons-up-down", class_name="h-4 w-4 text-gray-300"),
            ),
            class_name="flex items-center cursor-pointer hover:text-blue-600 transition-colors",
            on_click=lambda: FlowState.toggle_sort(column),
        ),
        class_name="px-4 py-3 text-left text-xs uppercase tracking-wider bg-gray-100 border-b border-gray-200 text-gray-600",
    )


def table_row(entry: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.cond(
                    entry["status"] == "Nouvelle variable",
                    rx.icon(
                        "circle-alert", class_name="h-4 w-4 text-red-500 mr-2 shrink-0"
                    ),
                    None,
                ),
                rx.el.span(entry["data_id"]),
                class_name=rx.cond(
                    entry["status"] == "Nouvelle variable",
                    "flex items-center font-bold text-red-600",
                    "flex items-center font-semibold text-gray-900",
                ),
            ),
            class_name="px-4 py-3 max-w-[250px] truncate",
        ),
        rx.el.td(
            entry["data_ref"],
            class_name="px-4 py-3 text-gray-600 max-w-[200px] truncate",
        ),
        rx.el.td(
            confidence_badge(entry["confidence"].to(int)),
            class_name="px-4 py-3 whitespace-nowrap",
        ),
        rx.el.td(
            entry["status"], class_name="px-4 py-3 text-gray-500 whitespace-nowrap"
        ),
        rx.el.td(
            entry["raison"], class_name="px-4 py-3 text-gray-500 max-w-xs truncate"
        ),
        on_click=lambda: FlowState.select_row(entry["original_idx"]),
        class_name=rx.cond(
            FlowState.selected_row_idx == entry["original_idx"],
            "bg-blue-50/50 border-l-4 border-blue-500 cursor-pointer transition-all",
            "hover:bg-gray-50 cursor-pointer transition-all even:bg-[#f9f9f9] border-l-4 border-transparent",
        ),
    )


def details_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                FlowState.selected_row_idx >= 0,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h2(
                                    FlowState.selected_row_data["data_id"],
                                    class_name="text-xl font-bold text-gray-900 mb-1",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "arrow-right",
                                        class_name="h-4 w-4 text-gray-400",
                                    ),
                                    rx.el.span(
                                        FlowState.selected_row_data["data_ref"],
                                        class_name="text-md font-medium text-blue-600 truncate",
                                    ),
                                    class_name="flex items-center gap-2",
                                ),
                                class_name="flex-1",
                            ),
                            rx.el.div(
                                confidence_badge(
                                    FlowState.selected_row_data["confidence"].to(int)
                                ),
                                class_name="shrink-0",
                            ),
                            class_name="flex justify-between items-start gap-4 mb-6 pb-6 border-b border-gray-100",
                        ),
                        rx.el.div(
                            rx.el.h4(
                                "Analyse du rapprochement",
                                class_name="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    rx.cond(
                                        FlowState.selected_row_data["raison"] != "",
                                        FlowState.selected_row_data["raison"],
                                        rx.el.span(
                                            "Aucune raison spécifiée.",
                                            class_name="italic text-gray-400",
                                        ),
                                    ),
                                    class_name="text-sm text-gray-600 leading-relaxed",
                                ),
                                class_name="bg-gray-50 p-5 rounded-xl border border-gray-100",
                            ),
                        ),
                        class_name="p-6 bg-white border border-gray-200 rounded-2xl shadow-sm",
                    ),
                    class_name="mb-8 animate-in fade-in slide-in-from-top-2 duration-300",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "mouse-pointer-click",
                            class_name="h-10 w-10 text-gray-300 mb-4",
                        ),
                        rx.el.h4(
                            "Variable non sélectionnée",
                            class_name="text-sm font-bold text-gray-900 mb-1",
                        ),
                        rx.el.p(
                            "Utilisez le diagramme Sankey ou le tableau ci-dessous pour explorer les correspondances.",
                            class_name="text-sm text-gray-500 max-w-[240px]",
                        ),
                        class_name="flex flex-col items-center justify-center text-center",
                    ),
                    class_name="p-12 border-2 border-dashed border-gray-200 rounded-2xl mb-8 bg-gray-50/30",
                ),
            )
        ),
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400",
                ),
                rx.el.input(
                    placeholder="Rechercher une variable...",
                    on_change=FlowState.set_search_query.debounce(500),
                    class_name="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white",
                ),
                class_name="relative mb-6",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            table_header("Variable Source", "data_id"),
                            table_header("Référentiel", "data_ref"),
                            table_header("Confiance", "confidence"),
                            table_header("Statut", "status"),
                            table_header("Raison", "raison"),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(FlowState.filtered_data, table_row),
                        class_name="divide-y divide-gray-100",
                    ),
                    class_name="w-full table-auto border-collapse font-['Roboto'] text-[14px]",
                ),
                class_name="overflow-x-auto rounded-xl border border-gray-200 bg-white",
            ),
            class_name="flex flex-col",
        ),
        class_name="bg-white p-6 md:p-8 rounded-2xl border border-gray-100 shadow-sm h-full",
    )