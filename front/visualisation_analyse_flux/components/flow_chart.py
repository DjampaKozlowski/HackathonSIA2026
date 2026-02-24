import reflex as rx
from visualisation_analyse_flux.states.flow_state import FlowState


def flow_chart() -> rx.Component:
    return rx.el.div(
        rx.plotly(
            data=FlowState.sankey_figure,
            on_click=FlowState.handle_sankey_click,
            height="450px",
            class_name="w-full",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm overflow-hidden",
    )